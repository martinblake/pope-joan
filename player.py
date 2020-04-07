from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QGroupBox,
    QGridLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class Player(QGroupBox):

    @staticmethod
    def _label(text, font=QFont.Normal):
        label = QLabel(text)
        label.setFont(QFont('SansSerif', 8, font))
        return label

    def __init__(self, name, dress_cb):
        super().__init__(name)
        self.setMaximumHeight(130)
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
        grid.addWidget(self.q_dress, 2, 0, 1, 2)

        self.counters = 50

        self.setLayout(grid)

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


class PlayerPanel(QWidget):

    def __init__(self, players, dress_cb):
        super().__init__()
        layout = QVBoxLayout()

        self.q_players = {}
        for i, name in enumerate(players):
            player = Player(name, partial(dress_cb, name))
            self.q_players[name] = player
            layout.addWidget(player)

        self.setLayout(layout)

    def __getitem__(self, key):
        """Return the requested player widget."""
        return self.q_players[key]

    def clear_round(self):
        """Clear all card counts."""
        for player in self.q_players.values():
            player.q_cards.setText("")

    def __iter__(self):
        """Return iterator through player widgets."""
        return iter(self.q_players.values())
