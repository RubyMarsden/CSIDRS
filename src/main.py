import os
import sys

from PyQt5.QtWidgets import QApplication, QMessageBox

from model.sidrs_model import SidrsModel
from controllers.signals import Signals
from view.sidrs_window import SidrsWindow

def set_except_hook(window):
    def except_hook(cls, exception, traceback):
        sys.__excepthook__(cls, exception, traceback)
        QMessageBox.critical(window, "Error", str(exception))

    sys.excepthook = except_hook


if __name__ == "__main__":
    app = QApplication(sys.argv)
    signals = Signals()

    model = SidrsModel(signals)
    window = SidrsWindow(model)

    # model.isotopes = ["16O", "18O"]
    # model.material = "Zircon"
    #
    # filenames = os.listdir("data/ExampleOdata")
    # full_filenames = ["data/ExampleOdata/" + filename for filename in filenames]
    # model.import_all_files(full_filenames)
    # model.signals.sampleNamesUpdated.emit(model.sample_names)


    set_except_hook(window)
    window.show()

    sys.exit(app.exec())
