import pandas as pd


def analyze_csv(file_path):
    df = pd.read_csv(file_path)

    field_infos = []

    for column in df.columns:
        column_data = df[column]

        data_type = str(column_data.dtype)
        missing_count = int(column_data.isna().sum())
        sample_values = column_data.dropna().head(3).tolist()

        field_info = {
            "field_name": column,
            "data_type": data_type,
            "missing_count": missing_count,
            "sample_values": sample_values
        }

        field_infos.append(field_info)

    return field_infos


if __name__ == "__main__":
    result = analyze_csv("data/sample_users.csv")
    print(result)