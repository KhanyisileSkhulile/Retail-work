"""M15-06 performance tests for Retail-X-AI services."""

import statistics
import sys
import unittest
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "application" / "backend"))

from database import service as db_service
from application.backend.forecasts import service as forecast_service
from recommendations import service as restocking_service


class PerformanceTests(unittest.TestCase):

    RUNS = 5

    def measure(self, name, function, validate):
        timings = []

        for _ in range(self.RUNS):
            start = perf_counter()
            result = function()
            elapsed_ms = (perf_counter() - start) * 1000

            validate(result)
            timings.append(elapsed_ms)

        average = statistics.mean(timings)
        minimum = min(timings)
        maximum = max(timings)

        print(f"\n{name}")
        print(f"Runs: {self.RUNS}")
        print(f"Average: {average:.2f} ms")
        print(f"Minimum: {minimum:.2f} ms")
        print(f"Maximum: {maximum:.2f} ms")

        self.assertGreater(average, 0)
        return average

    def test_forecast_loading_performance(self):
        self.measure(
            "Forecast CSV loading",
            forecast_service.load_forecasts,
            lambda result: self.assertGreater(len(result), 0),
        )

    def test_database_summary_performance(self):
        self.measure(
            "Database summary retrieval",
            db_service.get_inventory_summary,
            lambda result: self.assertGreater(result["records"], 0),
        )

    def test_complete_restocking_performance(self):
        def validate(result):
            self.assertTrue(result["success"])
            self.assertGreater(result["record_count"], 0)

        self.measure(
            "Complete restocking workflow",
            restocking_service.get_restocking_recommendations,
            validate,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
