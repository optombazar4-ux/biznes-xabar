import unittest

from app.services.monitoring import sanitize_error


class MonitoringSecurityTests(unittest.TestCase):
    def test_redacts_telegram_token_from_error(self):
        value = sanitize_error(
            "POST https://api.telegram.org/bot123456:very-secret/sendMessage failed"
        )
        self.assertNotIn("very-secret", value)
        self.assertIn("bot[REDACTED]/sendMessage", value)

    def test_redacts_password_from_database_url(self):
        value = sanitize_error(
            "postgres failed via postgresql://db-user:secret-password@example.com/db"
        )
        self.assertNotIn("secret-password", value)
        self.assertIn("[REDACTED]@example.com", value)


if __name__ == "__main__":
    unittest.main()
