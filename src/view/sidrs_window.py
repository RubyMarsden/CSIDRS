from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QDialog
from PyQt5.QtCore import Qt, QSize

from src.view.isotope_button_widget import IsotopeButtonWidget
from src.view.file_entry_widget import FileEntryWidget
from src.view.reference_material_dialog import ReferenceMaterialSelectionDialog


class SidrsWindow(QMainWindow):
    def __init__(self, model):
        QMainWindow.__init__(self)

        self.model = model

        self.setMinimumSize(QSize(640, 480))
        self.setWindowTitle("SIDRS v-0.0")

        self.file_entry_widget = FileEntryWidget(model)

        self.setCentralWidget(self.create_main_widget())

    def create_main_widget(self):
        main_widget = QWidget()
        title = QLabel("Stable Isotope Data Reduction for CAMECA data")
        title.setAlignment(Qt.AlignCenter)
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_button_clicked)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        self.file_entry_widget.setDisabled(True)
        self.next_button.setDisabled(True)

        self.model.signals.materialInput.connect(self.enable_widgets)

        main_layout.addWidget(title)
        main_layout.addWidget(IsotopeButtonWidget(self.model))
        main_layout.addWidget(self.file_entry_widget)
        main_layout.addWidget(self.next_button, alignment=Qt.AlignRight)

        return main_widget

    def enable_widgets(self):
        self.file_entry_widget.setEnabled(True)
        self.next_button.setEnabled(True)

    def next_button_clicked(self):
        element = self.model.element
        material = self.model.material
        dialog = ReferenceMaterialSelectionDialog(element, material)
        result = dialog.exec()
        if result == QDialog.Accepted:
            return dialog.get_selected_reference_material()
        return None
        # TODO: Make it go back if no reference material selected and forward to next screen if there is.

