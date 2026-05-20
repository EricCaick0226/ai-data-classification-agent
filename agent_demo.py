from pathlib import Path
import importlib.util
import subprocess
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

    print(
        "[Setup] Missing packages for current python3: "
        + ", ".join(missing_packages)
    )
    print("[Setup] Installing with current interpreter...")
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            *missing_packages,
        ]
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
