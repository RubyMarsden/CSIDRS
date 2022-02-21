from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFileDialog, QTreeWidget, QTreeWidgetItem, \
    QVBoxLayout

from src.view.change_sample_names_dialog import ChangeSampleNamesDialog


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

        self.sample_name_list = QTreeWidget()
        self.sample_name_list.setHeaderLabel("Sample names")

        self.remove_single_file_button = QPushButton("Remove file")
        self.remove_single_file_button.clicked.connect(self.on_remove_single_file_button_clicked)

        self.manual_sample_names_button = QPushButton("Change sample names")
        self.manual_sample_names_button.clicked.connect(self.on_change_sample_names_button_clicked)

        lhs_layout = QVBoxLayout()
        lhs_layout.addWidget(self.filename_list)
        lhs_layout.addWidget(self.remove_single_file_button)

        layout.addLayout(lhs_layout)

        rhs_layout = QVBoxLayout()

        rhs_layout.addWidget(self.file_entry_button)
        rhs_layout.addWidget(self.sample_name_list)
        rhs_layout.addWidget(self.manual_sample_names_button)

        layout.addLayout(rhs_layout)

        self.model.signals.dataCleared.connect(self.on_data_cleared)

        #############
        ## Actions ##
        #############

    def on_file_entry_button_clicked(self):
        filenames, _ = QFileDialog.getOpenFileNames(self,
                                                    "Select files",
                                                    "home/ruby/Documents/Programming/UWA/CSIDRS/data",
                                                    "ASCII files (*.asc)"
                                                    )
        self.model.import_all_files(filenames)
        self.on_filenames_updated()

    def on_filenames_updated(self):
        for filename in self.model.imported_files:
            filename_item = QTreeWidgetItem(self.filename_list)
            filename_item.setText(0, filename)

        for sample_name in self.model.list_of_sample_names:
            sample_name_item = QTreeWidgetItem(self.sample_name_list)
            sample_name_item.setText(0, sample_name)

        self.filename_list.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.filename_list.horizontalScrollBar().setEnabled(True)
        self.filename_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.filename_list.header().setStretchLastSection(False)

    def on_change_sample_names_button_clicked(self):
        dialog = ChangeSampleNamesDialog(self.model.list_of_sample_names)
        result = dialog.exec()
        if result:
            sample_names = dialog.sample_names
            self.model.signals.sampleNamesUpdated.emit(sample_names)
        return sample_names

    def on_remove_single_file_button_clicked(self):
        print("remove file")

    def on_data_cleared(self):
        self.filename_list.clear()
        self.sample_name_list.clear()
