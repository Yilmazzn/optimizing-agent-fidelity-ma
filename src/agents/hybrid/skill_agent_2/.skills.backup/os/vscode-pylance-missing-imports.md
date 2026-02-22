---
annotations: []
description: Suppress Pylance/Pyright “missing imports” diagnostics via diagnosticSeverityOverrides
metrics:
  negative_impact: 0
  neutral_impact: 0
  positive_impact: 0
  times_followed: 0.0
  times_requested: 0
name: vscode-pylance-missing-imports
---

## Disable only the noisy missing-import diagnostics (keep analysis on)
1. Open the JSON settings file:
   - `Ctrl+Shift+P` → **Preferences: Open User Settings (JSON)**, or
   - `Ctrl+Shift+P` → **Preferences: Open Workspace Settings (JSON)** (per-project).
2. Add this at the **top level** of the JSON object:
   ```json
   "python.analysis.diagnosticSeverityOverrides": {
     "reportMissingImports": "none",
     "reportMissingModuleSource": "none"
   }
   ```
3. If diagnostics don’t update: `Ctrl+Shift+P` → **Python: Restart Language Server** (or **Developer: Reload Window**).

### Notes
- Prefer this over turning off analysis globally (e.g., `python.analysis.typeCheckingMode: "off"`).
- To downgrade instead of disable, use `"warning"` rather than `"none"`.