import csv

CSV_DELIMITER = ","


def write_csv_output(headers, rows, output_file) -> None:
    with open(output_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=CSV_DELIMITER, quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)
