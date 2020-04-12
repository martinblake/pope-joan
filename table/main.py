"""Entry point for the application."""
import sys

from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QGridLayout,
    QGroupBox,
    QMainWindow,
    QPushButton,
)

from table.board import Board
from table.config import ConfigView
from table.player import PlayerPanel
from table.scorer import Scorer


class Window(QMainWindow):
    """The application window."""

    def __init__(self, starting_value, players):
        """Initialise the window."""
        super().__init__()
        self.setWindowTitle("Pope Joan")

        self.setCentralWidget(
            TableView(starting_value, players)
        )
        self.show()


class TableView(QGroupBox):
    """Top level view for game activity."""

    def __init__(self, starting_value, players):
        """Initialise widgets."""
        self.scorer = Scorer(starting_value, players)
        super().__init__(self.scorer.title)
        layout = QGridLayout()

        # Add board view
        self.q_board = Board(players, self.game_winner_cb)
        layout.addWidget(self.q_board, 0, 0, 2, 1)

        # Add a panel showing details for each player
        self.q_players = PlayerPanel(players, self.dress, self.drop)
        layout.addWidget(self.q_players, 0, 1)

        # Add a button for completing the round
        self.q_end_round = QPushButton("End Round")
        self.q_end_round.clicked.connect(self.end_round)
        layout.addWidget(self.q_end_round, 1, 1)

        self.setLayout(layout)

        # Initial state
        self.refresh_display()

    def dress(self, player):
        """Dress the board using counters from the given player."""
        self.scorer.log_dress(player.name)
        self.refresh_display()

    def drop(self, player):
        """Drop the given player from the game."""
        self.scorer.drop(player.name)
        self.refresh_display()

    def game_winner_cb(self, name):
        """
        Only enable the 'End Round' button once the game winner is selected.
        """
        self.q_end_round.setEnabled(name != "")

    def end_round(self):
        """Complete counter transactions required at the end of the round."""

        # Log scores and update views
        self.scorer.log_round(
            {name: seg.q_player.currentText()
             for name, seg in self.q_board.q_segments.items()},
            {p.name: p.cards for p in self.q_players}
        )
        self.refresh_display()

    def refresh_display(self):
        """Refresh all displayed info from the scorer."""
        self.setTitle(self.scorer.title)
        self.q_board.refresh(self.scorer.phase,
                             self.scorer.players,
                             self.scorer.balance.segments)
        self.q_players.refresh(self.scorer.phase,
                               self.scorer.players,
                               self.scorer.dresser,
                               self.scorer.balance.players)
        self.q_end_round.setEnabled(False)


if __name__ == '__main__':
    App = QApplication(sys.argv)
    App.setStyle("Fusion")
    config = ConfigView()
    if config.exec_() == QDialog.Accepted:
        window = Window(config.starting_value, config.player_list)
        sys.exit(App.exec())
