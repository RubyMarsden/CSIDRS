from collections import defaultdict

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox, QMessageBox


class ChangeSampleNamesDialog(QDialog):
    def __init__(self, sample_names):
        QDialog.__init__(self)

        self.setWindowTitle("Change sample names")
        self.setMinimumWidth(450)
        self.input_box_list = []
        self.merges = None
        self.simple_renames = None
        self.original_names = sample_names

        layout = QVBoxLayout()

        for sample_name in sample_names:
            input_box = QLineEdit(sample_name)
            self.input_box_list.append(input_box)

            layout.addWidget(input_box)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.on_accept_button_clicked)
        self.buttonBox.rejected.connect(self.reject)

        layout.addWidget(self.buttonBox)

        self.setLayout(layout)

    def on_accept_button_clicked(self):
        new_names = [input_box.text() for input_box in self.input_box_list]

        new_names_mapped_to_old_names = defaultdict(list)

        for new_name, old_name in zip(new_names, self.original_names):
            new_names_mapped_to_old_names[new_name].append(old_name)

        merged_sample_names = []
        simple_renames = []
        for new_name, old_names in new_names_mapped_to_old_names.items():
            if len(old_names) > 1:
                merged_sample_names.append((new_name, old_names))
            elif new_name != old_names[0]:
                simple_renames.append((old_names[0], new_name))

        if len(merged_sample_names) > 0:
            # show a popup box - YES NO DIALOG shortcut
            merge_strings = []
            for new_name, old_names in merged_sample_names:
                merge_strings.append("    " + ", ".join(old_names) + " into " + new_name)
            merge_message = "\n".join(merge_strings)
            message = "This operation will merge the following samples:\n\n" + merge_message + "\n\n"\
                        "This cannot be undone without deleting and reimporting the files. \n \n " \
                        "Would you like to proceed?"
            approve_merge_answer = QMessageBox.question(self,
                                                        "Merge warning",
                                                        message,
                                                        buttons=QMessageBox.Yes | QMessageBox.No,
                                                        defaultButton=QMessageBox.No)
            if approve_merge_answer == QMessageBox.No:
                return

        self.merges = merged_sample_names
        self.simple_renames = simple_renames
        self.accept()
