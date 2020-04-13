"""Management of the board display."""
import os
import sys

import numpy as np
from collections import OrderedDict

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QImage, QPen
from PyQt5.QtWidgets import QComboBox, QGraphicsScene, QGraphicsView


from table.scorer import Phase, SEGMENTS


def resource_dir():
    """Return the path to the resources directory."""
    root_dir = (getattr(sys, "_MEIPASS", os.path.abspath("."))
                if getattr(sys, "frozen", False) else os.path.abspath("."))
    return os.path.join(root_dir, "resources")


def background_image_file():
    """Return the path to the background image file."""
    return os.path.join(resource_dir(), "wood_texture.jpg")


class Winner(QComboBox):
    """A single segment of the board."""

    def __init__(self, players):
        """
        Initialise with name, amount required to dress and a full list of
        players.
        """
        super().__init__()
        font = self.font()
        font.setWeight(QFont.Black)
        font.setPixelSize(15)
        self.setFont(font)
        self.set_options(players)

    def set_options(self, players):
        """Set the winner options."""
        self.addItems([None, *players])
        self.setItemData(0, Qt.red, Qt.FontRole)

    def move(self, x, y):
        """
        Adjust the 'move' method such that widget is centred at the
        requested location.
        """
        w = self.rect().width()
        h = self.rect().height()
        super().move(x - w / 2, y - h / 2)

    def automatically_populates(self, *winners):
        """
        Configure the provided segment's player entries to be set along with
        this segment.
        """

        def callback():
            index = self.currentIndex()
            for winner in winners:
                winner.setCurrentIndex(index)

        self.currentIndexChanged.connect(callback)


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

        self._draw_background(scene)

        self.counts = self._place_counts(scene)
        self.winners = self._place_winners(scene, players)

        self.winners["Intrigue"].automatically_populates(
            self.winners["Jack"], self.winners["Queen"]
        )
        self.winners["Matrimony"].automatically_populates(
            self.winners["Queen"], self.winners["King"]
        )
        game_winner = self.winners["Game"]
        game_winner.currentIndexChanged.connect(
            lambda: game_winner_cb(game_winner)
        )

    @staticmethod
    def _segment_angles():
        """Return a list of angles in the middle of segments."""
        return [2 * np.pi * (i + 0.5) / len(SEGMENTS)
                for i in range(len(SEGMENTS))]

    @staticmethod
    def _boundary_angles():
        """Return a list of angles on the boundaries between segments."""
        return [2 * np.pi * i / len(SEGMENTS)
                for i in range(len(SEGMENTS))]

    def _from_radial(self, r_frac, theta):
        """Return Cartesian coordinates from radial specification."""
        x = self.RADIUS + r_frac * self.RADIUS * np.cos(theta)
        y = self.RADIUS + r_frac * self.RADIUS * np.sin(theta)
        return x, y

    def _draw_background(self, scene):
        """Draw the boundaries between adjacent segments."""

        ellipse = scene.addEllipse(0, 0, 2 * self.RADIUS, 2 * self.RADIUS)
        ellipse.setPen(QPen(QBrush(), 0))
        ellipse.setBrush(QBrush(QImage(background_image_file())))

        # Add segment boundaries
        for theta in self._boundary_angles():
            x1, y1 = self._from_radial(0.1, theta)
            x2, y2 = self._from_radial(0.9, theta)
            line = scene.addLine(x1, y1, x2, y2)
            pen = line.pen()
            pen.setBrush(QBrush(QColor(0, 0, 0, 128)))
            pen.setWidth(10)
            pen.setCapStyle(Qt.RoundCap)
            line.setPen(pen)

        # Add segment name label
        for theta, name in zip(self._segment_angles(), SEGMENTS):
            x_name, y_name = self._from_radial(0.9, theta)
            text = scene.addText(name)
            font = text.font()
            font.setWeight(QFont.Black)
            font.setPixelSize(20)
            text.setFont(font)
            text.setDefaultTextColor(QColor(0, 0, 0, 128))
            center = text.boundingRect().center()
            text.setTransformOriginPoint(center)
            text.setPos(x_name - center.x(), y_name - center.y())
            text_angle = np.degrees(theta) % 180 - 90
            text.setRotation(text_angle)

    def _place_counts(self, scene):
        """Place and return a dict of counter counts."""

        def place_count(theta):
            x_count, y_count = self._from_radial(0.4, theta)
            count = scene.addText("0")
            font = count.font()
            font.setWeight(QFont.Black)
            font.setPixelSize(40)
            count.setFont(font)
            count.setDefaultTextColor(QColor(0, 0, 0, 128))
            center = count.boundingRect().center()
            count.setPos(x_count - center.x(), y_count - center.y())
            return count

        return OrderedDict(
            (name, place_count(theta))
            for name, theta in zip(SEGMENTS, self._segment_angles())
        )

    def _place_winners(self, scene, players):
        """Place and return a dict of winner selection boxes."""
        winners = OrderedDict(
            (name, Winner(players)) for name in SEGMENTS
        )
        for winner, theta in zip(winners.values(), self._segment_angles()):
            x_widget, y_widget = self._from_radial(0.7, theta)
            scene.addWidget(winner)
            winner.move(x_widget, y_widget)
        return winners

    def refresh(self, phase, players, balance):
        """Refresh the board."""

        # Update segment counts
        for segment, value in balance.items():
            self.counts[segment].setPlainText(str(value))

        for winner in self.winners.values():

            # Update widget state based on the game phase
            winner.setEnabled(phase == Phase.SCORING)

            # Update player options
            winner.clear()
            winner.set_options(players)
            winner.setCurrentIndex(0)

        self.update()
