import csv

from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QFileDialog

CSV_DELIMITER = ","


def write_csv_output(headers, rows, output_file) -> None:
    with open(output_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=CSV_DELIMITER, quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)

def get_output_file(save_filename):
    directory = QDir.currentPath()
    return QFileDialog.getSaveFileName(caption='Save CSV file',
                                       directory=str(directory + "/" + save_filename + ".csv"),
                                       filter=".csv",
                                       options=QFileDialog.DontUseNativeDialog
                                       )[0]
