import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from table.main import TableView
from table.player import START_COUNTERS

App = QApplication([])

TEST_PLAYERS = [f"Player{i}" for i in range(4)]

DRESS_VALUE = 15


class TableTest(unittest.TestCase):
    """Test the Pope Joan table GUI."""

    def check_successful_board_dress(self, board, player):
        """Check that the given player successfully dresses the board."""
        player_count_init = player.counters
        segment_counts_init = [int(s.q_counters.text())
                               for s in board.q_segments]
        QTest.mouseClick(player.q_dress, Qt.LeftButton)
        self.assertEqual(player_count_init - DRESS_VALUE, player.counters)
        for count_init, segment in zip(segment_counts_init, board.q_segments):
            self.assertEqual(count_init + segment.dress_value,
                             int(segment.q_counters.text()))

    def check_failed_board_dress(self, board, player):
        """Check that the given player cannot dress the board."""
        player_count_init = player.counters
        segment_counts_init = [int(s.q_counters.text())
                               for s in board.q_segments]
        QTest.mouseClick(player.q_dress, Qt.LeftButton)
        self.assertEqual(player_count_init, player.counters)
        for count_init, segment in zip(segment_counts_init, board.q_segments):
            self.assertEqual(count_init, int(segment.q_counters.text()))

    def finish_round(self, table):
        """Finish the current round as simply as possible."""
        player = table.q_board.q_game.q_player
        QTest.mouseClick(player, Qt.LeftButton)
        QTest.keyEvent(QTest.Press, player, Qt.Key_Down)
        QTest.keyEvent(QTest.Press, player, Qt.Key_Enter)
        QTest.mouseClick(table.q_end_round, Qt.LeftButton)

    def test_initialisation(self):
        """Test the initial state of the table."""
        table = TableView(TEST_PLAYERS)

        # Check the initial board state
        for segment in table.q_board.q_segments:
            self.assertEqual(0, segment.counters)
            self.assertEqual("0", segment.q_counters.text())
            for idx, name in enumerate(["", *TEST_PLAYERS]):
                self.assertEqual(name, segment.q_player.itemText(idx))
            self.assertEqual("", segment.q_player.currentText())

        # Check the initial counters assigned to each player
        for player in table.q_players:
            self.assertEqual(START_COUNTERS, player.counters)
            self.assertEqual(str(START_COUNTERS), player.q_counters.text())

    def test_board_dress(self):
        """Test dressing the board."""
        table = TableView(TEST_PLAYERS)

        # Board dressing doesn't initially work for players 1, 2 or 3
        for name in ("Player1", "Player2", "Player3"):
            self.check_failed_board_dress(
                table.q_board, table.q_players[name]
            )

        # Board dressing does work for player 0
        self.check_successful_board_dress(
            table.q_board, table.q_players["Player0"]
        )

        # Finish round, ready for next dressing
        self.finish_round(table)

        # Board dressing now doesn't work for players 0, 2 or 3
        for name in ("Player0", "Player2", "Player3"):
            self.check_failed_board_dress(
                table.q_board, table.q_players[name])

        # Board dressing does work for player 1
        self.check_successful_board_dress(
            table.q_board, table.q_players["Player1"]
        )
