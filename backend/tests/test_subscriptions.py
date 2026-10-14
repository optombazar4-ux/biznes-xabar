import unittest
from datetime import timedelta
from unittest.mock import patch

from fastapi import HTTPException
from starlette.requests import Request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models import Subscription
from app.rate_limit import enforce_rate_limit
from app.utils import utcnow_naive
from app.routers.news import (
    confirm_subscription,
    subscribe_newsletter,
    unsubscribe_newsletter,
)
from app.schemas import SubscribeIn


class SubscriptionFlowTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.db = self.Session()
        self.request = Request({"type": "http", "client": ("203.0.113.10", 1234)})

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    @patch("app.routers.news.send_subscription_confirmation_email", return_value=True)
    def test_subscription_requires_email_confirmation(self, send_confirmation):
        result = subscribe_newsletter(
            SubscribeIn(email="user@example.com"), self.request, self.db
        )

        self.assertTrue(result["ok"])
        subscription = self.db.query(Subscription).one()
        self.assertFalse(subscription.is_active)
        self.assertIsNotNone(subscription.confirmation_token)
        self.assertIsNotNone(subscription.confirmation_expires_at)
        self.assertIsNotNone(subscription.unsubscribe_token)
        confirmation_url = send_confirmation.call_args.args[1]
        self.assertIn(subscription.confirmation_token, confirmation_url)

        response = confirm_subscription(subscription.confirmation_token, self.db)
        self.assertEqual(response.status_code, 200)
        self.db.refresh(subscription)
        self.assertTrue(subscription.is_active)
        self.assertIsNone(subscription.confirmation_token)
        self.assertIsNone(subscription.confirmation_expires_at)
        self.assertIsNotNone(subscription.confirmed_at)

        response = unsubscribe_newsletter(subscription.unsubscribe_token, self.db)
        self.assertEqual(response.status_code, 200)
        self.db.refresh(subscription)
        self.assertFalse(subscription.is_active)

    @patch("app.routers.news.send_subscription_confirmation_email", return_value=True)
    def test_existing_subscriber_receives_the_same_response(self, _send_confirmation):
        existing = Subscription(email="member@example.com", is_active=True)
        self.db.add(existing)
        self.db.commit()

        result = subscribe_newsletter(
            SubscribeIn(email="member@example.com"), self.request, self.db
        )

        self.assertTrue(result["ok"])
        self.assertNotIn("allaqachon", result["xabar"])

    def test_expired_confirmation_token_is_rejected(self):
        subscription = Subscription(
            email="expired@example.com",
            is_active=False,
            confirmation_token="x" * 40,
            confirmation_expires_at=utcnow_naive() - timedelta(minutes=1),
        )
        self.db.add(subscription)
        self.db.commit()

        response = confirm_subscription(subscription.confirmation_token, self.db)

        self.assertEqual(response.status_code, 410)
        self.db.refresh(subscription)
        self.assertFalse(subscription.is_active)
        self.assertIsNone(subscription.confirmation_token)

    def test_database_rate_limit_is_shared_by_sessions(self):
        enforce_rate_limit(self.request, "shared-test", limit=1, window_seconds=60, db=self.db)
        second_session = self.Session()
        try:
            with self.assertRaises(HTTPException) as raised:
                enforce_rate_limit(
                    self.request,
                    "shared-test",
                    limit=1,
                    window_seconds=60,
                    db=second_session,
                )
            self.assertEqual(raised.exception.status_code, 429)
        finally:
            second_session.close()


if __name__ == "__main__":
    unittest.main()
