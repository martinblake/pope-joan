"""Management of the board display."""
import numpy as np
from collections import OrderedDict

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QGraphicsScene,
    QGraphicsView,
    QGroupBox,
    QGridLayout,
    QLabel,
)

from table.scorer import Phase, SEGMENTS


class Segment(QGroupBox):
    """A single segment of the board."""

    def __init__(self, name, dress_value, players):
        """
        Initialise with name, amount required to dress and a full list of
        players.
        """
        super().__init__(name)
        self.setAlignment(Qt.AlignCenter)
        self.dress_value = dress_value

        grid = QGridLayout(self)
        grid.addWidget(QLabel("Count:"), 0, 0)
        grid.addWidget(QLabel("Player:"), 1, 0)

        self.q_counters = QLabel("")
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

    @property
    def winner(self):
        """The assigned winner of the segment."""
        return self.q_player.currentText()

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

    RADIUS = 270

    def __init__(self, players, game_winner_cb):
        """
        Initialise the board.
        :param players:  A list of the players
        :param game_winner_cb:  Function to call when a game winner is selected
        """
        scene = QGraphicsScene()
        super().__init__(scene)

        self.setMinimumWidth(self.RADIUS * 2.2)
        self.setMinimumHeight(self.RADIUS * 2.2)

        scene.addEllipse(0, 0, 2 * self.RADIUS, 2 * self.RADIUS)

        self.q_segments = OrderedDict(
            (name, Segment(name, value, players))
            for name, value in SEGMENTS.items()
        )

        self.q_segments["Intrigue"].automatically_populates(
            self.q_segments["Jack"], self.q_segments["Queen"]
        )
        self.q_segments["Matrimony"].automatically_populates(
            self.q_segments["Queen"], self.q_segments["King"]
        )
        self.q_game.q_player.currentIndexChanged.connect(
            lambda: game_winner_cb(self.q_game.winner)
        )

        self._draw_segment_boundaries(scene)
        self._add_segment_widgets(scene)

    @property
    def q_game(self):
        return self.q_segments["Game"]

    def _draw_segment_boundaries(self, scene):
        """Draw the boundaries between adjacent segments."""
        x0 = y0 = self.RADIUS
        for i, seg in enumerate(self.q_segments.values()):
            theta = 2 * np.pi * i / len(self.q_segments)
            x1 = x0 + self.RADIUS * np.cos(theta)
            y1 = y0 + self.RADIUS * np.sin(theta)
            scene.addLine(x0, y0, x1, y1)

    def _add_segment_widgets(self, scene):
        """Add widgets for each segment."""
        for i, seg in enumerate(self.q_segments.values()):
            scene.addWidget(seg)
            theta = 2 * np.pi * (i + 0.5) / len(self.q_segments)
            x = self.RADIUS + 0.7 * self.RADIUS * np.cos(theta)
            y = self.RADIUS + 0.7 * self.RADIUS * np.sin(theta)
            seg.move(x, y)

    def refresh(self, phase, players, balance):
        """Refresh the board."""

        # Update segment counts
        for segment, value in balance.items():
            self.q_segments[segment].q_counters.setText(str(value))

        for segment in self.q_segments.values():

            # Update widget state based on the game phase
            segment.q_player.setEnabled(phase == Phase.SCORING)

            # Update player options
            segment.q_player.clear()
            segment.q_player.addItems([None, *players])
            segment.q_player.setCurrentIndex(0)

        self.update()
