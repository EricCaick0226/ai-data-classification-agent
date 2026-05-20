import argparse
import os
import sys
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


def main():
    args = parse_args()
    os.environ["LLM_MATCH_PROFILE_MODE"] = "off"
    sys.path.insert(0, str(SRC_DIR))

    from rules import load_rule_catalog

    eval_df = _read_eval_input(args.input)
    eval_df = _slice_eval_input(
        df=eval_df,
        offset=args.offset,
        limit=args.limit,
    )
    rule_catalog = load_rule_catalog(args.rules)

    rows = []
    for _, row in eval_df.iterrows():
        column_info = _column_info(row)
        candidates = rule_catalog.get_candidate_rules(
            column_info,
            limit=args.candidate_limit,
        )
        rows.append(_compare_candidates(row, candidates))

    result_df = pd.DataFrame(rows)
    summary = _build_summary(
        result_df=result_df,
        input_path=args.input,
        rules_path=args.rules,
        candidate_limit=args.candidate_limit,
    )
    _print_summary(summary, result_df)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        result_df.to_csv(output_path, index=False)
        print(f"\nDetail CSV: {output_path}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evaluate program candidate recall without LLM calls."
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
        "--candidate-limit",
        type=int,
        default=20,
        help="How many candidate rules to recall per column.",
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
    parser.add_argument(
        "--output",
        default=None,
        help="Optional per-row candidate evaluation CSV output path.",
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


def _compare_candidates(row, candidates):
    expected_path = _clean_value(row["expected_classification_path"])
    expected_review = _to_bool(row["expected_review_required"])
    candidate_paths = [
        candidate["classification_path"]
        for candidate in candidates
    ]
    candidate_rank = _candidate_rank(expected_path, candidate_paths)

    return {
        "table_name": _clean_value(row["table_name"]),
        "column_name": _clean_value(row["column_name"]),
        "expected_classification_path": expected_path,
        "expected_review_required": expected_review,
        "candidate_count": len(candidate_paths),
        "candidate_rank": candidate_rank,
        "recall_at_5": _within_rank(candidate_rank, 5),
        "recall_at_10": _within_rank(candidate_rank, 10),
        "recall_at_20": _within_rank(candidate_rank, 20),
        "review_candidate_empty_ok": expected_review and not candidate_paths,
        "top_candidate": candidate_paths[0] if candidate_paths else "",
        "top_5_candidates": " | ".join(candidate_paths[:5]),
    }


def _build_summary(result_df, input_path, rules_path, candidate_limit):
    labeled_df = result_df[result_df["expected_classification_path"].astype(bool)]
    review_df = result_df[result_df["expected_review_required"]]

    return {
        "input": input_path,
        "rules": rules_path,
        "candidate_limit": candidate_limit,
        "total": len(result_df),
        "labeled_total": len(labeled_df),
        "review_expected_total": len(review_df),
        "recall_at_5": _mean(labeled_df["recall_at_5"]),
        "recall_at_10": _mean(labeled_df["recall_at_10"]),
        "recall_at_20": _mean(labeled_df["recall_at_20"]),
        "review_candidate_empty_accuracy": _mean(review_df["review_candidate_empty_ok"]),
        "candidate_miss_count": int((labeled_df["candidate_rank"] == 0).sum()),
    }


def _print_summary(summary, result_df):
    print("Candidate Recall Summary")
    print(f"input: {summary['input']}")
    print(f"rules: {summary['rules']}")
    print(f"candidate_limit: {summary['candidate_limit']}")
    print(f"total: {summary['total']}")
    print(f"labeled_total: {summary['labeled_total']}")
    print(f"review_expected_total: {summary['review_expected_total']}")
    print(f"recall@5: {summary['recall_at_5']:.4f}")
    print(f"recall@10: {summary['recall_at_10']:.4f}")
    print(f"recall@20: {summary['recall_at_20']:.4f}")
    print(
        "review_candidate_empty_accuracy: "
        f"{summary['review_candidate_empty_accuracy']:.4f}"
    )
    print(f"candidate_miss_count: {summary['candidate_miss_count']}")

    misses = result_df[
        result_df["expected_classification_path"].astype(bool)
        & (result_df["candidate_rank"] == 0)
    ]
    if misses.empty:
        print("\nCandidate misses: 0")
        return

    print(f"\nCandidate misses: {len(misses)}")
    for _, row in misses.iterrows():
        print(
            "- {table}.{column}: expected={expected}; top5={top5}".format(
                table=row["table_name"],
                column=row["column_name"],
                expected=row["expected_classification_path"],
                top5=row["top_5_candidates"],
            )
        )


def _candidate_rank(expected_path, candidate_paths):
    if not expected_path:
        return 0

    for index, candidate_path in enumerate(candidate_paths, start=1):
        if candidate_path == expected_path:
            return index

    return 0


def _within_rank(rank, threshold):
    return bool(rank and rank <= threshold)


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
