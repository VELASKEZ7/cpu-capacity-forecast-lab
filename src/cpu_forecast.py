import argparse
import csv
import json
from pathlib import Path


def fit_linear_regression(values):
    n = len(values)
    x_values = list(range(n))
    mean_x = sum(x_values) / n
    mean_y = sum(values) / n
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, values))
    denominator = sum((x - mean_x) ** 2 for x in x_values)
    slope = numerator / denominator if denominator else 0.0
    intercept = mean_y - (slope * mean_x)
    return slope, intercept


def predict_point(index, slope, intercept):
    return max(0.0, min(100.0, slope * index + intercept))


def mape(actual, predicted):
    pairs = [(a, p) for a, p in zip(actual, predicted) if a != 0]
    if not pairs:
        return 0.0
    return round(sum(abs((a - p) / a) for a, p in pairs) / len(pairs) * 100, 2)


def build_forecast(values, horizon):
    split = int(len(values) * 0.8)
    train = values[:split]
    valid = values[split:]

    slope, intercept = fit_linear_regression(train)
    valid_pred = [predict_point(split + i, slope, intercept) for i in range(len(valid))]
    validation_mape = mape(valid, valid_pred)

    start_index = len(values)
    forecast = [round(predict_point(start_index + i, slope, intercept), 2) for i in range(horizon)]
    peak = max(forecast) if forecast else 0.0
    recommendation = "scale-up" if peak >= 80.0 else "maintain"

    return {
        "model": {"type": "linear_regression", "slope": round(slope, 6), "intercept": round(intercept, 6)},
        "validation": {"mape_percent": validation_mape, "validation_points": len(valid)},
        "forecast": forecast,
        "recommendation": recommendation,
    }


def load_cpu_values(path):
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [float(row["cpu_pct"]) for row in rows]


def main():
    parser = argparse.ArgumentParser(description="CPU capacity forecast")
    parser.add_argument("--input", required=True, help="CSV input file")
    parser.add_argument("--output", required=True, help="JSON output file")
    parser.add_argument("--horizon", type=int, default=24, help="Forecast horizon")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    values = load_cpu_values(input_path)
    report = build_forecast(values, args.horizon)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Generated forecast report: {output_path}")


if __name__ == "__main__":
    main()
