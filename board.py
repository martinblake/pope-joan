import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QFont
from PyQt5.QtWidgets import QGroupBox, QGridLayout, QLabel, QFrame, QComboBox


class Segment(QGroupBox):

    @staticmethod
    def _label(text, font=QFont.Normal):
        label = QLabel(text)
        label.setFont(QFont('SansSerif', 8, font))
        return label

    def __init__(self, parent, name, dress_value, players):
        super().__init__(name, parent)
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
        w = self.rect().width()
        h = self.rect().height()
        super().move(x - w / 2, y - h / 2)

    def dress(self):
        """Dress the segment and return the cost."""
        self.counters += self.dress_value
        return self.dress_value

    @property
    def counters(self):
        return self.__counters

    @counters.setter
    def counters(self, val):
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


class Board(QFrame):

    def __init__(self, parent, x0, y0, radius, players):
        super().__init__(parent)
        self.radius = radius
        self.setGeometry(x0 - radius, y0 - radius, radius * 2, radius * 2)

        self.game = Segment(self, "Game", 1, players)
        self.segments = (
            self.game,
            Segment(self, "Ace", 1, players),
            Segment(self, "King", 1, players),
            Segment(self, "Queen", 1, players),
            Segment(self, "Jack", 1, players),
            Segment(self, "9 Diamonds", 6, players),
            Segment(self, "Matrimony", 2, players),
            Segment(self, "Intrigue", 2, players)
        )
        for i, seg in enumerate(self.segments):
            theta = 2 * np.pi * (i + 0.5) / len(self.segments)
            x = self.radius + 0.7 * self.radius * np.cos(theta)
            y = self.radius + 0.7 * self.radius * np.sin(theta)
            seg.move(x, y)

    def paintEvent(self, event):
        """Draw the board shape."""
        painter = QPainter(self)
        painter.setPen(QPen(Qt.black, 3, Qt.SolidLine))
        painter.drawEllipse(0, 0, 2 * self.radius, 2 * self.radius)
        x0 = y0 = self.radius
        for i, seg in enumerate(self.segments):
            theta = 2 * np.pi * i / len(self.segments)
            x1 = x0 + self.radius * np.cos(theta)
            y1 = y0 + self.radius * np.sin(theta)
            painter.drawLine(x0, y0, x1, y1)

    def dress(self):
        """Dress the board and return the cost."""
        return sum([seg.dress() for seg in self.segments])

    @property
    def dress_value(self):
        return sum([seg.dress_value for seg in self.segments])
