from PyQt5.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


def create_figure_widget(fig, parent):
    canvas = FigureCanvas(fig)
    toolbar = NavigationToolbar(canvas, parent)

    layout = QVBoxLayout()
    layout.setContentsMargins(2, 2, 2, 2)
    layout.addWidget(canvas)
    layout.addWidget(toolbar)

    widget = QWidget()
    widget.setLayout(layout)
    return widget, canvas
