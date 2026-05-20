from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

from agent_demo import parse_args, run_agent  # noqa: E402


def main():
    args = parse_args()
    run_agent(
        input_path=args.input,
        rules_path=args.rules,
        output_path=args.output,
    )


if __name__ == "__main__":
    main()
