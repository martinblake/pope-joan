import argparse
import sys
from functools import partial

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton

from board import Board
from player import Player


def parse_args():
    """Parse and return command line arguments."""
    parser = argparse.ArgumentParser(description="Create Pope Joan session.")
    parser.add_argument("players", nargs="+",
                        help="The names of the players.")
    return parser.parse_args()


class Window(QMainWindow):
    """Manage all components at a high level."""

    WIDTH = 1000  # Total window width
    HEIGHT = 640  # Total window height
    RADIUS = 320  # Board radius

    def __init__(self, players):
        """Initialise widgets."""
        super().__init__()
        self.setWindowTitle("Pope Joan")
        self.setGeometry(0, 0, self.WIDTH, self.HEIGHT)

        # Add board view
        self.q_board = Board(self,
                             self.RADIUS, self.HEIGHT / 2,
                             self.RADIUS,
                             players)

        # Add a view for each player
        self.q_players = {}
        for i, name in enumerate(players):
            player = Player(self, name, partial(self.dress, name))
            player.move(2 * self.RADIUS + (self.WIDTH - 2 * self.RADIUS) / 2,
                        self.HEIGHT * (i + 0.5) / len(players))
            self.q_players[name] = player

        # Add a button for completing the round
        self.q_end_round = QPushButton("End Round", self)
        self.q_end_round.move(2 * self.RADIUS - 50, 2 * self.RADIUS - 50)
        self.q_end_round.clicked.connect(self.end_round)

        self.show()

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
