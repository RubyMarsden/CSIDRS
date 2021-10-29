from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFileDialog, QTreeWidget, QTreeWidgetItem


class FileEntryWidget(QWidget):
    def __init__(self, model):
        QWidget.__init__(self)
        self.model = model
        layout = QHBoxLayout()
        self.setLayout(layout)

        filename_list = QTreeWidget()

        for filename in self.model.imported_files:
            filename_item = QTreeWidgetItem(filename_list, filename)

        self.file_entry_button = QPushButton("Select data files")
        self.file_entry_button.clicked.connect(self.on_file_entry_button_clicked)

        layout.addWidget(filename_list)
        layout.addWidget(self.file_entry_button)

        #############
        ## Actions ##
        #############

    def on_file_entry_button_clicked(self):
        filenames, _ = QFileDialog.getOpenFileNames(self,
                                                    "Select files",
                                                    "home/ruby/Documents/Programming/UWA/SIDRS/data",
                                                    "ASCII files (*.asc)"
                                                    )
        # model needs to do the importing
        self.model.import_all_files(filenames)
