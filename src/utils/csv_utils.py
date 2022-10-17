import csv

from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QFileDialog, QMessageBox

CSV_DELIMITER = ","


def export_csv(parent, default_filename, headers, rows):
    filename = request_output_csv_filename_from_user(default_filename)
    if not filename:
        return

    write_csv_output(filename, headers, rows)
    csv_exported_successfully_popup(parent, filename)


def write_csv_output(output_file, headers, rows) -> None:
    with open(output_file, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=CSV_DELIMITER, quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)


def request_output_csv_filename_from_user(default_filename):
    directory = QDir.currentPath()
    return QFileDialog.getSaveFileName(caption='Save CSV file',
                                       directory=str(directory + "/" + default_filename + ".csv"),
                                       filter=".csv",
                                       options=QFileDialog.DontUseNativeDialog
                                       )[0]


def csv_exported_successfully_popup(parent, csv_filename):
    title = "Success!"
    text = "CSV file '%s' has been exported successfully." % csv_filename

    QMessageBox.information(parent, title, text)
