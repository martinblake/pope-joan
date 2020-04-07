"""Entry point for the application."""
import argparse
import sys

from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QMainWindow,
    QPushButton,
    QWidget,
)

from board import Board
from player import PlayerPanel


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
        self.setCentralWidget(GameView(players))
        self.show()


class GameView(QWidget):
    """Top level view for game activity."""

    def __init__(self, players):
        """Initialise widgets."""
        super().__init__()
        layout = QGridLayout()

        # Add board view
        self.q_board = Board(players)
        layout.addWidget(self.q_board, 0, 0, 2, 1)

        # Add a panel showing details for each player
        self.q_players = PlayerPanel(players, self.dress)
        layout.addWidget(self.q_players, 0, 1)

        # Add a button for completing the round
        self.q_end_round = QPushButton("End Round")
        self.q_end_round.clicked.connect(self.end_round)
        layout.addWidget(self.q_end_round, 1, 1)

        self.setLayout(layout)

    def dress(self, player_name):
        """Dress the board using counters from the named player."""
        player = self.q_players[player_name]
        if self.q_board.dress_value <= player.counters:
            player.counters -= self.q_board.dress()

    def end_round(self):
        """Complete counter transactions required at the end of the round."""

        if self.q_board.winner:

            # Game winner gets counters from all other players
            game_winner = self.q_players[self.q_board.winner]
            for player in self.q_players:
                game_winner.counters += player.cards
                player.counters -= player.cards

            # Winners of individual segments get contents
            for segment in self.q_board:
                if segment.winner:
                    player = self.q_players[segment.winner]
                    player.counters += segment.empty()

            # Clear round-specific data inputs
            self.q_board.clear_round()
            self.q_players.clear_round()


if __name__ == '__main__':
    App = QApplication(sys.argv)
    window = Window(parse_args().players)
    sys.exit(App.exec())
