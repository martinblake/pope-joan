from collections import OrderedDict, namedtuple
from enum import Enum, auto

Balance = namedtuple("Balance", ["segments", "players"])

SEGMENTS = OrderedDict([
    ("Game", 1),
    ("Ace", 1),
    ("Jack", 1),
    ("Intrigue", 2),
    ("Queen", 1),
    ("Matrimony", 2),
    ("King", 1),
    ("9 Diamonds", 6),
])

PLAYER_START_VALUE = 50


def dress_value():
    """Return the value required to dress the board."""
    return sum(SEGMENTS.values())


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


class Scorer:
    """A tracker of the state of play."""

    def __init__(self, starting_value, players):
        """Initialise round and phase."""
        self.round = 1
        self.phase = Phase.DRESSING
        self.players = players
        self.dresser_idx = 0
        self.balance = Balance(
            segments={s: 0 for s in SEGMENTS},
            players={p: starting_value for p in self.players},
        )

    def _advance(self):
        """Proceed to the next round/phase."""
        self.phase = self.phase.next()
        if self.phase == Phase.DRESSING:
            self.round += 1
            self.dresser_idx += 1
            if self.dresser_idx >= len(self.players):
                self.dresser_idx = 0

    def log_dress(self, player):
        """Log a player dressing the board."""
        self.balance.players[player] -= dress_value()
        for segment, value in SEGMENTS.items():
            self.balance.segments[segment] += value
        self._advance()

    def log_round(self, segment_winners, player_cards):
        """Log the results of the round."""
        for segment, winner in segment_winners.items():
            if winner:
                self.balance.players[winner] += self.balance.segments[segment]
                self.balance.segments[segment] = 0
        for player, cards in player_cards.items():
            self.balance.players[player] -= cards
            self.balance.players[segment_winners["Game"]] += cards
        self._advance()

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
