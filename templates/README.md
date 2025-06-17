# Template Library – Reusable Engineering Functions

This folder contains modular Python templates designed to streamline common engineering workflows such as data loading, transformation, statistical modeling, SPC, visualization, and synthetic test generation.

Each template is structured for practical reuse by engineers with minimal Python background and reflects real-world production needs in process development, MSAT, and manufacturing analytics roles.

---

## Intended Use Cases

This library is intended to help engineers or technical teams:
- Build lightweight internal tools for data triage or visualization
- Standardize pipeline functions across multiple case studies or departments
- Prototype real-time risk assessment, defect monitoring, or SPC workflows
- Enable consistent and transparent handoffs between engineers

Ideal for situations such as:
- QC lag time impacting real-time decisions
- Need for consistent model scoring logic across products
- Debugging spatial, temporal, or statistical trends in manufacturing data

---

## Folder Structure and Contents

Each folder contains modular `.py` files with reusable functions. All templates follow strict formatting, docstring, and commenting standards to support drop-in utility.

| Folder     | Contents |
|------------|----------|
| `io/`      | File loading, export, and batch log appending functions |
| `transform/` | Outlier detection, batch merging, SPC metric calculation |
| `models/`  | Training + inference logic for GMM, logistic regression |
| `plot/`    | Control charts, time-series risk plots, spatial defect maps |
| `test/`    | Synthetic data generators for batch metadata and defect maps |

All scripts include:
- Clear docstring headers
- Function-level documentation with parameter I/O
- Educational inline comments (for engineers with minimal Python experience)
- `if __name__ == "__main__"` test blocks for demo or debug use

---
## Template Standards Followed

All templates in this library follow a consistent and professional structure designed for clarity, maintainability, and easy adoption by other engineers. Key conventions include:

- **Consistent Naming**  
  File names follow the format `verb_noun[_modifier].py` (e.g., `load_csv_file.py`, `plot_risk_trend.py`), and function names use descriptive `snake_case` to clarify purpose at a glance.

- **Modular Function Design**  
  Each script includes one or more reusable functions with clean inputs and outputs. Parameters use intuitive names like `file_path`, `df`, `features`, or `threshold` for plug-and-play readability.

- **Docstring and Commenting Standards**  
  Every file begins with a structured docstring describing its purpose, inputs/outputs, and usage scenarios. Functions include inline comments that explain not just what the code does, but why — making the logic accessible to engineers with varying levels of Python fluency.

- **Testability and Self-Demo**  
  Templates include optional `if __name__ == "__main__"` blocks that demonstrate basic usage and serve as sanity checks during development.

- **Model Template Consistency**  
  All model training templates (e.g., logistic regression, GMM) include:
  - Generalized parameter names (no hard-coded metric logic)
  - A step-by-step transformation flow (label generation → scaling → training → prediction)
  - AUC and accuracy metrics to assess model quality
  - Compatibility with new batch inference using shared `apply_model_to_batch.py`

- **Style Alignment Across Projects**  
  The same conventions are used in all case study folders, making it easy to mix, extend, or repurpose code without translation overhead.

These standards are designed not only to demonstrate Python fluency, but also to reflect real-world engineering practices such as traceability, modular tool development, and internal team handoff readiness.

## Example Usage Pattern

Templates are designed to be chained in real-world workflows:

```python
from io.load_csv_file import load_csv_file
from transform.compute_spc_metrics import compute_spc_metrics
from plot.plot_control_chart import plot_control_chart

# Load and analyze data
df = load_csv_file('example.csv')
stats = compute_spc_metrics(df['thickness_nm'])
plot_control_chart(df['thickness_nm'], stats, output_path='spc_chart.png')
```

Other workflows might combine:
- GMM clustering and cluster-wise failure scoring
- Logistic regression training with real QC thresholds
- Model application to new batches without final lab results

---

## Alignment With Case Studies

Each template in this folder originated from a real case study in the repo:
- `batch_summary_tool/`
- `spatial_defect_map_tool/`
- `spc_summary_tool/`

Templates were extracted and standardized to promote reuse across projects and to reflect staff-level thinking around internal tool generalization, onboarding enablement, and systems integration.

