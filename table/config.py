from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (
    QDialog,
    QGroupBox,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class StartingValue(QGroupBox):
    """A widget for submitting the starting number of counters per player."""

    def __init__(self, on_content_change):
        """Initialise wideget."""
        super().__init__("Starting Value")
        layout = QVBoxLayout()
        self.q_value = QLineEdit()
        self.q_value.setValidator(QIntValidator())
        self.q_value.textChanged.connect(on_content_change)
        layout.addWidget(self.q_value)
        self.setLayout(layout)


class PlayerList(QGroupBox):
    """A widget for naming the players in the game."""

    MAX_PLAYERS = 8

    def __init__(self, on_content_change):
        """Initialise wideget."""
        super().__init__("Players")
        layout = QVBoxLayout()
        self.q_players = [QLineEdit() for _ in range(self.MAX_PLAYERS)]
        for player in self.q_players:
            player.textChanged.connect(on_content_change)
            layout.addWidget(player)
        self.setLayout(layout)


class ConfigView(QDialog):
    """Widget for selecting key configurations."""

    def __init__(self):
        """Initialise widgets"""
        super().__init__()
        self.layout = QVBoxLayout()
        self.setWindowTitle("Configure Game")

        self.q_starting_value = StartingValue(self.on_content_change)
        self.layout.addWidget(self.q_starting_value)

        self.q_player_list = PlayerList(self.on_content_change)
        self.layout.addWidget(self.q_player_list)

        self.q_continue = QPushButton("Continue")
        self.layout.addWidget(self.q_continue)
        self.q_continue.clicked.connect(self.accept)
        self.q_continue.setEnabled(False)

        self.setLayout(self.layout)

    def on_content_change(self, text):
        """Reassess whether the 'continue' button can be enabled."""
        self.q_continue.setEnabled(
            (self.q_starting_value.q_value.text() != "")
            and (len(self.player_list) > 0)
            and (len(self.player_list) == len(set(self.player_list)))
        )

    @property
    def starting_value(self):
        """The number of counters each player should start with."""
        try:
            return int(self.q_starting_value.q_value.text())
        except ValueError:
            return 0

    @property
    def player_list(self):
        """A list of player names."""
        return [p.text() for p in self.q_player_list.q_players if p.text()]
