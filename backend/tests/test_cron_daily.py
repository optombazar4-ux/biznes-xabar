import unittest
from unittest.mock import patch

from app import cron_daily


class DailyCronTests(unittest.TestCase):
    def test_main_runs_pipeline_and_logs_saved_count(self):
        with (
            patch.object(cron_daily, "run_pipeline", return_value=2) as run_mock,
            patch.object(cron_daily.logging, "info") as log_mock,
        ):
            cron_daily.main()

        run_mock.assert_called_once_with()
        log_mock.assert_any_call(
            "✅ Muvaffaqiyatli %s ta yangi biznes darsi yaratildi va "
            "indeksatsiyaga yuborildi!",
            2,
        )


if __name__ == "__main__":
    unittest.main()
