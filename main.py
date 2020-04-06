import argparse
import sys
from functools import partial

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton

from board import Board
from player import Player


def parse_args():
    parser = argparse.ArgumentParser(description="Create Pope Joan session.")
    parser.add_argument("players", nargs="+",
                        help="The names of the players.")
    return parser.parse_args()


class Window(QMainWindow):

    WIDTH = 1000
    HEIGHT = 640
    RADIUS = 320

    def __init__(self, players):
        super().__init__()
        self.title = "Pope Joan"
        self.setWindowTitle(self.title)
        self.setGeometry(0, 0, self.WIDTH, self.HEIGHT)

        self.q_board = Board(self,
                             self.RADIUS, self.HEIGHT / 2,
                             self.RADIUS,
                             players)

        self.q_players = {}
        for i, name in enumerate(players):
            player = Player(self, name, partial(self.dress, name))
            player.move(2 * self.RADIUS + (self.WIDTH - 2 * self.RADIUS) / 2,
                        self.HEIGHT * (i + 0.5) / len(players))
            self.q_players[name] = player

        self.q_end_round = QPushButton("End Round", self)
        self.q_end_round.move(2 * self.RADIUS - 50, 2 * self.RADIUS - 50)
        self.q_end_round.clicked.connect(self.end_round)

        self.show()

    def dress(self, player_name):
        player = self.q_players[player_name]
        if self.q_board.dress_value <= player.counters:
            player.counters = player.counters - self.q_board.dress()
            self.update()

    def end_round(self):

        if self.q_board.game.winner:

            # Game winner gets counters from all other players
            winner = self.q_players[self.q_board.game.winner]
            for player in self.q_players.values():
                winner.counters = winner.counters + player.cards
                player.counters = player.counters - player.cards

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
