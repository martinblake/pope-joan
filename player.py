from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QGroupBox,
    QGridLayout,
    QLabel,
    QPushButton,
    QTextEdit,
)


class Player(QGroupBox):

    @staticmethod
    def _label(text, font=QFont.Normal):
        label = QLabel(text)
        label.setFont(QFont('SansSerif', 8, font))
        return label

    def __init__(self, parent, name, dress_cb):
        super().__init__(name, parent)
        self.setGeometry(0, 0, 150, 130)
        self.setFont(QFont('SansSerif', 10, QFont.Bold))
        self.setAlignment(Qt.AlignCenter)

        grid = QGridLayout(self)
        grid.addWidget(self._label("Count:"), 0, 0)
        grid.addWidget(self._label("Cards:"), 1, 0)

        self.q_counters = self._label("", font=QFont.Bold)
        self.q_cards = QTextEdit()
        grid.addWidget(self.q_counters, 0, 1)
        grid.addWidget(self.q_cards, 1, 1)

        self.q_dress = QPushButton("Dress")
        self.q_dress.clicked.connect(dress_cb)
        grid.addWidget(self.q_dress, 2, 0)

        self.counters = 50

        self.setLayout(grid)

    def move(self, x, y):
        w = self.rect().width()
        h = self.rect().height()
        super().move(x - w / 2, y - h / 2)

    @property
    def counters(self):
        return self.__counters

    @counters.setter
    def counters(self, val):
        self.__counters = val
        self.q_counters.setText(str(self.__counters))
        self.update()

    @property
    def cards(self):
        return int(self.q_cards.toPlainText())
