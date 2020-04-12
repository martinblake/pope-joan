"""Management of per-player info."""
from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from table.scorer import Phase, dress_value


class Player(QGroupBox):
    """A widget for managing player info."""

    def __init__(self, name, dress_cb, drop_cb):
        """Initialise with name and a callback for board dressing."""
        super().__init__(name)
        self.name = name
        self.setAlignment(Qt.AlignCenter)

        layout = QFormLayout()

        self.count = QLabel("")
        layout.addRow("Count:", self.count)

        self.cards = QLineEdit()
        self.cards.setValidator(QIntValidator())
        layout.addRow("Cards:", self.cards)

        self.dress = QPushButton("Dress")
        self.dress.clicked.connect(partial(dress_cb, self))
        self.drop = QPushButton("Go Out")
        self.drop.clicked.connect(partial(drop_cb, self))
        self.drop.hide()
        buttons = QHBoxLayout()
        buttons.addWidget(self.dress)
        buttons.addWidget(self.drop)
        layout.setLayout(2, QFormLayout.SpanningRole, buttons)

        self.setLayout(layout)

    def set_color(self, color):
        """Set the color palette."""
        pal = self.palette()
        pal.setColor(self.backgroundRole(), color)
        self.setPalette(pal)

    def refresh(self, phase, is_in_game, is_dresser, balance):
        """Refresh the widget based on the game state."""

        # Update player scores
        self.count.setText(str(balance))

        # Clear card counts
        self.cards.setText("")

        # Update widget state based on the game phase
        self.setEnabled(is_in_game)
        self.dress.setEnabled(is_dresser and (phase == Phase.DRESSING))
        self.drop.setEnabled(is_dresser and (phase == Phase.DRESSING))
        self.cards.setEnabled(phase == Phase.SCORING)
        can_dress = balance >= dress_value()
        self.set_color(
            Qt.lightGray if not is_in_game
            else (Qt.green if is_dresser else Qt.darkGray) if can_dress
            else (Qt.red if is_dresser and (phase == Phase.DRESSING)
                  else Qt.yellow)
        )
        if can_dress:
            self.drop.hide()
        else:
            self.drop.show()

    @property
    def cards_left(self):
        """Get the number of cards remaining."""
        try:
            return int(self.cards.text())
        except ValueError:
            return 0


class PlayerPanel(QWidget):
    """A panel of widgets for managing player info."""

    N_ROWS = 4

    def __init__(self, players, dress_cb, drop_cb):
        """Initialise from a list of names and board dressing callback."""
        super().__init__()
        layout = QGridLayout()

        self.players = {}
        for i, name in enumerate(players):
            player = Player(name, dress_cb, drop_cb)
            self.players[name] = player
            row = 2 * (i % self.N_ROWS)
            col = (i // self.N_ROWS)
            layout.addWidget(player, row, col)
            layout.setRowStretch(row + 1, 1)

        self.setLayout(layout)

    def __getitem__(self, key):
        """Return the requested player widget."""
        return self.players[key]

    def __iter__(self):
        """Return iterator through player widgets."""
        return iter(self.players.values())

    def refresh(self, phase, players, dresser, balance):
        """Refresh the player score displays based on the game state."""

        for name, player in self.players.items():
            player.refresh(phase,
                           name in players,
                           name == dresser,
                           balance[name])
