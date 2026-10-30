"""
Device Log Summarizer CLI Tool
------------------------------
Section 1: clean_sensor_readings() + simple test cases (run with --test)
Section 2: Read device_telemetry.csv, group by device, compute statistics,
           filter hot devices, export summary.json and print a table.

Usage:
    python main.py                      # process the default CSV
    python main.py --test               # run the Section 1 test cases
    python main.py --input other.csv    # use a different CSV file
"""

import argparse
import csv
import json
import math
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Settings (paths are relative to this file so it works on any computer)
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DEFAULT_CSV_PATH = BASE_DIR / "device_telemetry.csv"
OUTPUT_JSON_PATH = BASE_DIR / "summary.json"

REQUIRED_COLUMNS = ["device_id", "status", "temperature"]
VALID_STATUSES = {"ACTIVE", "WARNING", "ERROR"}
MAX_SENSOR_VALUE = 500.0
MAX_AVERAGE_TEMPERATURE = 80.0


class CsvDataError(Exception):
    """Raised when the CSV file cannot be used (missing, empty, bad columns...)."""


# ---------------------------------------------------------------------------
# SECTION 1: Coding logic and sanitization
# ---------------------------------------------------------------------------
def clean_sensor_readings(readings):
    """
    Clean a list of mixed sensor readings and return a list of floats.

    Steps:
      1. Convert each item to float (strings like "42.5" are accepted).
      2. Drop None, values that cannot be converted, and negative values.
      3. Cap any value above 500.0 at 500.0.

    Empty lists, None, or lists with only invalid entries return [].
    """
    if not readings:  # handles [] and None
        return []

    cleaned = []
    for item in readings:
        if item is None:
            continue
        if isinstance(item, bool):  # True/False are not real sensor values
            continue
        try:
            value = float(item)
        except (ValueError, TypeError):
            continue  # cannot be converted -> drop it
        if math.isnan(value) or value < 0:
            continue  # NaN and negative error flags are dropped
        cleaned.append(min(value, MAX_SENSOR_VALUE))  # clip to 500.0
    return cleaned


def run_sanitization_tests():
    """Run simple test cases for clean_sensor_readings(). Returns True if all pass."""
    test_cases = [
        (
            "Normal mixed input",
            [10, "20.5", None, "abc", -5, 600, "750.2", 0, "-1"],
            [10.0, 20.5, 500.0, 500.0, 0.0],
        ),
        ("Entirely invalid input", [None, "bad", "", -1, "-3.2", [1, 2]], []),
        ("Empty list", [], []),
    ]

    all_passed = True
    print("Running tests for clean_sensor_readings()...")
    for name, test_input, expected in test_cases:
        actual = clean_sensor_readings(test_input)
        passed = actual == expected
        all_passed = all_passed and passed
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
        if not passed:
            print(f"         expected: {expected}")
            print(f"         actual:   {actual}")
    print("All tests passed." if all_passed else "Some tests FAILED.")
    return all_passed


# ---------------------------------------------------------------------------
# SECTION 2: Core data processing
# ---------------------------------------------------------------------------
def read_telemetry_csv(csv_path):
    """
    Read the CSV file and return (valid_records, skipped_messages).

    Raises CsvDataError for file-level problems (missing file, empty file,
    missing columns). Bad individual rows are skipped and reported.
    """
    csv_path = Path(csv_path)
    if not csv_path.is_file():
        raise CsvDataError(f"CSV file not found: {csv_path}")

    records = []
    skipped = []

    try:
        with open(csv_path, newline="", encoding="utf-8-sig") as csv_file:
            reader = csv.DictReader(csv_file)

            if reader.fieldnames is None:
                raise CsvDataError("The CSV file is empty.")

            header = [name.strip() for name in reader.fieldnames]
            missing = [col for col in REQUIRED_COLUMNS if col not in header]
            if missing:
                raise CsvDataError(
                    f"Missing required column(s): {', '.join(missing)}. "
                    f"Found columns: {', '.join(header)}"
                )
            reader.fieldnames = header  # use the cleaned header names

            for line_number, row in enumerate(reader, start=2):  # line 1 = header
                record, problem = parse_row(row)
                if problem:
                    skipped.append(f"Line {line_number}: {problem}")
                else:
                    records.append(record)
    except PermissionError:
        raise CsvDataError(f"No permission to read: {csv_path}")
    except UnicodeDecodeError:
        raise CsvDataError("The file is not a readable text/CSV file.")
    except csv.Error as error:
        raise CsvDataError(f"Could not parse the CSV file: {error}")

    if not records and not skipped:
        raise CsvDataError("The CSV file has a header but no data rows.")

    return records, skipped


def parse_row(row):
    """
    Validate one CSV row.
    Returns (record_dict, None) if valid, or (None, problem_text) if invalid.
    """
    device_id = (row.get("device_id") or "").strip()
    status = (row.get("status") or "").strip().upper()
    temperature_text = (row.get("temperature") or "").strip()

    if not device_id:
        return None, "missing device_id"
    if status not in VALID_STATUSES:
        return None, f"invalid status '{status}'"
    if not temperature_text:
        return None, "missing temperature"

    try:
        temperature = float(temperature_text)
    except ValueError:
        return None, f"invalid temperature '{temperature_text}'"
    if math.isnan(temperature) or math.isinf(temperature):
        return None, f"invalid temperature '{temperature_text}'"

    return {"device_id": device_id, "status": status, "temperature": temperature}, None


def summarize_by_device(records):
    """Group records by device_id and compute the statistics for each device."""
    grouped = {}
    for record in records:
        grouped.setdefault(record["device_id"], []).append(record)

    summary = []
    for device_id in sorted(grouped):
        device_records = grouped[device_id]
        temperatures = [r["temperature"] for r in device_records]
        error_count = sum(1 for r in device_records if r["status"] == "ERROR")
        summary.append(
            {
                "device_id": device_id,
                "total_records": len(device_records),
                "average_temperature": round(sum(temperatures) / len(temperatures), 2),
                "error_count": error_count,
            }
        )
    return summary


def filter_hot_devices(summary):
    """Keep devices whose average temperature is NOT above 80.0."""
    kept = [d for d in summary if d["average_temperature"] <= MAX_AVERAGE_TEMPERATURE]
    excluded = [d for d in summary if d["average_temperature"] > MAX_AVERAGE_TEMPERATURE]
    return kept, excluded


def save_summary_json(summary, output_path):
    """Write the summary list to a JSON file."""
    try:
        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(summary, json_file, indent=4)
    except OSError as error:
        raise CsvDataError(f"Could not write {output_path}: {error}")


def print_summary_table(summary):
    """Print a clean, readable table in the terminal."""
    headers = ["Device ID", "Total Records", "Avg Temp (C)", "ERROR Count"]
    rows = [
        [d["device_id"], str(d["total_records"]),
         f"{d['average_temperature']:.2f}", str(d["error_count"])]
        for d in summary
    ]
    widths = [max(len(headers[i]), *(len(r[i]) for r in rows)) if rows else len(headers[i])
              for i in range(len(headers))]

    def format_line(cells):
        return " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells))

    separator = "-+-".join("-" * w for w in widths)
    print(format_line(headers))
    print(separator)
    for row in rows:
        print(format_line(row))


def parse_arguments():
    parser = argparse.ArgumentParser(description="Device Log Summarizer CLI Tool")
    parser.add_argument("--input", default=str(DEFAULT_CSV_PATH),
                        help="path to the telemetry CSV (default: device_telemetry.csv)")
    parser.add_argument("--output", default=str(OUTPUT_JSON_PATH),
                        help="path for the JSON summary (default: summary.json)")
    parser.add_argument("--test", action="store_true",
                        help="run the Section 1 test cases and exit")
    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.test:
        sys.exit(0 if run_sanitization_tests() else 1)

    try:
        records, skipped = read_telemetry_csv(args.input)

        if skipped:
            print(f"Warning: skipped {len(skipped)} invalid record(s):")
            for message in skipped:
                print(f"  - {message}")
            print()

        if not records:
            raise CsvDataError("No valid records found in the CSV file.")

        summary = summarize_by_device(records)
        kept, excluded = filter_hot_devices(summary)
        save_summary_json(kept, args.output)
    except CsvDataError as error:
        print(f"Error: {error}")
        sys.exit(1)

    print(f"Processed {len(records)} valid records from {len(summary)} devices.")
    if excluded:
        names = ", ".join(f"{d['device_id']} ({d['average_temperature']:.2f})" for d in excluded)
        print(f"Excluded (average temperature > {MAX_AVERAGE_TEMPERATURE}): {names}")
    print()

    if kept:
        print_summary_table(kept)
    else:
        print("No devices left after filtering.")
    print(f"\nSummary saved to: {Path(args.output).name}")


if __name__ == "__main__":
    main()
