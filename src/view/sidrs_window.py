from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, QLineEdit, QSpinBox, \
    QMessageBox

from controllers.signals import signals
from view.data_processing_dialog import DataProcessingDialog
from view.file_entry_widget import FileEntryWidget
from view.isotope_button_widget import IsotopeButtonWidget
from view.reference_material_dialog import ReferenceMaterialSelectionDialog


class SidrsWindow(QMainWindow):
    def __init__(self, model):
        QMainWindow.__init__(self)

        self.model = model

        self.setMinimumSize(QSize(640, 480))
        self.setWindowTitle("CSIDRS v-1.1.0")

        self.file_entry_widget = FileEntryWidget(model)

        self.setCentralWidget(self.create_main_widget())

        signals.dataCleared.connect(self.on_data_cleared)

    def create_main_widget(self):
        main_widget = QWidget()
        title = QLabel("Stable Isotope Data Reduction for CAMECA data")
        title.setAlignment(Qt.AlignCenter)
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_button_clicked)

        self.clear_data_button = QPushButton("Clear all data and methods")
        self.clear_data_button.clicked.connect(self.clear_data_button_clicked)

        self.montecarlo_number_input = QSpinBox()
        self.montecarlo_number_input.setMinimum(1)
        self.montecarlo_number_input.setMaximum(1000000000)
        self.montecarlo_number_input.setValue(10000)
        montecarlo_text = QLabel("Number of trials for Monte Carlo distributions:")

        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        button_layout = QHBoxLayout()

        self.file_entry_widget.setDisabled(True)
        self.next_button.setDisabled(True)
        self.clear_data_button.setDisabled(True)

        self.montecarlo_number_input.setDisabled(True)

        signals.materialInput.connect(self.enable_widgets)

        button_layout.addWidget(self.clear_data_button, alignment=Qt.AlignLeft)
        button_layout.addWidget(self.next_button, alignment=Qt.AlignRight)

        montecarlo_layout = QHBoxLayout()
        montecarlo_layout.addWidget(montecarlo_text)
        montecarlo_layout.addWidget(self.montecarlo_number_input)

        main_layout.addWidget(title)
        main_layout.addWidget(IsotopeButtonWidget(self.model))
        main_layout.addWidget(self.file_entry_widget)
        main_layout.addLayout(montecarlo_layout)
        main_layout.addLayout(button_layout)

        return main_widget

    def enable_widgets(self):
        self.file_entry_widget.setEnabled(True)
        self.next_button.setEnabled(True)
        self.clear_data_button.setEnabled(True)
        self.montecarlo_number_input.setEnabled(True)

    def next_button_clicked(self):
        popup = QMessageBox()

        popup.setWindowTitle('Monte Carlo warning')
        if self.montecarlo_number_input.value() < 1000:
            popup.setText('Less than 1000 trials leads to high variance in the mean and standard deviation of results.')
            popup.exec()
        elif self.montecarlo_number_input.value() > 1000000:
            popup.setText('More than 1000000 trials will cause significant memory usage and the program may crash.')
            popup.exec()
        dialog = ReferenceMaterialSelectionDialog(self.model)
        result = dialog.exec()
        if result:
            dialog.get_selected_reference_material()
            self.on_reference_material_selected()

        return None

    def on_reference_material_selected(self):
        montecarlo_number = self.montecarlo_number_input.value()
        self.model.set_montecarlo_number(montecarlo_number)
        self.model.calculate_results()
        dialog = DataProcessingDialog(self.model)
        dialog.exec()

    def clear_data_button_clicked(self):
        self.model.clear_all_data_and_methods()

    def on_data_cleared(self):
        self.file_entry_widget.setDisabled(True)
        self.next_button.setDisabled(True)
        self.clear_data_button.setDisabled(True)