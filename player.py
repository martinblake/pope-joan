"""Management of per-player info."""
from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QGroupBox,
    QGridLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QWidget,
)


class Player(QGroupBox):
    """A widget for managing player info."""

    @staticmethod
    def _label(text, font=QFont.Normal):
        """Return a label of the default style for this widget."""
        label = QLabel(text)
        label.setFont(QFont('SansSerif', 8, font))
        return label

    def __init__(self, name, dress_cb):
        """Initialise with name and a callback for board dressing."""
        super().__init__(name)
        self.setMaximumHeight(130)
        self.setMinimumWidth(150)
        self.setMaximumWidth(150)
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
        self.q_dress.setFont(QFont('SansSerif', 8, QFont.Normal))
        self.q_dress.clicked.connect(dress_cb)
        grid.addWidget(self.q_dress, 2, 0, 1, 2)

        self.counters = 50

        self.setLayout(grid)

    def setColor(self, color):
        """Set the color palette."""
        pal = self.palette()
        pal.setColor(self.backgroundRole(), color)
        self.setPalette(pal)

    def enable_dressing(self):
        """Enable dressing only."""
        self.q_dress.setEnabled(True)
        self.q_cards.setEnabled(False)
        self.setColor(Qt.green)

    def enable_scoring(self):
        """Enable scoring only."""
        self.q_dress.setEnabled(False)
        self.q_cards.setEnabled(True)

    def disable(self):
        """Disable all inputs."""
        self.q_dress.setEnabled(False)
        self.q_cards.setEnabled(False)
        self.setColor(Qt.lightGray)

    @property
    def counters(self):
        """Get the number of counters."""
        return self.__counters

    @counters.setter
    def counters(self, val):
        """Set the number of counters."""
        self.__counters = val
        self.q_counters.setText(str(self.__counters))
        self.update()

    @property
    def cards(self):
        """Get the number of cards remaining."""
        try:
            return int(self.q_cards.toPlainText())
        except ValueError:
            return 0


class PlayerPanel(QWidget):
    """A panel of widgets for managing player info."""

    N_ROWS = 4

    def __init__(self, players, dress_cb):
        """Initialise from a list of names and board dressing callback."""
        super().__init__()
        layout = QGridLayout()

        self.q_players = {}
        for i, name in enumerate(players):
            player = Player(name, partial(dress_cb, name))
            self.q_players[name] = player
            layout.addWidget(player, i % self.N_ROWS, i // self.N_ROWS)

        self.setLayout(layout)

    def __getitem__(self, key):
        """Return the requested player widget."""
        return self.q_players[key]

    def __iter__(self):
        """Return iterator through player widgets."""
        return iter(self.q_players.values())

    def dressing_phase(self, dresser):
        """Enable only the dresser."""
        for name, player in self.q_players.items():
            if name == dresser:
                player.enable_dressing()
            else:
                player.disable()

    def scoring_phase(self):
        """Enable all player widget inputs except dressing."""
        for name, player in self.q_players.items():
            player.enable_scoring()

    def clear_round(self):
        """Clear all card counts."""
        for player in self.q_players.values():
            player.q_cards.setText("")
