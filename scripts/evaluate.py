import argparse
import os
import sys
import time
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
DEFAULT_INPUT = PROJECT_ROOT / "data" / "eval_column_metadata.csv"
DEFAULT_RULES = Path("/Users/ericcai/Desktop/internfiles/分类分级标准.xlsx")
METADATA_COLUMNS = [
    "table_name",
    "column_name",
    "column_type",
    "column_description",
]
EXPECTED_COLUMNS = [
    "expected_classification_path",
    "expected_security_level",
    "expected_review_required",
]
MATCH_PROFILE_MODES = {"off", "always", "auto"}


def main():
    args = parse_args()
    os.environ["LLM_MATCH_PROFILE_MODE"] = args.mode
    sys.path.insert(0, str(SRC_DIR))

    from classifier import classify_column
    from llm_metrics import get_metrics, reset_metrics
    from rules import load_rule_catalog

    eval_df = _read_eval_input(args.input)
    eval_df = _slice_eval_input(
        df=eval_df,
        offset=args.offset,
        limit=args.limit,
    )
    rule_catalog = load_rule_catalog(args.rules)

    reset_metrics()
    started_at = time.perf_counter()
    results = []

    for _, row in eval_df.iterrows():
        column_info = _column_info(row)
        actual = classify_column(column_info, rule_catalog)
        results.append(_compare_result(row, actual))

    elapsed_seconds = time.perf_counter() - started_at
    result_df = pd.DataFrame(results)
    metrics = get_metrics()
    summary = _build_summary(
        result_df=result_df,
        mode=args.mode,
        input_path=args.input,
        rules_path=args.rules,
        elapsed_seconds=elapsed_seconds,
        metrics=metrics,
        match_profile_status=rule_catalog.match_profile_status or {},
    )

    _print_summary(summary, result_df)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result_df.to_csv(output_path, index=False)
        print(f"\nDetail CSV: {output_path}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate column classification against expected labels."
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help="Evaluation CSV with metadata columns and expected_* labels.",
    )
    parser.add_argument(
        "--rules",
        default=str(DEFAULT_RULES),
        help="Rule Excel path.",
    )
    parser.add_argument(
        "--mode",
        choices=sorted(MATCH_PROFILE_MODES),
        default="auto",
        help="First LLM match profile mode.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional per-row evaluation CSV output path.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Only evaluate this many rows after applying --offset.",
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Skip this many rows before evaluation.",
    )
    return parser.parse_args()


def _read_eval_input(input_path):
    df = pd.read_csv(input_path).fillna("")
    required_columns = METADATA_COLUMNS + EXPECTED_COLUMNS
    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]
    if missing_columns:
        raise ValueError(
            "Evaluation input is missing required columns: "
            + ", ".join(missing_columns)
        )

    return df


def _slice_eval_input(df, offset, limit):
    if offset < 0:
        raise ValueError("--offset must be >= 0.")

    if limit is not None and limit < 0:
        raise ValueError("--limit must be >= 0.")

    if limit is None:
        return df.iloc[offset:].copy()

    return df.iloc[offset : offset + limit].copy()


def _column_info(row):
    return {
        column: _clean_value(row[column])
        for column in METADATA_COLUMNS
    }


def _compare_result(row, actual):
    expected_path = _clean_value(row["expected_classification_path"])
    expected_level = _clean_value(row["expected_security_level"])
    expected_review = _to_bool(row["expected_review_required"])
    actual_path = _clean_value(actual.get("classification_path", ""))
    actual_level = _clean_value(actual.get("security_level", ""))
    actual_review = bool(actual.get("review_required", False))

    path_ok = actual_path == expected_path
    level_ok = actual_level == expected_level
    review_ok = actual_review == expected_review

    return {
        "table_name": _clean_value(row["table_name"]),
        "column_name": _clean_value(row["column_name"]),
        "expected_classification_path": expected_path,
        "actual_classification_path": actual_path,
        "expected_security_level": expected_level,
        "actual_security_level": actual_level,
        "expected_review_required": expected_review,
        "actual_review_required": actual_review,
        "path_ok": path_ok,
        "level_ok": level_ok,
        "review_ok": review_ok,
        "all_ok": path_ok and level_ok and review_ok,
        "confidence": actual.get("confidence", 0),
        "failure_reason": actual.get("failure_reason", ""),
        "basis": actual.get("basis", ""),
    }


def _build_summary(
    result_df,
    mode,
    input_path,
    rules_path,
    elapsed_seconds,
    metrics,
    match_profile_status,
):
    total = len(result_df)
    classified = int(result_df["actual_classification_path"].astype(bool).sum())
    review_required = int(result_df["actual_review_required"].sum())

    return {
        "mode": mode,
        "input": input_path,
        "rules": rules_path,
        "match_profile_status": match_profile_status,
        "total": total,
        "classified": classified,
        "review_required": review_required,
        "path_accuracy": _mean(result_df["path_ok"]),
        "level_accuracy": _mean(result_df["level_ok"]),
        "review_accuracy": _mean(result_df["review_ok"]),
        "all_accuracy": _mean(result_df["all_ok"]),
        "first_llm_calls": metrics.get("match_profile_llm_calls", 0),
        "classifier_llm_calls": metrics.get("classifier_llm_calls", 0),
        "elapsed_seconds": round(elapsed_seconds, 2),
    }


def _print_summary(summary, result_df):
    print("Evaluation Summary")
    print(f"mode: {summary['mode']}")
    print(f"input: {summary['input']}")
    print(f"rules: {summary['rules']}")
    print(f"match_profile_status: {summary['match_profile_status']}")
    print(f"total: {summary['total']}")
    print(f"classified: {summary['classified']}")
    print(f"review_required: {summary['review_required']}")
    print(f"path_accuracy: {summary['path_accuracy']:.4f}")
    print(f"level_accuracy: {summary['level_accuracy']:.4f}")
    print(f"review_accuracy: {summary['review_accuracy']:.4f}")
    print(f"all_accuracy: {summary['all_accuracy']:.4f}")
    print(f"first_llm_calls: {summary['first_llm_calls']}")
    print(f"classifier_llm_calls: {summary['classifier_llm_calls']}")
    print(f"elapsed_seconds: {summary['elapsed_seconds']}")

    mismatches = result_df[~result_df["all_ok"]]
    if mismatches.empty:
        print("\nMismatches: 0")
        return

    print(f"\nMismatches: {len(mismatches)}")
    for _, row in mismatches.iterrows():
        print(
            "- {table}.{column}: expected=({expected_path}, {expected_level}, review={expected_review}) "
            "actual=({actual_path}, {actual_level}, review={actual_review}) reason={reason}".format(
                table=row["table_name"],
                column=row["column_name"],
                expected_path=row["expected_classification_path"],
                expected_level=row["expected_security_level"],
                expected_review=row["expected_review_required"],
                actual_path=row["actual_classification_path"],
                actual_level=row["actual_security_level"],
                actual_review=row["actual_review_required"],
                reason=row["failure_reason"],
            )
        )


def _mean(series):
    if len(series) == 0:
        return 0.0

    return float(series.mean())


def _to_bool(value):
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def _clean_value(value):
    return str(value or "").strip()


if __name__ == "__main__":
    main()
