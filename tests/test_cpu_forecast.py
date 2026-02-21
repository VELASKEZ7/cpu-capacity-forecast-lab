import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from cpu_forecast import build_forecast, fit_linear_regression  # noqa: E402


class CpuForecastTests(unittest.TestCase):
    def test_fit_linear_regression(self):
        slope, intercept = fit_linear_regression([10, 20, 30, 40])
        self.assertGreater(slope, 0)
        self.assertGreaterEqual(intercept, 0)

    def test_build_forecast_horizon(self):
        values = [40 + (i * 0.7) for i in range(60)]
        report = build_forecast(values, 12)
        self.assertEqual(len(report["forecast"]), 12)
        self.assertIn(report["recommendation"], {"scale-up", "maintain"})


if __name__ == "__main__":
    unittest.main()
