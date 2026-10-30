# Device Log Summarizer CLI Tool

## Project Overview
A small Python command-line tool that reads device telemetry from a CSV file,
summarizes it per device, removes devices that run too hot, saves the result as
JSON, and draws a bar chart of average temperatures.

It was built for the Software Engineering Intern technical assessment.

## Features
- `clean_sensor_readings(readings)` cleans mixed sensor data (strings, `None`,
  negatives, values above 500.0) with built-in test cases (`python main.py --test`).
- Reads `device_telemetry.csv` with Python's built-in `csv` module.
- Groups by `device_id` and calculates: total records, average temperature,
  and number of `ERROR` records.
- Excludes devices whose average temperature is **above 80.0**
  (exactly 80.0 is kept).
- Exports results to `summary.json` and prints a readable table.
- Error handling for: missing file, empty file, missing/incorrect columns,
  invalid temperatures, and other invalid rows (skipped with a warning).
- `chart.py` creates `temperature_chart.png` using Matplotlib, with a title,
  axis labels, values above the bars, rotated labels, and `tight_layout()`.

## Prerequisites
- Python 3.8 or newer
- pip (comes with Python)

## Installation
```bash
# 1. Open a terminal inside the Device-Log-Summarizer folder
# 2. (Recommended) create a virtual environment
python -m venv venv

# Activate it:
#   Windows:      venv\Scripts\activate
#   macOS/Linux:  source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

## How to Run
```bash
python main.py --test   # run the Section 1 test cases
python main.py          # process the CSV, create summary.json, print the table
python chart.py         # create temperature_chart.png (run main.py first)
```
On some computers use `python3` instead of `python`.

Optional: `python main.py --input other_file.csv --output other_summary.json`

## Sample Terminal Output
`python main.py --test`
```
Running tests for clean_sensor_readings()...
  [PASS] Normal mixed input
  [PASS] Entirely invalid input
  [PASS] Empty list
All tests passed.
```

`python main.py`
```
Processed 23 valid records from 6 devices.
Excluded (average temperature > 80.0): DEV_C (88.00)

Device ID | Total Records | Avg Temp (C) | ERROR Count
----------+---------------+--------------+------------
DEV_A     | 5             | 72.00        | 1
DEV_B     | 4             | 60.50        | 0
DEV_D     | 4             | 79.75        | 2
DEV_E     | 3             | 47.67        | 0
DEV_F     | 2             | 80.00        | 1

Summary saved to: summary.json
```

`python chart.py`
```
Chart saved to: temperature_chart.png
```

## Expected Output Files
| File | Created by | Description |
|------|-----------|-------------|
| `summary.json` | `main.py` | Filtered per-device results |
| `temperature_chart.png` | `chart.py` | Bar chart of average temperature |

## Project Structure
```
Device-Log-Summarizer/
    main.py                 # Sections 1 and 2
    chart.py                # Section 3
    device_telemetry.csv    # sample input data
    summary.json            # output of main.py
    temperature_chart.png   # output of chart.py
    PROMPT_LOG.md           # AI usage log
    requirements.txt
    README.md
    .gitignore
```

## Notes
- Invalid CSV rows (bad status, bad/missing temperature, missing device_id) are
  skipped and listed as warnings; the rest of the data is still processed.
- Temperatures are not clipped or filtered by sign: only
  `clean_sensor_readings` applies the Section 1 rules.
