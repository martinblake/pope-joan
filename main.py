"""Entry point for the application."""
import argparse
import sys

from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsView,
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

    RADIUS = 300  # Board radius

    def __init__(self, players):
        """Initialise widgets."""
        super().__init__()
        layout = QGridLayout()

        # Add board view
        self.q_board = Board(self.RADIUS, players)
        board_view = QGraphicsView(self.q_board)
        board_view.setMinimumWidth(self.RADIUS * 2.1)
        board_view.setMinimumHeight(self.RADIUS * 2.1)
        layout.addWidget(board_view, 0, 0, 2, 1)

        # Add a panel showing details for each player
        player_panel = PlayerPanel(players, self.dress)
        self.q_players = player_panel.q_players
        layout.addWidget(player_panel, 0, 1)

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
            self.update()

    def end_round(self):
        """Complete counter transactions required at the end of the round."""

        if self.q_board.game.winner:

            # Game winner gets counters from all other players
            game_winner = self.q_players[self.q_board.game.winner]
            for player in self.q_players.values():
                game_winner.counters += player.cards
                player.counters -= player.cards

            # Winners of individual segments get contents
            for seg in self.q_board.segments:
                if seg.winner:
                    player = self.q_players[seg.winner]
                    player.counters = player.counters + seg.empty()

            # Clear round-specific data inputs
            for player in self.q_players.values():
                player.q_cards.setText("")
            for seg in self.q_board.segments:
                seg.q_player.setCurrentIndex(0)


if __name__ == '__main__':
    App = QApplication(sys.argv)
    window = Window(parse_args().players)
    sys.exit(App.exec())
