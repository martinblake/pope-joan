"""Entry point for the application."""
import argparse
import sys

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QWidget,
)

from table.board import Board
from table.player import PlayerPanel
from table.scorer import Scorer


def parse_args():
    """Parse and return command line arguments."""
    parser = argparse.ArgumentParser(description="Create Pope Joan session.")
    parser.add_argument("players", nargs="+",
                        help="The names of the players.")
    return parser.parse_args()


class Window(QMainWindow):
    """The application window."""

    def __init__(self, players):
        """Initialise the window."""
        super().__init__()
        self.setWindowTitle("Pope Joan")
        self.setCentralWidget(TableView(players))
        self.show()


class TableView(QWidget):
    """Top level view for game activity."""

    def __init__(self, players):
        """Initialise widgets."""
        super().__init__()
        layout = QGridLayout()

        # Add a title indicating the game state
        self.scorer = Scorer(players)
        self.q_title = QLabel(self.scorer.title)
        self.q_title.setFont(QFont('SansSerif', 16, QFont.Bold))
        layout.addWidget(self.q_title, 0, 0, 1, 2)

        # Add board view
        self.q_board = Board(players, self.game_winner_cb)
        layout.addWidget(self.q_board, 1, 0, 2, 1)

        # Add a panel showing details for each player
        self.q_players = PlayerPanel(players, self.dress, self.drop)
        layout.addWidget(self.q_players, 1, 1)

        # Add a button for completing the round
        self.q_end_round = QPushButton("End Round")
        self.q_end_round.clicked.connect(self.end_round)
        layout.addWidget(self.q_end_round, 2, 1)

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
        self.q_title.setText(self.scorer.title)
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
    window = Window(parse_args().players)
    sys.exit(App.exec())
