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


def predict_linear(train, horizon, validation_size):
    slope, intercept = fit_linear_regression(train)
    valid_pred = [predict_point(len(train) + i, slope, intercept) for i in range(validation_size)]
    future = [round(predict_point(len(train) + validation_size + i, slope, intercept), 2) for i in range(horizon)]
    return valid_pred, future, {"type": "linear_regression", "slope": round(slope, 6), "intercept": round(intercept, 6)}


def predict_moving_average(train, horizon, validation_size, window=6):
    history = list(train)
    valid_pred = []
    for _ in range(validation_size):
        sample = history[-window:] if len(history) >= window else history
        pred = sum(sample) / len(sample)
        valid_pred.append(round(pred, 2))
        history.append(pred)
    future = []
    for _ in range(horizon):
        sample = history[-window:] if len(history) >= window else history
        pred = sum(sample) / len(sample)
        pred = round(max(0.0, min(100.0, pred)), 2)
        future.append(pred)
        history.append(pred)
    return valid_pred, future, {"type": "moving_average", "window": window}


def recommend_capacity(forecast, current_capacity_vcpu=8):
    peak = max(forecast) if forecast else 0.0
    needed_vcpu = max(current_capacity_vcpu, int((peak / 100.0) * current_capacity_vcpu * 1.3) + 1)
    if peak >= 80.0:
        return "scale-up", needed_vcpu, peak
    return "maintain", current_capacity_vcpu, peak


def build_forecast(values, horizon, current_capacity_vcpu=8):
    split = int(len(values) * 0.8)
    train = values[:split]
    valid = values[split:]
    validation_size = len(valid)

    linear_valid, linear_future, linear_model = predict_linear(train, horizon, validation_size)
    ma_valid, ma_future, ma_model = predict_moving_average(train, horizon, validation_size)
    linear_mape = mape(valid, linear_valid)
    ma_mape = mape(valid, ma_valid)

    if linear_mape <= ma_mape:
        selected_model = linear_model
        forecast = linear_future
        selected_mape = linear_mape
        challenger = {"model": ma_model, "mape_percent": ma_mape}
    else:
        selected_model = ma_model
        forecast = ma_future
        selected_mape = ma_mape
        challenger = {"model": linear_model, "mape_percent": linear_mape}

    recommendation, recommended_vcpu, peak = recommend_capacity(forecast, current_capacity_vcpu)

    return {
        "model": selected_model,
        "validation": {
            "selected_model_mape_percent": selected_mape,
            "validation_points": len(valid),
            "challenger": challenger,
        },
        "forecast": forecast,
        "recommendation": recommendation,
        "capacity": {
            "current_vcpu": current_capacity_vcpu,
            "recommended_vcpu": recommended_vcpu,
            "forecast_peak_cpu_percent": round(peak, 2),
        },
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
    parser.add_argument("--current-vcpu", type=int, default=8, help="Current vCPU capacity")
    parser.add_argument("--csv-output", help="Optional forecast CSV path")
    parser.add_argument("--markdown-output", help="Optional markdown report path")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    values = load_cpu_values(input_path)
    report = build_forecast(values, args.horizon, current_capacity_vcpu=args.current_vcpu)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Generated forecast report: {output_path}")
    if args.csv_output:
        csv_path = Path(args.csv_output)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        with csv_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["step", "forecast_cpu_pct"])
            for idx, value in enumerate(report["forecast"], start=1):
                writer.writerow([idx, value])
        print(f"Generated forecast csv: {csv_path}")
    if args.markdown_output:
        md_path = Path(args.markdown_output)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md = (
            "# CPU Forecast Report\n\n"
            f"- Selected model: {report['model']['type']}\n"
            f"- Validation MAPE: {report['validation']['selected_model_mape_percent']}%\n"
            f"- Recommendation: {report['recommendation']}\n"
            f"- Recommended vCPU: {report['capacity']['recommended_vcpu']}\n"
            f"- Forecast peak CPU: {report['capacity']['forecast_peak_cpu_percent']}%\n"
        )
        md_path.write_text(md, encoding="utf-8")
        print(f"Generated forecast markdown: {md_path}")


if __name__ == "__main__":
    main()
