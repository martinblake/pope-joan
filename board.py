import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QComboBox,
    QGraphicsScene,
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


class Board(QGraphicsScene):
    """Representation of the state of the board."""

    def __init__(self, radius, players):
        """Initialise the board."""
        super().__init__()
        self.radius = radius
        self.addEllipse(0, 0, 2 * self.radius, 2 * self.radius)

        self.game = Segment("Game", 1, players)
        self.segments = (
            self.game,
            Segment("Ace", 1, players),
            Segment("Jack", 1, players),
            Segment("Intrigue", 2, players),
            Segment("Queen", 1, players),
            Segment("Matrimony", 2, players),
            Segment("King", 1, players),
            Segment("9 Diamonds", 6, players),
        )

        # Draw the board segment boundaries
        x0 = y0 = self.radius
        for i, seg in enumerate(self.segments):
            theta = 2 * np.pi * i / len(self.segments)
            x1 = x0 + self.radius * np.cos(theta)
            y1 = y0 + self.radius * np.sin(theta)
            self.addLine(x0, y0, x1, y1)

        # Add widgets for each segment
        for i, seg in enumerate(self.segments):
            self.addWidget(seg)
            theta = 2 * np.pi * (i + 0.5) / len(self.segments)
            x = self.radius + 0.7 * self.radius * np.cos(theta)
            y = self.radius + 0.7 * self.radius * np.sin(theta)
            seg.move(x, y)

    def dress(self):
        """Dress the board and return the cost."""
        return sum([seg.dress() for seg in self.segments])

    @property
    def dress_value(self):
        """Return the full cost of dressing the board."""
        return sum([seg.dress_value for seg in self.segments])
