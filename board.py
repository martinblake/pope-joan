"""Management of the board display."""
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QComboBox,
    QGraphicsScene,
    QGraphicsView,
    QGroupBox,
    QGridLayout,
    QLabel,
)


class Segment(QGroupBox):
    """A single segment of the board."""

    @staticmethod
    def _label(text, font=QFont.Normal):
        """Return a label with consistent formatting."""
        label = QLabel(text)
        label.setFont(QFont('SansSerif', 8, font))
        return label

    def __init__(self, name, dress_value, players):
        """
        Initialise with name, amount required to dress and a full list of
        players.
        """
        super().__init__(name)
        self.setFont(QFont('SansSerif', 10, QFont.Bold))
        self.setAlignment(Qt.AlignCenter)
        self.dress_value = dress_value

        grid = QGridLayout(self)
        grid.addWidget(self._label("Count:"), 0, 0)
        grid.addWidget(self._label("Player:"), 1, 0)

        self.q_counters = self._label("", font=QFont.Bold)
        self.q_player = QComboBox()
        self.q_player.addItems([None, *players])
        grid.addWidget(self.q_counters, 0, 1)
        grid.addWidget(self.q_player, 1, 1)

        self.counters = 0

        self.setLayout(grid)

    def move(self, x, y):
        """
        Adjust the 'move' method such that widget is centred at the
        requested location.
        """
        w = self.rect().width()
        h = self.rect().height()
        super().move(x - w / 2, y - h / 2)

    def dress(self):
        """Dress the segment and return the cost."""
        self.counters += self.dress_value
        return self.dress_value

    @property
    def counters(self):
        """Get the number of counters."""
        return self.__counters

    @counters.setter
    def counters(self, val):
        """Set the number of counters."""
        self.__counters = val
        self.q_counters.setText(str(self.__counters))
        self.update()

    @property
    def winner(self):
        """Return the winner of the segment."""
        return self.q_player.currentText()

    def empty(self):
        """Empty the segment and return its payout."""
        payout = self.counters
        self.counters = 0
        return payout

    def automatically_populates(self, *segments):
        """
        Configure the provided segment's player entries to be set along with
        this segment.
        """
        def callback():
            index = self.q_player.currentIndex()
            for segment in segments:
                segment.q_player.setCurrentIndex(index)
        self.q_player.currentIndexChanged.connect(callback)


class Board(QGraphicsView):
    """Representation of the state of the board."""

    RADIUS = 300

    def __init__(self, players):
        """Initialise the board."""
        scene = QGraphicsScene()
        super().__init__(scene)

        self.setMinimumWidth(self.RADIUS * 2.1)
        self.setMinimumHeight(self.RADIUS * 2.1)

        scene.addEllipse(0, 0, 2 * self.RADIUS, 2 * self.RADIUS)

        self.q_game = Segment("Game", 1, players)
        q_ace = Segment("Ace", 1, players)
        q_jack = Segment("Jack", 1, players)
        q_intrigue = Segment("Intrigue", 2, players)
        q_queen = Segment("Queen", 1, players)
        q_matrimony = Segment("Matrimony", 2, players)
        q_king = Segment("King", 1, players)
        q_9d = Segment("9 Diamonds", 6, players)
        self.q_segments = (self.q_game, q_ace, q_jack, q_intrigue,
                           q_queen, q_matrimony, q_king, q_9d)

        q_intrigue.automatically_populates(q_jack, q_queen)
        q_matrimony.automatically_populates(q_queen, q_king)

        # Draw the board segment boundaries
        x0 = y0 = self.RADIUS
        for i, seg in enumerate(self.q_segments):
            theta = 2 * np.pi * i / len(self.q_segments)
            x1 = x0 + self.RADIUS * np.cos(theta)
            y1 = y0 + self.RADIUS * np.sin(theta)
            scene.addLine(x0, y0, x1, y1)

        # Add widgets for each segment
        for i, seg in enumerate(self.q_segments):
            scene.addWidget(seg)
            theta = 2 * np.pi * (i + 0.5) / len(self.q_segments)
            x = self.RADIUS + 0.7 * self.RADIUS * np.cos(theta)
            y = self.RADIUS + 0.7 * self.RADIUS * np.sin(theta)
            seg.move(x, y)

    def dress(self):
        """Dress the board and return the cost."""
        return sum([seg.dress() for seg in self.q_segments])

    @property
    def dress_value(self):
        """Return the full cost of dressing the board."""
        return sum([seg.dress_value for seg in self.q_segments])

    def clear_round(self):
        """Clear the winner fields."""
        for segment in self.q_segments:
            segment.q_player.setCurrentIndex(0)

    def __iter__(self):
        """Return iterator through segment widgets."""
        return iter(self.q_segments)

    @property
    def winner(self):
        """Return the name of the game winner."""
        return self.q_game.winner
