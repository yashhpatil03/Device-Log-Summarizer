# Prompt Log

> **Honesty note:** Sections marked **[PLACEHOLDER]** are examples to be replaced
> with what actually happens when *you* run the first AI-generated chart.
> Do not submit the placeholder as if it were a real event.

## 1. Initial Prompt
The prompt I gave to the AI assistant:

```
Act as a senior Python developer and software engineering mentor.
I have uploaded my Software Engineering Intern Coding Assessment PDF. I need you
to complete the entire assignment according to the exact requirements in the PDF.
Project: Device Log Summarizer CLI Tool. Create main.py (clean_sensor_readings
function, CSV reading with the csv module, grouping by device_id, total records,
average temperature, ERROR count, exclusion of devices with average temperature
above 80.0, summary.json export, terminal table, error handling), chart.py
(Matplotlib bar chart from summary.json with title, axis labels, value labels,
tight_layout(), saved as temperature_chart.png), a sample CSV, README.md,
requirements.txt, .gitignore, and this PROMPT_LOG.md. Keep it beginner-friendly.
```

## 2. Bug / Formatting Mistake in the First Chart
**[PLACEHOLDER - replace after testing]**

Example only (not claimed as a real event): *"In the first version, the temperature
labels above the bars overlapped the top border of the chart, and the X-axis device
names were crowded together."*

What I actually saw when I ran my first chart:
`<write your real observation here, or "No issues found">`

## 3. Follow-up Prompt Used to Fix It
**[PLACEHOLDER - replace with your real follow-up prompt]**

Example: *"The value labels collide with the top of the plot and the X labels overlap.
Add headroom to the Y-axis, rotate the X labels 45 degrees, and keep tight_layout()."*

## 4. Improvements Made
The final `chart.py` includes these safeguards (these are in the code today):
- Y-axis limit set to 115% of the tallest bar so value labels are not cut off.
- X-axis labels rotated 45 degrees with right alignment to avoid overlap.
- Temperature value (2 decimals) shown above each bar.
- Title and axis labels (units in °C).
- `tight_layout()` before saving.
- Graceful errors for a missing, invalid, or empty `summary.json`.

*(If your real bug differs, update this list to match.)*

## 5. How AI Was Used During Development
- Generated the first version of the project structure and code.
- Helped plan edge cases (empty CSV, missing columns, bad temperatures).
- The sample CSV was designed so DEV_C (average 88.00) is excluded and
  DEV_F (average exactly 80.00) is kept, which tests the "above 80.0" rule.
- Calculations were checked by hand (e.g. DEV_A: 360 / 5 = 72.00) and error
  handling was tested with bad inputs.
- **Section 1 of the assessment says to solve it without AI.** If you need to follow
  that rule strictly, rewrite `clean_sensor_readings` yourself and mention it here.
