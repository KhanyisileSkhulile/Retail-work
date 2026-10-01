"""
M02-03 - Validate missing values and duplicates

Validates the raw retail store inventory dataset for missing values
and duplicate rows. Produces a markdown report as evidence.

Usage:
    python validate_data_quality.py

Author: Khanyisile Skhulile
Issue:  M02-03
"""

import os
from datetime import datetime

import pandas as pd


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATASET_PATH = os.path.join(REPO_ROOT, "dataset", "raw", "retail_store_inventory.csv")
OUTPUT_DIR = os.path.join(REPO_ROOT, "documentation", "03-data-analysis")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "M02-03-data-quality-results.md")


def validate_data_quality():
    print(f"Loading dataset from: {DATASET_PATH}")
    df = pd.read_csv(DATASET_PATH)

    lines = []
    lines.append("# M02-03 - Data Quality Validation Results\n")
    lines.append("**Issue:** M02-03  ")
    lines.append("**Analyst:** Khanyisile Skhulile  ")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  ")
    lines.append("**Source file:** `dataset/raw/retail_store_inventory.csv`\n")
    lines.append("---\n")

    # 1. Shape
    lines.append("## 1. Dataset Shape\n")
    lines.append(f"- **Rows:** {df.shape[0]:,}")
    lines.append(f"- **Columns:** {df.shape[1]}\n")

    # 2. Missing values - summary
    lines.append("## 2. Missing Values - Summary\n")
    total_cells = df.shape[0] * df.shape[1]
    total_missing = int(df.isna().sum().sum())
    lines.append(f"- **Total cells:** {total_cells:,}")
    lines.append(f"- **Missing cells:** {total_missing:,}")
    lines.append(f"- **Missing %:** {(100 * total_missing / total_cells):.4f}%\n")

    if total_missing == 0:
        lines.append("**No missing values detected anywhere in the dataset.**\n")
    else:
        lines.append("| Column | Missing | % of Column |")
        lines.append("|--------|---------|-------------|")
        for col in df.columns:
            n = int(df[col].isna().sum())
            if n > 0:
                pct = 100 * n / len(df)
                lines.append(f"| `{col}` | {n:,} | {pct:.2f}% |")
        lines.append("")

    # 3. Missing values - per column
    lines.append("## 3. Missing Values - Per Column\n")
    lines.append("| Column | Non-Null | Null | Null % |")
    lines.append("|--------|----------|------|--------|")
    for col in df.columns:
        nulls = int(df[col].isna().sum())
        non_null = df.shape[0] - nulls
        pct = 100 * nulls / df.shape[0]
        lines.append(f"| `{col}` | {non_null:,} | {nulls:,} | {pct:.2f}% |")
    lines.append("")

    # 4. Duplicate rows
    lines.append("## 4. Duplicate Rows\n")
    dupes = int(df.duplicated().sum())
    lines.append(f"- **Exact duplicate rows (all columns):** {dupes:,}\n")
    if dupes == 0:
        lines.append("**No duplicate rows detected.**\n")
    else:
        lines.append("Duplicate rows found. Samples:\n")
        lines.append("```")
        lines.append(
            df[df.duplicated(keep=False)]
            .sort_values(list(df.columns))
            .head(10)
            .to_string()
        )
        lines.append("```\n")

    # 5. Duplicate check on key columns
    lines.append("## 5. Duplicate Check on Key Columns\n")
    key_sets = [
        ["Date", "Store ID", "Product ID"],
        ["Store ID", "Product ID"],
    ]
    for keys in key_sets:
        if all(k in df.columns for k in keys):
            n_dupes = int(df.duplicated(subset=keys).sum())
            lines.append(f"- On `{' + '.join(keys)}`: **{n_dupes:,}** duplicate rows")
    lines.append("")

    # 6. Constant columns
    lines.append("## 6. Constant Columns (only one unique value)\n")
    constants_found = False
    for col in df.columns:
        if df[col].nunique(dropna=True) == 1:
            constants_found = True
            lines.append(
                f"- `{col}` has only one unique value: `{df[col].dropna().iloc[0]}`"
            )
    if not constants_found:
        lines.append("No constant columns detected.")
    lines.append("")

    # 7. Whitespace / empty-string check
    lines.append("## 7. Whitespace / Empty-String Check\n")
    issues_found = False
    for col in df.select_dtypes(include="object").columns:
        empty = int((df[col].astype(str).str.strip() == "").sum())
        if empty > 0:
            issues_found = True
            lines.append(f"- `{col}`: **{empty:,}** empty/whitespace-only values")
    if not issues_found:
        lines.append("No empty or whitespace-only string values detected.")
    lines.append("")

    # 8. Verdict
    lines.append("## 8. Verdict\n")
    issues = []
    if total_missing > 0:
        issues.append(f"{total_missing:,} missing values")
    if dupes > 0:
        issues.append(f"{dupes:,} duplicate rows")
    if issues:
        lines.append(f"**Issues found:** {', '.join(issues)}")
    else:
        lines.append("**Dataset passes all M02-03 quality checks.**")
        lines.append("- No missing values")
        lines.append("- No duplicate rows")
        lines.append("- No constant columns")
    lines.append("")

    # Write output
    report = "\n".join(lines)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\nReport written to: {OUTPUT_PATH}\n")
    print(report)


if __name__ == "__main__":
    validate_data_quality()