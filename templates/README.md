# Template Library – Reusable Engineering Functions

This folder contains modular Python templates designed to streamline engineering workflows such as data loading, transformation, statistical modeling, SPC, visualization, and test data generation.

Each script is structured for real-world clarity and reuse, especially by engineers in process development, MSAT, and manufacturing analytics roles including those with limited Python experience.

---

## Intended Use Cases

This library supports:
- Lightweight internal tooling for triage or visualization
- Standardized logic across case studies or product lines
- Rapid prototyping of batch scoring, SPC analysis, and risk triage tools
- Easier onboarding and knowledge transfer across engineering teams

Especially helpful when:
- QC results are delayed
- Early detection or parameter-space clustering is needed
- Visualization or model application needs to be consistent and repeatable

---

## Folder Structure

| Folder       | Description |
|--------------|-------------|
| `io/`        | Load and export data, append batch records |
| `transform/` | Merge datasets, detect outliers, compute SPC metrics |
| `models/`    | Train/apply GMM and logistic regression models |
| `plot/`      | Generate control charts, risk trend plots, and defect maps |
| `test/`      | Generate synthetic batch and defect data for testing |

---

## Template Conventions

All templates follow a consistent structure for clarity, maintainability, and adaptability:

- **Naming:** `verb_noun[_modifier].py` (e.g., `load_csv_file.py`, `train_logistic_regression.py`)
- **Function Design:** Clean inputs/outputs; intuitive variable names (`df`, `features`, `threshold`, etc.)
- **Docstrings:** File-level and function-level explanations with I/O details and real-world usage context
- **Inline Comments:** Explain rationale, not just behavior
- **Demo Blocks:** Optional `if __name__ == "__main__"` sections for testing and illustration
- **Model Templates:** Follow a shared structure with normalization, training, scoring, and AUC/accuracy evaluation
- **Cross-Project Consistency:** Shared conventions across all case studies for easy mixing and reuse

These standards emphasize traceability, team handoff readiness, and alignment with real production environments.

---

## Example Usage Pattern

Templates are designed to plug into one another across a typical workflow:

```python
from io.load_csv_file import load_csv_file
from transform.compute_spc_metrics import compute_spc_metrics
from plot.plot_control_chart import plot_control_chart

# Load and analyze process data
df = load_csv_file('example.csv')
stats = compute_spc_metrics(df['thickness_nm'])
plot_control_chart(df['thickness_nm'], stats, output_path='spc_chart.png')
```

Other workflows may include:
- Cluster-based failure risk mapping with GMM
- Binary classification using logistic regression
- Applying trained models to new batches before QC is complete

---

## Connection to Case Studies

These templates were extracted and standardized from real case studies in this repository:
- `batch_summary_tool/`
- `spatial_defect_map_tool/`
- `spc_summary_tool/`

The goal is to demonstrate how reusable, lightweight tooling can improve visibility, reduce QC delays, and support staff-level responsibilities in production environments.
