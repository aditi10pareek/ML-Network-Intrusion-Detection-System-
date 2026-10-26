"""Run reproducible exploratory analysis for the supplied UNSW-NB15 CSV files."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)
sns.set_theme(style="whitegrid", palette="deep")


def quality(frame: pd.DataFrame) -> dict[str, int]:
    numeric = frame.select_dtypes(include=np.number)
    without_id = frame.drop(columns=["id"], errors="ignore")
    return {
        "rows": len(frame),
        "columns": frame.shape[1],
        "duplicate rows (excluding id)": int(without_id.duplicated().sum()),
        "missing cells": int(frame.isna().sum().sum()),
        "infinite numeric cells": int(np.isinf(numeric).sum().sum()),
    }


def write_count_plot(train: pd.DataFrame) -> None:
    counts = train["label"].fillna("<missing>").value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.barplot(x=counts.index.astype(str), y=counts.values, ax=ax, color="#3B82F6")
    ax.set(title="Training set: binary label distribution", xlabel="label (0 = normal, 1 = attack)", ylabel="Flows")
    fig.tight_layout()
    fig.savefig(FIGURES / "target_distributions.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def write_categorical_plots(train: pd.DataFrame) -> list[str]:
    made = []
    for col in ("proto", "service", "state"):
        if col not in train:
            continue
        top = train[col].fillna("<missing>").value_counts().head(12).index
        table = pd.crosstab(train[col].fillna("<missing>"), train["label"], normalize="index")
        table = table.reindex(top).dropna(how="all")
        ax = table.plot(kind="bar", stacked=True, figsize=(10, 4), color=["#60A5FA", "#F97316"])
        ax.set(title=f"Binary label mix by {col} (top categories)", xlabel=col, ylabel="Proportion")
        ax.legend(title="label", labels=["Normal (0)", "Attack (1)"])
        plt.xticks(rotation=35, ha="right")
        plt.tight_layout()
        out = FIGURES / f"{col}_by_label.png"
        plt.savefig(out, dpi=160, bbox_inches="tight")
        plt.close()
        made.append(out.name)
    return made


def write_numeric_plot(train: pd.DataFrame) -> str | None:
    candidates = [
        c for c in ("dur", "spkts", "dpkts", "sbytes", "dbytes", "rate", "sload", "dload", "ct_dst_sport_ltm", "ct_srv_dst")
        if c in train
    ]
    if not candidates:
        return None
    rows = 2
    cols = 3
    fig, axes = plt.subplots(rows, cols, figsize=(15, 8))
    axes = axes.ravel()
    for ax, col in zip(axes, candidates):
        for label, subset in train.groupby("label", observed=True):
            values = pd.to_numeric(subset[col], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
            values = values[values >= 0]
            if len(values) > 100_000:
                values = values.sample(100_000, random_state=42)
            ax.hist(values, bins=40, density=True, histtype="step", linewidth=1.4, label=str(label), log=True)
        ax.set(title=col, xlabel="Value", ylabel="Density (log scale)")
    for ax in axes[len(candidates):]:
        ax.remove()
    axes[0].legend(title="label (0 normal, 1 attack)")
    fig.suptitle("Selected numeric feature distributions")
    fig.tight_layout()
    fig.savefig(FIGURES / "numeric_feature_distributions.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    return "numeric_feature_distributions.png"


def write_correlation_plot(train: pd.DataFrame) -> tuple[str | None, pd.DataFrame]:
    numeric = train.select_dtypes(include=np.number).drop(columns=["id", "label"], errors="ignore")
    corr = numeric.corr(numeric_only=True)
    if corr.empty:
        return None, pd.DataFrame()
    fig, ax = plt.subplots(figsize=(14, 11))
    sns.heatmap(corr, cmap="coolwarm", center=0, vmin=-1, vmax=1, ax=ax, cbar_kws={"shrink": 0.75})
    ax.set_title("Training set numeric feature correlation")
    fig.tight_layout()
    fig.savefig(FIGURES / "numeric_correlation_heatmap.png", dpi=160, bbox_inches="tight")
    plt.close(fig)
    pairs = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool)).stack().rename("correlation").reset_index()
    pairs.columns = ["feature_1", "feature_2", "correlation"]
    return "numeric_correlation_heatmap.png", pairs.assign(abs_correlation=pairs.correlation.abs()).sort_values("abs_correlation", ascending=False)


def main() -> None:
    train_path = DATA / "UNSW_NB15_training-set.csv"
    test_path = DATA / "UNSW_NB15_testing-set.csv"
    train = pd.read_csv(train_path, low_memory=False)
    test = pd.read_csv(test_path, low_memory=False)

    issues = pd.DataFrame({"train": quality(train), "test": quality(test)})
    schema = pd.DataFrame({"train_dtype": train.dtypes.astype(str), "test_dtype": test.dtypes.astype(str)})
    schema["same_dtype"] = schema.train_dtype == schema.test_dtype
    overlap = len(set(train["id"]) & set(test["id"])) if "id" in train and "id" in test else None
    train_without_id = train.drop(columns=["id"], errors="ignore")
    test_without_id = test.drop(columns=["id"], errors="ignore")
    train_row_hashes = set(pd.util.hash_pandas_object(train_without_id, index=False))
    shared_records = int(pd.util.hash_pandas_object(test_without_id, index=False).isin(train_row_hashes).sum())
    id_summary = ""
    if "id" in train and "id" in test:
        id_summary = (
            f"`id` ranges are {train.id.min():,}–{train.id.max():,} in train and "
            f"{test.id.min():,}–{test.id.max():,} in test; values are unique within each file, "
            "but the row numbering restarts in the test file, so the cross-file ID overlap is not a record-overlap test."
        )

    write_count_plot(train)
    cat_figures = write_categorical_plots(train)
    numeric_fig = write_numeric_plot(train)
    corr_fig, pairs = write_correlation_plot(train)

    lines = [
        "# UNSW-NB15 Exploratory Data Analysis", "",
        "## Dataset overview", "",
        f"- Training file: `{train_path.name}` — {len(train):,} rows × {train.shape[1]} columns.",
        f"- Testing file: `{test_path.name}` — {len(test):,} rows × {test.shape[1]} columns.",
        f"- Train/test schema columns match: {set(train.columns) == set(test.columns)}.",
        f"- Columns with differing dtypes: {', '.join(schema.index[~schema.same_dtype]) if (~schema.same_dtype).any() else 'none'}.",
        f"- Shared `id` values across provided splits: {overlap:,}. {id_summary}" if overlap is not None else "- No `id` column available for split overlap check.", "",
        f"- Test rows exactly matching a training row after dropping `id` (all other columns, including labels): {shared_records:,}.", "",
        "## Data quality", "", "| Check | Training | Testing |", "|---|---:|---:|",
    ]
    for metric in issues.index:
        lines.append(f"| {metric.title()} | {issues.loc[metric, 'train']:,} | {issues.loc[metric, 'test']:,} |")
    lines.extend(["", "## Binary target balance", "", "| Label | Meaning | Train count | Train % | Test count | Test % |", "|---:|---|---:|---:|---:|---:|"])
    train_counts = train["label"].value_counts(dropna=False)
    test_counts = test["label"].value_counts(dropna=False)
    meanings = {0: "Normal", 1: "Attack"}
    for cls in sorted(set(train_counts.index) | set(test_counts.index)):
        ntr, nte = int(train_counts.get(cls, 0)), int(test_counts.get(cls, 0))
        lines.append(f"| {cls} | {meanings.get(cls, 'Unknown')} | {ntr:,} | {ntr / len(train) * 100:.2f}% | {nte:,} | {nte / len(test) * 100:.2f}% |")
    lines.append("")
    lines.extend(["## Feature inspection", "", "### Categorical feature top values", ""])
    for col in ("proto", "service", "state"):
        if col in train:
            lines.append(f"- `{col}`: " + ", ".join(f"{k} ({v:,})" for k, v in train[col].fillna("<missing>").value_counts().head(8).items()))
    lines.extend(["", "### Numeric predictor summary", "", "```text", train.select_dtypes(include=np.number).drop(columns=["id", "label"], errors="ignore").describe(percentiles=[.01, .5, .99]).round(3).to_string(), "```", ""])
    if not pairs.empty:
        lines.extend(["### Strongest numeric correlations", "", "| Feature 1 | Feature 2 | Correlation |", "|---|---|---:|"])
        for row in pairs.head(12).itertuples(index=False):
            lines.append(f"| {row.feature_1} | {row.feature_2} | {row.correlation:.3f} |")
    lines.extend([
        "", "## Modeling implications", "",
        "- Use `label` as the binary target: 0 = normal and 1 = attack.",
        "- Exclude `id`, `label`, and `attack_cat` from model features; `attack_cat` is not used in this binary task.",
        "- Keep the provided training and testing files as separate splits for final evaluation.",
        "- Check attack precision, attack recall, F1, and the confusion matrix alongside accuracy because class proportions differ between the supplied splits.",
        "- Fit imputers, encoders, scaling, feature selection, and any resampling on training data only, preferably in a pipeline.",
        "- Duplicate-row counts above ignore the `id` field, so otherwise identical flows are detected even when their row identifiers differ.",
        f"- {shared_records:,} test rows exactly match a training row after dropping `id`; this overlap may make test metrics more optimistic for those records.",
        "- The `id` counter restarts in the test file; exclude it as an input feature.", "",
        "## Figures", "", "| Figure | Path |", "|---|---|",
        "| Binary label counts | `reports/figures/target_distributions.png` |",
    ])
    for name in cat_figures:
        lines.append(f"| Categorical feature versus label: {name.split('_')[0]} | `reports/figures/{name}` |")
    if numeric_fig:
        lines.append(f"| Numeric feature distributions | `reports/figures/{numeric_fig}` |")
    if corr_fig:
        lines.append(f"| Numeric correlation heatmap | `reports/figures/{corr_fig}` |")
    (REPORTS / "EDA_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    schema.to_csv(REPORTS / "schema_summary.csv", index_label="column")
    print(f"EDA complete. Report: {REPORTS / 'EDA_REPORT.md'}")
    print(f"Figures: {len(list(FIGURES.glob('*.png')))} saved to {FIGURES}")
    print(issues.to_string())


if __name__ == "__main__":
    main()
