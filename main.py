"""Entry point for the application."""
import argparse
import sys
from enum import Enum, auto

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QWidget,
)

from board import Board
from player import PlayerPanel

BORROW_AMOUNT = 10


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


class Phase(Enum):
    """An enumeration of phases in each round."""
    DRESSING = auto()
    SCORING = auto()

    def next(self):
        """Return the next phase."""
        if self == self.DRESSING:
            return self.SCORING
        else:
            return self.DRESSING


class GameState:
    """A tracker of the state of play."""

    def __init__(self, players):
        """Initialise round and phase."""
        self.round = 1
        self.phase = Phase.DRESSING
        self.players = players
        self.dresser_idx = 0

    def advance(self):
        """Proceed to the next round/phase."""
        self.phase = self.phase.next()
        if self.phase == Phase.DRESSING:
            self.round += 1
            self.dresser_idx += 1
            if self.dresser_idx >= len(self.players):
                self.dresser_idx = 0

    @property
    def title(self):
        """Return a title for displaying round and phase."""
        return f"Round {self.round} - {self.phase.name.title()}"

    @property
    def dresser(self):
        """Return the current board dresser."""
        return self.players[self.dresser_idx]

    def drop(self, player):
        """Remove the given player from the game."""
        self.players.remove(player)
        if self.dresser_idx >= len(self.players):
            self.dresser_idx = 0


class GameView(QWidget):
    """Top level view for game activity."""

    def __init__(self, players):
        """Initialise widgets."""
        super().__init__()
        layout = QGridLayout()

        # Add a title indicating the game state
        self.state = GameState(players)
        self.q_title = QLabel(self.state.title)
        self.q_title.setFont(QFont('SansSerif', 16, QFont.Bold))
        layout.addWidget(self.q_title, 0, 0, 1, 2)

        # Add board view
        self.q_board = Board(players, self.game_winner_cb)
        layout.addWidget(self.q_board, 1, 0, 2, 1)

        # Add a panel showing details for each player
        self.q_players = PlayerPanel(players, self.dress, self.drop, self.borrow)
        layout.addWidget(self.q_players, 1, 1)

        # Add a button for completing the round
        self.q_end_round = QPushButton("End Round")
        self.q_end_round.clicked.connect(self.end_round)
        layout.addWidget(self.q_end_round, 2, 1)

        self.setLayout(layout)

        # Initial state
        self.q_board.disable()
        self.q_players.dressing_phase(self.state.dresser,
                                      self.q_board.dress_value)
        self.q_end_round.setEnabled(False)

    def dress(self, player):
        """Dress the board using counters from the given player."""
        player.counters -= self.q_board.dress()
        self.advance_game_state()
        self.q_board.enable()
        self.q_players.scoring_phase()

    def drop(self, player):
        """Drop the given player from the game."""
        player.setEnabled(False)
        self.state.drop(player.name)
        self.q_players.dressing_phase(self.state.dresser,
                                      self.q_board.dress_value)
        self.q_board.drop_player(player.name)

    def borrow(self, player):
        """Borrow some counters to stay in the game."""
        player.counters += BORROW_AMOUNT
        self.q_players.dressing_phase(self.state.dresser,
                                      self.q_board.dress_value)

    def game_winner_cb(self, name):
        """
        Only enable the 'End Round' button once the game winner is selected.
        """
        self.q_end_round.setEnabled(name != "")

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

            self.advance_game_state()
            self.q_board.disable()
            self.q_players.dressing_phase(self.state.dresser,
                                          self.q_board.dress_value)
            self.q_end_round.setEnabled(False)

    def advance_game_state(self):
        """Advance the game state, update the title and usable widgets."""
        self.state.advance()
        self.q_title.setText(self.state.title)


if __name__ == '__main__':
    App = QApplication(sys.argv)
    window = Window(parse_args().players)
    sys.exit(App.exec())
