from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QFileDialog


class FileEntryWidget(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        layout = QHBoxLayout()
        self.setLayout(layout)

        label = QLabel("File entry goes here")

        self.file_entry_button = QPushButton("Select data files")
        self.file_entry_button.clicked.connect(self.on_file_entry_button_clicked)

        layout.addWidget(label)
        layout.addWidget(self.file_entry_button)

        #############
        ## Actions ##
        #############

    def on_file_entry_button_clicked(self):
        filenames, _ = QFileDialog.getOpenFileNames()
        # model needs to do the importing
        # self.model.import_samples(filenames)
        if filenames:
            for filename in filenames:
                print(filename)

