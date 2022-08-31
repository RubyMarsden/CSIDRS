from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout

from view.data_processing_dialog import DataProcessingDialog
from view.file_entry_widget import FileEntryWidget
from view.isotope_button_widget import IsotopeButtonWidget
from view.reference_material_dialog import ReferenceMaterialSelectionDialog

from src.model.isotopes import Isotope


class SidrsWindow(QMainWindow):
    def __init__(self, model):
        QMainWindow.__init__(self)

        self.model = model

        self.signals = self.model.signals

        self.setMinimumSize(QSize(640, 480))
        self.setWindowTitle("CSIDRS v-0.0")

        self.file_entry_widget = FileEntryWidget(model)

        self.setCentralWidget(self.create_main_widget())

        self.signals.dataCleared.connect(self.on_data_cleared)

    def create_main_widget(self):
        main_widget = QWidget()
        title = QLabel("Stable Isotope Data Reduction for CAMECA data")
        title.setAlignment(Qt.AlignCenter)
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_button_clicked)

        self.clear_data_button = QPushButton("Clear all data and methods")
        self.clear_data_button.clicked.connect(self.clear_data_button_clicked)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        button_layout = QHBoxLayout()

        self.file_entry_widget.setDisabled(True)
        self.next_button.setDisabled(True)
        self.clear_data_button.setDisabled(True)

        self.model.signals.materialInput.connect(self.enable_widgets)

        button_layout.addWidget(self.clear_data_button, alignment=Qt.AlignLeft)
        button_layout.addWidget(self.next_button, alignment=Qt.AlignRight)

        main_layout.addWidget(title)
        main_layout.addWidget(IsotopeButtonWidget(self.model))
        main_layout.addWidget(self.file_entry_widget)
        main_layout.addLayout(button_layout)

        return main_widget

    def enable_widgets(self):
        self.file_entry_widget.setEnabled(True)
        self.next_button.setEnabled(True)
        self.clear_data_button.setEnabled(True)

    def next_button_clicked(self):
        self.model.import_all_files(self.file_entry_widget.filenames)
        dialog = ReferenceMaterialSelectionDialog(self.model)
        result = dialog.exec()
        if result:
            dialog.get_selected_reference_material()
            self.on_reference_material_selected()

        return None
        # TODO: Make it go back if no reference material selected and forward to next screen if there is.

    def on_reference_material_selected(self):
        self.model.process_data()
        self.model.drift_correction_process()
        self.model.SIMS_correction_process()
        for isotope in self.model.isotopes:
            if isotope.value == "36S":
                self.model.calculate_cap_values_S36_S33()
        dialog = DataProcessingDialog(self.model)
        result = dialog.exec()

    def clear_data_button_clicked(self):
        self.signals.clearAllData.emit()

    def on_data_cleared(self):
        self.file_entry_widget.setDisabled(True)
        self.next_button.setDisabled(True)
        self.clear_data_button.setDisabled(True)