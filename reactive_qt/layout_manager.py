from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QObject
from reactive_qt.core import render_diff

# it's a simple handler for managing the call to
# reactive_qt.render_diff() (basically, it just keeps the current
# layout in state, since the call to render_diff is stateless)
class StatefulReactiveQtAppWindow(QWidget):

    # A signal to hit when the layout changes, so we can be sure to
    # run the layout mutations in the UI thread
    layout_changed = pyqtSignal(object)

    def __init__(self, initial_layout=[], initial_elements={}):
        super().__init__()
        self.elements = initial_elements
        self.current_layout = initial_layout
        self.layout_changed.connect(self.next_layout)

    @pyqtSlot(object)
    def next_layout(self, layout):
        self.elements = render_diff(
            self.current_layout,
            layout,
            self.elements)

        self.current_layout = layout
