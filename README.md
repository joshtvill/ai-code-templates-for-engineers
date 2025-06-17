# Manufacturing Data Toolkit

This repository showcases reusable, lightweight Python tooling that a senior or staff-level engineer might prototype to support internal process development, MSAT workflows, manufacturing data analysis, or systems integration.

All code is structured for clarity, maintainability, and adaptation by teams, with consistent naming, modular logic, and documented interfaces.

---

## Why This Repo Exists

In many production environments, engineers encounter recurring bottlenecks: QC results are delayed, model logic is scattered across scripts, or there is no shared framework for quick triage or prototyping.

This repo demonstrates how one engineer might address those gaps by:
- Building simple, understandable tools for batch scoring, SPC, and defect mapping
- Standardizing analysis blocks to improve reuse and reduce onboarding time
- Aligning tool logic to real workflows in early-phase manufacturing and tech transfer

The goal is not to replace enterprise systems, but to show how fast, testable code can increase visibility, support decisions, and accelerate engineering feedback cycles.

---

## How This Might Be Used on a Real Team

If embedded in a cross-functional team, these tools could be adapted to:
- Score incoming batches before QC is finalized
- Visualize inline parameter drift or SPC excursions
- Map defects spatially for faster root cause narrowing
- Create modular functions that feed into internal dashboards or notebooks

Everything here is built to plug into a real process environment, not just run in isolation.

---

## Repository Structure

| Folder               | Description |
|----------------------|-------------|
| `case_studies/`      | Three complete tools simulating batch scoring, defect triage, and SPC analysis |
| `templates/`         | Reusable Python modules grouped by function: I/O, transform, model, plot, test |

---

## Case Studies

| Case Study               | Summary |
|--------------------------|---------|
| `batch_summary_tool/`    | Uses GMM and logistic regression to estimate risk of QC failure from process inputs |
| `spatial_defect_map_tool/` | Visualizes defect (x, y) clustering by type for debug and triage |
| `spc_summary_tool/`      | Calculates control limits, flags outliers, and plots SPC trend lines for a single process metric |

Each case study is fully self-contained with:
- Input and output example files
- Visual output (plots)
- Docstring-driven code with inline commentary
- A README describing use case, expected behavior, and setup

---

## About the Template Library

Templates in `/templates/` are modular, testable blocks extracted from real case logic:
- `io/`: Load, save, append
- `transform/`: Detect outliers, merge batch and QC data, calculate SPC stats
- `models/`: Train and apply GMM or logistic regression
- `plot/`: Render SPC charts, risk scores over time, spatial maps
- `test/`: Generate synthetic batch and defect data

These templates follow consistent conventions:
- Docstring headers and parameter explanations
- `snake_case` naming for files and functions
- Optional `__main__` blocks for standalone testing

---

## Example Usage Pattern

```python
from io.load_csv_file import load_csv_file
from transform.compute_spc_metrics import compute_spc_metrics
from plot.plot_control_chart import plot_control_chart

df = load_csv_file('example_data.csv')
stats = compute_spc_metrics(df['thickness'])
plot_control_chart(df['thickness'], stats, output_path='spc_chart.png')
```

Other workflows include:
- Training models on historical batch data
- Estimating batch risk using model predictions
- Visualizing outliers or trends across time

---

## Development Note

This repository was created using a hybrid workflow combining engineering domain knowledge with AI-assisted development to accelerate prototype generation. Every function and output was designed for real-world applicability and team handoff readiness.
