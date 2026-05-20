from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "table_name",
    "column_name",
    "column_type",
    "column_description",
]

COLUMN_ALIASES = {
    "表名": "table_name",
    "字段名": "column_name",
    "字段类型": "column_type",
    "字段描述": "column_description",
    "列名": "column_name",
    "列类型": "column_type",
    "列描述": "column_description",
}


def read_column_metadata(file_path, sheet_name=None):
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Column metadata file not found: {file_path}")

    if path.suffix.lower() == ".csv":
        df = pd.read_csv(path)
    elif path.suffix.lower() in {".xlsx", ".xls"}:
        try:
            df = pd.read_excel(path, sheet_name=sheet_name or 0)
        except ImportError as exc:
            raise RuntimeError(
                "Reading column metadata Excel files requires openpyxl. "
                "Use the project virtual environment: "
                "source .venv/bin/activate, or run with .venv/bin/python."
            ) from exc
    else:
        raise ValueError("Column metadata input must be a CSV or Excel file.")

    df = _normalize_columns(df)
    _validate_required_columns(df)

    column_infos = []
    for _, row in df.iterrows():
        column_info = {
            "table_name": _clean_value(row.get("table_name")),
            "column_name": _clean_value(row.get("column_name")),
            "column_type": _clean_value(row.get("column_type")),
            "column_description": _clean_value(row.get("column_description")),
        }

        if not any(column_info.values()):
            continue

        for column in df.columns:
            if column not in column_info:
                column_info[column] = _clean_value(row.get(column))

        column_infos.append(column_info)

    return column_infos


def _normalize_columns(df):
    renamed_columns = {}
    for column in df.columns:
        normalized = str(column).strip()
        renamed_columns[column] = COLUMN_ALIASES.get(normalized, normalized)

    return df.rename(columns=renamed_columns)


def _validate_required_columns(df):
    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]
    if missing_columns:
        raise ValueError(
            "Column metadata file is missing required columns: "
            + ", ".join(missing_columns)
        )


def _clean_value(value):
    if pd.isna(value):
        return ""

    return str(value).strip()


if __name__ == "__main__":
    print(read_column_metadata("data/sample_column_metadata.csv"))
