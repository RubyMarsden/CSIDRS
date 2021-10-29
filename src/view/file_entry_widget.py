from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFileDialog, QTreeWidget, QTreeWidgetItem


class FileEntryWidget(QWidget):
    def __init__(self, model):
        QWidget.__init__(self)
        self.model = model
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.filename_list = QTreeWidget()

        self.filename_list.setHeaderLabel("Imported files")

        self.file_entry_button = QPushButton("Select data files")
        self.file_entry_button.clicked.connect(self.on_file_entry_button_clicked)

        layout.addWidget(self.filename_list)
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
        self.on_filenames_updated()

    def on_filenames_updated(self):
        for filename in self.model.imported_files:
            filename_item = QTreeWidgetItem(self.filename_list)
            filename_item.setText(0,filename)
            #self.filename_list.setItemWidget(filename_item)
