from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

from reactive_qt.core import render_diff

layout0 = []

layout1  = [{'component': 'button',
             'text': 'submit!!',
             'id': 5678},
            {'component': 'label',
             'text': 'sal',
             'id': 5679},
            {'component': 'label',
             'text': 'abby',
             'id': 5680},
            {'component': 'label',
             'text': 'bailey',
             'id': 5681},
            {'component': 'button',
             'text': 'i shall be removed',
             'id': 5667},
            {'component': 'button',
             'text': 'i am going to move and change',
             'id': 7777},
            {'component': 'vbox',
             'id': 9876,
             'contains': [
                 {'component': 'label',
                  'text': 'inner',
                  'id': 8765
                 }
             ]}]

layout2  = [{'component': 'button',
             'text': 'submit',
             'id': 5678},
            {'component': 'label',
             'text': 'hello i am new',
             'id': 1234},
            {'component': 'label',
             'text': 'sal',
             'id': 5679},
            {'component': 'label',
             'text': 'bailey',
             'id': 5681},
            {'component': 'label',
             'text': 'abby',
             'id': 5680},
            {'component': 'vbox',
             'id': 9876,
             'contains': [
                 {'component': 'label',
                  'text': 'inner',
                  'id': 8765
                 },
                 {'component': 'button',
                  'text': 'i am going to move and change!',
                  'id': 7777},
             ]}]


class AppWindow(QWidget):
    def __init__(self, layouts, elements):
        super().__init__()
        self.layouts = layouts
        self.current_layout_ix = 0
        self.elements = elements

    def next_layout(self):
        current = self.layouts[self.current_layout_ix]

        self.current_layout_ix = (self.current_layout_ix + 1) \
                                 % len(self.layouts)

        nxt = self.layouts[self.current_layout_ix]

        self.elements = render_diff(
            {'contains': current, 'id': 0},
            {'contains': nxt, 'id': 0},
            self.elements)

    def prev_layout(self):
        current = self.layouts[self.current_layout_ix]

        self.current_layout_ix = (self.current_layout_ix - 1) \
                                 % len(self.layouts)

        nxt = self.layouts[self.current_layout_ix]

        self.elements = render_diff({'contains': current, 'id': 0},
                                    {'contains': nxt, 'id': 0},
                                    self.elements)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Q:
            self.close()
        elif e.key() == Qt.Key_Comma:
            self.next_layout()
        elif e.key() == Qt.Key_Period:
            self.prev_layout()

app = QApplication([])
window = QWidget()
vbox = QVBoxLayout()

appwindow = AppWindow([layout0, layout1, layout2], {0: vbox})

appwindow.setLayout(vbox)
appwindow.show()
app.exec_()
