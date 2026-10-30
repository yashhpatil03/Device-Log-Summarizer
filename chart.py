"""
chart.py - Section 3
Loads summary.json and saves a bar chart of average temperature per device
as temperature_chart.png.

Usage:
    python main.py     # creates summary.json first
    python chart.py
"""

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # no pop-up window needed; we only save the image
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
SUMMARY_JSON_PATH = BASE_DIR / "summary.json"
CHART_PATH = BASE_DIR / "temperature_chart.png"


def load_summary(json_path):
    """Load and validate summary.json. Returns a non-empty list of devices."""
    json_path = Path(json_path)
    if not json_path.is_file():
        raise ValueError(f"{json_path.name} not found. Run 'python main.py' first.")

    try:
        with open(json_path, encoding="utf-8") as json_file:
            data = json.load(json_file)
    except json.JSONDecodeError as error:
        raise ValueError(f"{json_path.name} is not valid JSON: {error}")
    except OSError as error:
        raise ValueError(f"Could not read {json_path.name}: {error}")

    if not isinstance(data, list) or not data:
        raise ValueError(f"{json_path.name} must contain a non-empty list of devices.")

    for entry in data:
        if (not isinstance(entry, dict) or "device_id" not in entry
                or "average_temperature" not in entry):
            raise ValueError("Each entry needs 'device_id' and 'average_temperature'.")
        if isinstance(entry["average_temperature"], bool) or not isinstance(
                entry["average_temperature"], (int, float)):
            raise ValueError(f"Invalid average_temperature for {entry['device_id']}.")
    return data


def create_chart(summary, output_path):
    """Draw the bar chart and save it as a PNG."""
    device_ids = [d["device_id"] for d in summary]
    temperatures = [d["average_temperature"] for d in summary]

    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.bar(device_ids, temperatures, color="steelblue", edgecolor="black")

    ax.set_title("Average Temperature per Device")
    ax.set_xlabel("Device ID")
    ax.set_ylabel("Average Temperature (°C)")
    ax.set_ylim(0, max(temperatures) * 1.15)  # headroom so labels are not cut off

    # Temperature value above each bar
    for bar, temperature in zip(bars, temperatures):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{temperature:.2f}", ha="center", va="bottom", fontsize=10)

    plt.xticks(rotation=45, ha="right")  # avoid overlapping X labels
    plt.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)


def main():
    try:
        summary = load_summary(SUMMARY_JSON_PATH)
        create_chart(summary, CHART_PATH)
    except ValueError as error:
        print(f"Error: {error}")
        sys.exit(1)
    except OSError as error:
        print(f"Error: could not save the chart: {error}")
        sys.exit(1)
    print(f"Chart saved to: {CHART_PATH.name}")


if __name__ == "__main__":
    main()
