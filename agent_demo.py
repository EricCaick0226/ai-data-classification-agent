from pathlib import Path
import importlib.util
import sys


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

sys.path.insert(0, str(SRC_DIR))

REQUIRED_PACKAGES = {
    "pandas": "pandas",
    "openpyxl": "openpyxl",
    "openai": "openai",
    "httpx": "httpx",
}


def ensure_dependencies():
    missing_packages = [
        package_name
        for import_name, package_name in REQUIRED_PACKAGES.items()
        if importlib.util.find_spec(import_name) is None
    ]

    if not missing_packages:
        return

    missing_list = ", ".join(missing_packages)
    raise SystemExit(
        "[Setup] Missing required packages for current Python: "
        f"{missing_list}\n"
        "[Setup] Install dependencies in your project environment first:\n"
        "  python -m pip install -r requirements.txt"
    )


ensure_dependencies()

from agent_runner import parse_args, resolve_paths, run_agent  # noqa: E402


def main():
    args = parse_args()
    input_path, rules_path, output_path = resolve_paths(args)
    run_agent(
        input_path=input_path,
        rules_path=rules_path,
        output_path=output_path,
    )


if __name__ == "__main__":
    main()
