from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
DEFAULT_INPUT = PROJECT_ROOT / "data" / "sample_column_metadata.csv"
DEFAULT_RULES = Path("/Users/ericcai/Desktop/internfiles/分类分级标准.xlsx")
DEFAULT_OUTPUT = PROJECT_ROOT / "reports" / "classification_report.md"

sys.path.insert(0, str(SRC_DIR))

from agent_demo import run_agent  # noqa: E402


def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_INPUT)
    rules_path = sys.argv[2] if len(sys.argv) > 2 else str(DEFAULT_RULES)
    output_path = sys.argv[3] if len(sys.argv) > 3 else str(DEFAULT_OUTPUT)

    run_agent(
        input_path=input_path,
        rules_path=rules_path,
        output_path=output_path,
    )


if __name__ == "__main__":
    main()
