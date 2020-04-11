import unittest
from contextlib import contextmanager
from copy import copy
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtTest import QTest

from table.main import TableView
from table.player import START_COUNTERS

App = QApplication([])

TEST_PLAYERS = [f"Player{i}" for i in range(4)]
ALL_SEGMENTS = ["Game", "Ace", "Jack", "Queen", "King",
                "Intrigue", "Matrimony", "9 Diamonds"]
ALL_PLAYERS_AND_SEGMENTS = [*TEST_PLAYERS, *ALL_SEGMENTS]

DRESS_VALUE = 15


class TableTest(unittest.TestCase):
    """Test the Pope Joan table GUI."""

    def setUp(self):
        """Initialise the table view."""
        self.table = TableView(copy(TEST_PLAYERS))

    def find_segment(self, segment_name):
        """Find the segment with the given name."""
        segments = self.table.q_board.q_segments
        return next(v for k, v in segments.items() if k == segment_name)

    def find_widget(self, name):
        """Find the player or segment with the given name."""
        return (self.table.q_players[name] if name in TEST_PLAYERS
                else self.find_segment(name))

    def mock_segment_win(self, player_name, segment_name):
        """Mock a player winning a segment."""
        segment = self.find_segment(segment_name)
        QTest.mouseClick(segment.q_player, Qt.LeftButton)
        for _ in range(self.table.scorer.players.index(player_name) + 1):
            QTest.keyEvent(QTest.Press, segment.q_player, Qt.Key_Down)
        QTest.keyEvent(QTest.Press, segment.q_player, Qt.Key_Enter)

    def mock_cards_left(self, player_name, number):
        """Mock the number of cards left in a player's hand."""
        cards = self.table.q_players[player_name].q_cards
        QTest.mouseClick(cards, Qt.LeftButton)
        QTest.keyClicks(cards, str(number))

    def finish_dress(self):
        """Make sure the board is dressed by trying for every player."""
        for name in TEST_PLAYERS:
            QTest.mouseClick(self.table.q_players[name].q_dress, Qt.LeftButton)

    def finish_round(self):
        """Finish the current round as simply as possible."""
        self.mock_segment_win("Player0", "Game")
        QTest.mouseClick(self.table.q_end_round, Qt.LeftButton)

    @contextmanager
    def assert_count_changes(self, change_dict):
        """Check for the expected change in player / segment counters."""
        full_change_dict = {
            name: change_dict[name] if name in change_dict else 0
            for name in ALL_PLAYERS_AND_SEGMENTS
        }
        expected_counts = {
            name: int(self.find_widget(name).q_counters.text()) + change
            for name, change in full_change_dict.items()
        }
        yield
        self.assertEqual(
            expected_counts,
            {name: int(self.find_widget(name).q_counters.text())
             for name in expected_counts}
        )

    def check_successful_board_dress(self, player_name):
        """Check that the given player successfully dresses the board."""
        expected_count_changes = {
            player_name: -DRESS_VALUE,
            **{s: 1 for s in ("Game", "Jack", "Queen", "King", "Ace")},
            **{s: 2 for s in ("Intrigue", "Matrimony")},
            "9 Diamonds": 6
        }
        with self.assert_count_changes(expected_count_changes):
            QTest.mouseClick(self.table.q_players[player_name].q_dress,
                             Qt.LeftButton)

    def check_player_color(self, player, color):
        """Check the window colour for the given player's view."""
        player = self.table.q_players[player]
        self.assertEqual(color, player.palette().color(QPalette.Window))

    def check_failed_board_dress(self, player_name):
        """Check that the given player cannot dress the board."""
        expected_count_changes = {
            name: 0 for name in
            (player_name, "Game", "Jack", "Queen", "King",
             "Ace", "Intrigue", "Matrimony", "9 Diamonds")
        }
        with self.assert_count_changes(expected_count_changes):
            QTest.mouseClick(self.table.q_players[player_name].q_dress,
                             Qt.LeftButton)

    def test_initialisation(self):
        """Test the initial state of the table."""

        # Check the initial board state
        for segment in self.table.q_board.q_segments.values():
            self.assertEqual("0", segment.q_counters.text())
            for idx, name in enumerate(["", *TEST_PLAYERS]):
                self.assertEqual(name, segment.q_player.itemText(idx))
            self.assertEqual("", segment.q_player.currentText())

        # Check the initial counters assigned to each player
        for player in self.table.q_players:
            self.assertEqual(str(START_COUNTERS), player.q_counters.text())

    def test_board_dress(self):
        """Test dressing the board."""

        # Board dressing only works for player 0
        for name in ("Player1", "Player2", "Player3"):
            self.check_failed_board_dress(name)
        self.check_successful_board_dress("Player0")

        # Finish round, ready for next dressing
        self.finish_round()

        # Board dressing now only works for player 1
        for name in ("Player0", "Player2", "Player3"):
            self.check_failed_board_dress(name)
        self.check_successful_board_dress("Player1")

    def test_segment_win(self):
        """Test players winning board segments."""

        # Round 1
        self.finish_dress()

        self.mock_segment_win("Player2", "Game")
        self.mock_segment_win("Player3", "Jack")
        expected_changes = {
            "Player2": 1, "Game": -1,
            "Player3": 1, "Jack": -1,
        }
        with self.assert_count_changes(expected_changes):
            QTest.mouseClick(self.table.q_end_round, Qt.LeftButton)

        # Round 2
        self.finish_dress()

        self.mock_segment_win("Player0", "Game")
        self.mock_segment_win("Player2", "Intrigue")
        expected_changes = {
            "Player0": 1, "Game": -1,
            # Contents of segment is cumulative
            # Intrigue automatically allocates Jack and Queen
            "Player2": 7, "Jack": -1, "Queen": -2, "Intrigue": -4,
        }
        with self.assert_count_changes(expected_changes):
            QTest.mouseClick(self.table.q_end_round, Qt.LeftButton)

        # Round 3
        self.finish_dress()

        self.mock_segment_win("Player3", "9 Diamonds")
        no_changes = {}  # Game must be assigned to a player for round to end
        with self.assert_count_changes(no_changes):
            QTest.mouseClick(self.table.q_end_round, Qt.LeftButton)

        self.mock_segment_win("Player1", "Game")
        expected_changes = {
            "Player1": 1, "Game": -1,
            "Player3": 18, "9 Diamonds": -18,
        }

    def test_card_payout(self):
        """Test players exchanging counters based on cards left in hand."""

        self.finish_dress()

        self.mock_cards_left("Player0", 4)
        self.mock_cards_left("Player1", 3)
        self.mock_cards_left("Player2", 2)
        self.mock_segment_win("Player3", "Game")
        expected_changes = {
            "Player0": -4, "Player1": -3, "Player2": -2, "Game": -1,
            "Player3": 10
        }
        with self.assert_count_changes(expected_changes):
            QTest.mouseClick(self.table.q_end_round, Qt.LeftButton)

    def test_player_drop_out(self):
        """Test player drop out option when unable to dress."""

        # Drain player 1 of counters in first round
        self.finish_dress()
        self.mock_cards_left("Player1", 45)
        self.mock_segment_win("Player0", "Game")
        QTest.mouseClick(self.table.q_end_round, Qt.LeftButton)

        # Player 1 drops out
        QTest.mouseClick(self.table.q_players["Player1"].q_drop, Qt.LeftButton)

        # Board dressing continues to player 2
        self.check_failed_board_dress("Player1")
        self.check_successful_board_dress("Player2")

        # Player 1 can no longer win segments
        self.assertRaises(
            ValueError, lambda: self.mock_segment_win("Player1", "Game")
        )

        # Player 1 can no longer lose cards
        self.mock_cards_left("Player1", 5)
        self.mock_segment_win("Player0", "Game")
        expected_changes = {"Player0": 1, "Game": -1}
        with self.assert_count_changes(expected_changes):
            QTest.mouseClick(self.table.q_end_round, Qt.LeftButton)

    def test_dresser_highlights(self):
        """
        Test highlighting based on whether players are expected to or are
        able to dress the board.
        """

        # Player 0 is the initial dresser
        self.check_player_color("Player0", Qt.green)

        # Player 0 cannot drop out
        QTest.mouseClick(self.table.q_players["Player1"].q_drop, Qt.LeftButton)
        self.check_player_color("Player0", Qt.green)

        # Player 0 is still indicated as the dresser even after dressing
        self.finish_dress()
        self.check_player_color("Player0", Qt.green)

        # Players 1 and 2 are drained of counters
        self.mock_cards_left("Player1", 40)
        self.mock_cards_left("Player2", 40)
        self.finish_round()

        # Player 0 is no longer the dresser
        self.check_player_color("Player0", Qt.darkGray)

        # Player 1 must dress but cannot
        self.check_player_color("Player1", Qt.red)

        # Player 2 doesn't need to dress yet, but wouldn't be able to
        self.check_player_color("Player2", Qt.yellow)

        # Player 1 drops out
        QTest.mouseClick(self.table.q_players["Player1"].q_drop, Qt.LeftButton)
        self.check_player_color("Player1", Qt.lightGray)

        # Player 2 now must dress
        self.check_player_color("Player2", Qt.red)

        # Player 2 keeps playing, but goes negative
        self.finish_dress()
        self.assertLess(
            int(self.table.q_players["Player2"].q_counters.text()), 0
        )
