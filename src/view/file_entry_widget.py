import os.path

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QFileDialog, QTreeWidget, QTreeWidgetItem, \
    QVBoxLayout

from view.change_sample_names_dialog import ChangeSampleNamesDialog


class FileEntryWidget(QWidget):
    def __init__(self, model):
        QWidget.__init__(self)
        self.model = model

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.filename_tree_widget = QTreeWidget()
        self.filename_tree_widget.setHeaderLabel("Imported files")

        self.file_entry_button = QPushButton("Select data files")
        self.file_entry_button.clicked.connect(self.on_file_entry_button_clicked)

        self.sample_name_tree_widget = QTreeWidget()
        self.sample_name_tree_widget.setHeaderLabel("Sample names")

        self.remove_single_file_button = QPushButton("Remove file")
        self.remove_single_file_button.clicked.connect(self.on_remove_single_file_button_clicked)

        self.manual_sample_names_button = QPushButton("Change sample names")
        self.manual_sample_names_button.clicked.connect(self.on_change_sample_names_button_clicked)

        lhs_layout = QVBoxLayout()
        lhs_layout.addWidget(self.filename_tree_widget)
        lhs_layout.addWidget(self.remove_single_file_button)

        layout.addLayout(lhs_layout)

        rhs_layout = QVBoxLayout()

        rhs_layout.addWidget(self.file_entry_button)
        rhs_layout.addWidget(self.sample_name_tree_widget)
        rhs_layout.addWidget(self.manual_sample_names_button)

        layout.addLayout(rhs_layout)

        self.model.signals.dataCleared.connect(self.on_data_cleared)
        self.model.signals.importedFilesUpdated.connect(self.on_imported_files_updated)
        self.model.signals.sampleNamesUpdated.connect(self.on_samples_names_updated)

        #############
        ## Actions ##
        #############

    def on_file_entry_button_clicked(self):
        filenames, _ = QFileDialog.getOpenFileNames(self,
                                                    "Select files",
                                                    "home",
                                                    "ASCII files (*.asc)"
                                                    )
        if filenames:
            self.model.import_all_files(filenames)

    def on_imported_files_updated(self):
        for filename in self.model.imported_files:
            base_name = os.path.basename(filename)
            filename_item = QTreeWidgetItem(self.filename_tree_widget)
            filename_item.setText(0, base_name)

        self.filename_tree_widget.header().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.filename_tree_widget.horizontalScrollBar().setEnabled(True)
        self.filename_tree_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.filename_tree_widget.header().setStretchLastSection(False)

    def on_change_sample_names_button_clicked(self):
        sample_names = [sample.name for sample in self.model.get_samples()]
        dialog = ChangeSampleNamesDialog(sample_names)
        result = dialog.exec()
        if result:
            merge_operations = dialog.merges
            rename_operations = dialog.simple_renames
            self.model.rename_and_merge_samples(rename_operations, merge_operations)
        return sample_names

    def on_remove_single_file_button_clicked(self):
        print("remove file")

    def on_data_cleared(self):
        self.filename_tree_widget.clear()
        self.sample_name_tree_widget.clear()

    def on_samples_names_updated(self):
        self.sample_name_tree_widget.clear()
        for sample in self.model.get_samples():
            sample_name_item = QTreeWidgetItem(self.sample_name_tree_widget)
            sample_name_item.setText(0, sample.name)
