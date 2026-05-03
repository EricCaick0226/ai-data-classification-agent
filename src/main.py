from csv_analyzer import analyze_csv
from classifier import classify_column
from report_generator import generate_report


def main():
    file_path = "data/sample_users.csv"

    print("Starting rule-based classification pipeline...")
    print(f"Reading CSV file: {file_path}")
    column_infos = analyze_csv(file_path)
    print(f"Found {len(column_infos)} fields in the CSV file.")
    classification_results = []

    for column_info in column_infos:
        result = classify_column(column_info)
        classification_results.append(result)

    print(f"Classified {len(classification_results)} fields.")
    
    report_path = generate_report(classification_results)

    print(f"Report generated successfully: {report_path}")
    print("Pipeline finished.")

if __name__ == "__main__":
    main()