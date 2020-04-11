"""Management of per-player info."""
from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (
    QGroupBox,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from table.scorer import Phase, dress_value
from table.style import adjust_font


class Player(QGroupBox):
    """A widget for managing player info."""

    HEIGHT = 130
    WIDTH = 150

    def __init__(self, name, dress_cb, drop_cb):
        """Initialise with name and a callback for board dressing."""
        super().__init__(name)
        self.name = name
        adjust_font(self, size=10, bold=True)
        self.setAlignment(Qt.AlignCenter)

        self.layout = QGridLayout()
        self._set_geometry(self.layout)

        self.q_counters = adjust_font(QLabel(""), bold=True)
        self.layout.addWidget(adjust_font(QLabel("Count:"), size=8), 0, 0)
        self.layout.addWidget(self.q_counters, 0, 1)

        self.q_cards = adjust_font(QLineEdit())
        self.q_cards.setValidator(QIntValidator())
        self.layout.addWidget(adjust_font(QLabel("Cards:"), size=8), 1, 0)
        self.layout.addWidget(self.q_cards, 1, 1)

        self.q_dress = adjust_font(QPushButton("Dress"))
        self.q_dress.clicked.connect(partial(dress_cb, self))
        self.layout.addWidget(self.q_dress, 2, 0, 1, 2)

        self.q_drop = adjust_font(QPushButton("Go Out"))
        self.layout.addWidget(self.q_drop, 2, 1)
        self.q_drop.clicked.connect(partial(drop_cb, self))
        self.q_drop.hide()

        self.setLayout(self.layout)

    def _set_geometry(self, layout):
        """Set the widget dimensions."""
        self.setMinimumHeight(self.HEIGHT)
        self.setMaximumHeight(self.HEIGHT)
        self.setMinimumWidth(self.WIDTH)
        self.setMaximumWidth(self.WIDTH)
        for col in range(2):
            layout.setColumnMinimumWidth(col, self.WIDTH / 2)
        for row in range(3):
            layout.setRowMinimumHeight(row, self.HEIGHT / 3)

    def set_color(self, color):
        """Set the color palette."""
        pal = self.palette()
        pal.setColor(self.backgroundRole(), color)
        self.setPalette(pal)

    def refresh(self, phase, is_in_game, is_dresser, balance):
        """Refresh the widget based on the game state."""

        # Update player scores
        self.q_counters.setText(str(balance))

        # Clear card counts
        self.q_cards.setText("")

        # Update widget state based on the game phase
        self.setEnabled(is_in_game)
        self.q_dress.setEnabled(is_dresser and (phase == Phase.DRESSING))
        self.q_drop.setEnabled(is_dresser and (phase == Phase.DRESSING))
        self.q_cards.setEnabled(phase == Phase.SCORING)
        can_dress = balance >= dress_value()
        self.set_color(
            Qt.lightGray if not is_in_game
            else (Qt.green if can_dress else Qt.red) if is_dresser
            else (Qt.darkGray if can_dress else Qt.yellow)
        )
        if can_dress:
            self.layout.addWidget(self.q_dress, 2, 0, 1, 2)
            self.q_drop.hide()
        else:
            self.layout.addWidget(self.q_dress, 2, 0)
            self.q_drop.show()

    @property
    def cards(self):
        """Get the number of cards remaining."""
        try:
            return int(self.q_cards.text())
        except ValueError:
            return 0


class PlayerPanel(QWidget):
    """A panel of widgets for managing player info."""

    N_ROWS = 4

    def __init__(self, players, dress_cb, drop_cb):
        """Initialise from a list of names and board dressing callback."""
        super().__init__()
        layout = QGridLayout()

        self.q_players = {}
        for i, name in enumerate(players):
            player = Player(name, dress_cb, drop_cb)
            self.q_players[name] = player
            layout.addWidget(player, i % self.N_ROWS, i // self.N_ROWS)

        self.setLayout(layout)

    def __getitem__(self, key):
        """Return the requested player widget."""
        return self.q_players[key]

    def __iter__(self):
        """Return iterator through player widgets."""
        return iter(self.q_players.values())

    def refresh(self, phase, players, dresser, balance):
        """Refresh the player score displays based on the game state."""

        for name, player in self.q_players.items():
            player.refresh(phase,
                           name in players,
                           name == dresser,
                           balance[name])
