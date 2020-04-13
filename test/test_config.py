import unittest
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QDialog

from table.config import ConfigView


class TestConfig(unittest.TestCase):
    """Test the Pope Joan configuratino dialog."""

    def setUp(self):
        """Initialise the config dialog."""
        self.config = ConfigView()

    def enter_starting_value(self, value):
        """Enter the starting value for each player."""
        widget = self.config.q_starting_value.q_value
        QTest.mouseClick(widget, Qt.LeftButton)
        QTest.keyClicks(widget, str(value))

    def enter_player(self, idx, name):
        """Enter the name of a player."""
        widget = self.config.q_player_list.q_players[idx]
        QTest.mouseClick(widget, Qt.LeftButton)
        QTest.keyClicks(widget, name)

    def click_continue(self):
        """Click continue on the dialog."""
        QTest.mouseClick(self.config.q_continue, Qt.LeftButton)

    def test_no_starting_value(self):
        """Test dialog not accepted without a starting value."""
        self.enter_player(0, "Harry Potter")
        self.click_continue()
        self.assertEqual(QDialog.Rejected, self.config.result())

    def test_no_players(self):
        """Test dialog not accepted without players."""
        self.enter_starting_value(35)
        self.click_continue()
        self.assertEqual(QDialog.Rejected, self.config.result())

    def test_one_player(self):
        """Test that a minimum of one player is needed."""
        self.enter_starting_value(50)
        self.enter_player(0, "Mr Bean")
        self.click_continue()
        self.assertEqual(50, self.config.starting_value)
        self.assertEqual(["Mr Bean"], self.config.player_list)
        self.assertEqual(QDialog.Accepted, self.config.result())

    def test_multiple_players(self):
        """Test that multiple players are equally accepted."""
        self.enter_starting_value(40)
        self.enter_player(0, "Doc")
        self.enter_player(2, "Happy")
        self.enter_player(7, "Bashful")
        self.click_continue()
        self.assertEqual(40, self.config.starting_value)
        self.assertEqual(["Doc", "Happy", "Bashful"], self.config.player_list)
        self.assertEqual(QDialog.Accepted, self.config.result())

    def test_repeated_player(self):
        """Test that player names can't be repeated."""
        self.enter_starting_value(25)
        self.enter_player(1, "Bill")
        self.enter_player(3, "Ben")
        self.enter_player(4, "Bill")
        self.click_continue()
        self.assertEqual(QDialog.Rejected, self.config.result())
