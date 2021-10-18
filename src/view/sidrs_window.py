from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton
from PyQt5.QtCore import Qt, QSize

from src.view.isotope_button_widget import IsotopeButtonWidget
from src.view.file_entry_widget import FileEntryWidget
from src.view.reference_material_dialog import ReferenceMaterialSelectionDialog


class SidrsWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(640, 480))
        self.setWindowTitle("SIDRS v-0.0")

        self.setCentralWidget(self.create_main_widget())

    def create_main_widget(self):
        main_widget = QWidget()
        title = QLabel("Stable Isotope Data Reduction for CAMECA data")
        title.setAlignment(Qt.AlignCenter)
        next_button = QPushButton("Next")
        next_button.clicked.connect(self.next_button_clicked)
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)

        main_layout.addWidget(title)
        main_layout.addWidget(IsotopeButtonWidget())
        main_layout.addWidget(FileEntryWidget())
        main_layout.addWidget(next_button, alignment=Qt.AlignRight)

        return main_widget

    def next_button_clicked(self):
        isotope = "s"
        dialog = ReferenceMaterialSelectionDialog(isotope)
        result = dialog.exec()
