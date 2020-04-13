import unittest
from contextlib import contextmanager
from copy import copy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette
from PyQt5.QtTest import QTest

from table.main import TableView

TEST_PLAYERS = [f"Player{i}" for i in range(4)]
ALL_SEGMENTS = ["Game", "Ace", "Jack", "Queen", "King",
                "Intrigue", "Matrimony", "9 Diamonds"]
ALL_PLAYERS_AND_SEGMENTS = [*TEST_PLAYERS, *ALL_SEGMENTS]

DRESS_VALUE = 15
START_COUNTERS = 50


class TableTest(unittest.TestCase):
    """Test the Pope Joan table GUI."""

    def setUp(self):
        """Initialise the table view."""
        self.table = TableView(START_COUNTERS, copy(TEST_PLAYERS))

    def find_count(self, name):
        """Find the player or segment with the given name."""
        return (self.table.q_players[name].count.text()
                if name in TEST_PLAYERS else
                self.table.q_board.counts[name].toPlainText())

    def mock_segment_win(self, player_name, segment_name):
        """Mock a player winning a segment."""
        winner = self.table.q_board.winners[segment_name]
        QTest.mouseClick(winner, Qt.LeftButton)
        for _ in range(self.table.scorer.players.index(player_name) + 1):
            QTest.keyEvent(QTest.Press, winner, Qt.Key_Down)
        QTest.keyEvent(QTest.Press, winner, Qt.Key_Enter)

    def mock_cards_left(self, player_name, number):
        """Mock the number of cards left in a player's hand."""
        cards = self.table.q_players[player_name].cards
        QTest.mouseClick(cards, Qt.LeftButton)
        QTest.keyClicks(cards, str(number))

    def finish_dress(self):
        """Make sure the board is dressed by trying for every player."""
        for name in TEST_PLAYERS:
            QTest.mouseClick(self.table.q_players[name].dress, Qt.LeftButton)

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
            name: int(self.find_count(name)) + change
            for name, change in full_change_dict.items()
        }
        yield
        self.assertEqual(
            expected_counts,
            {name: int(self.find_count(name))
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
            QTest.mouseClick(self.table.q_players[player_name].dress,
                             Qt.LeftButton)

    def check_player_color(self, player, expected):
        """Check the window colour for the given player's buttons."""
        player = self.table.q_players[player]
        for button in (player.dress, player.drop):
            color = player.dress.palette().color(QPalette.Window)
            # Alpha depends on isEnabled, which we're not testing here
            color.setAlpha(255)
            self.assertEqual(expected, color)

    def check_failed_board_dress(self, player_name):
        """Check that the given player cannot dress the board."""
        expected_count_changes = {
            name: 0 for name in
            (player_name, "Game", "Jack", "Queen", "King",
             "Ace", "Intrigue", "Matrimony", "9 Diamonds")
        }
        with self.assert_count_changes(expected_count_changes):
            QTest.mouseClick(self.table.q_players[player_name].dress,
                             Qt.LeftButton)

    def check_player_bold_italic(self, player, expected):
        """Return whether the given player is in italic text."""
        font = self.table.q_players[player].font()
        self.assertEqual(expected, font.bold())
        self.assertEqual(expected, font.italic())

    def test_initialisation(self):
        """Test the initial state of the table."""

        # Check the initial board state
        for segment in ALL_SEGMENTS:
            count = self.table.q_board.counts[segment]
            winner = self.table.q_board.winners[segment]
            self.assertEqual("0", count.toPlainText())
            for idx, name in enumerate(["", *TEST_PLAYERS]):
                self.assertEqual(name, winner.itemText(idx))
            self.assertEqual("", winner.currentText())

        # Check the initial counters assigned to each player
        for player in self.table.q_players:
            self.assertEqual(str(START_COUNTERS), player.count.text())

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
        self.mock_segment_win("Player2", "Game")
        QTest.mouseClick(self.table.q_end_round, Qt.LeftButton)

        # Player 1 drops out
        QTest.mouseClick(self.table.q_players["Player1"].drop, Qt.LeftButton)

        # Board dressing continues to player 2
        self.check_failed_board_dress("Player1")
        self.check_successful_board_dress("Player2")

        # Player 1 can no longer win segments
        self.assertRaises(
            ValueError, lambda: self.mock_segment_win("Player1", "Game")
        )

        # Player 1 can no longer lose cards
        self.mock_cards_left("Player1", 5)
        self.mock_cards_left("Player0", 50)
        self.mock_segment_win("Player3", "Game")
        expected_changes = {"Player0": -50, "Player3": 51, "Game": -1}
        with self.assert_count_changes(expected_changes):
            QTest.mouseClick(self.table.q_end_round, Qt.LeftButton)

        # Meanwhile, player 0 has gone negative, so can also drop out,
        # even though they're not dressing
        QTest.mouseClick(self.table.q_players["Player0"].drop, Qt.LeftButton)

        # This doesn't interrupt the dresser cycle, i.e. it's still
        # Player 3's turn
        self.check_successful_board_dress("Player3")

        # Player 0 also cannot win segments now
        self.assertRaises(
            ValueError, lambda: self.mock_segment_win("Player0", "Jack")
        )

    def test_dresser_color(self):
        """
        Test changing colour based on whether players are expected to or are
        able to dress the board.
        """

        # Player 0 is the initial dresser
        self.check_player_color("Player0", Qt.green)

        # Player 0 cannot drop out
        QTest.mouseClick(self.table.q_players["Player1"].drop, Qt.LeftButton)
        self.check_player_color("Player0", Qt.green)

        # Player 0 has finished dressing
        self.finish_dress()
        self.check_player_color("Player0", Qt.darkGray)

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
        QTest.mouseClick(self.table.q_players["Player1"].drop, Qt.LeftButton)
        self.check_player_color("Player1", Qt.lightGray)

        # Player 2 now must dress
        self.check_player_color("Player2", Qt.red)

        # Player 2 keeps playing, but goes negative
        self.finish_dress()
        self.assertLess(
            int(self.table.q_players["Player2"].count.text()), 0
        )
        self.check_player_color("Player2", Qt.red)

        # Player 3 has enough to dress once...
        self.mock_cards_left("Player3", 30)
        self.finish_round()
        self.check_player_color("Player3", Qt.green)

        # ...but will then be below the limit
        self.finish_dress()
        self.check_player_color("Player3", Qt.yellow)

    def test_dresser_indicator(self):
        """Test displaying the dresser in bold and italics."""

        # Player 0 is the initial dresser
        self.check_player_bold_italic("Player0", True)

        # Player 0 is still indicated as the dresser even after dressing
        self.finish_dress()
        self.check_player_bold_italic("Player0", True)

        # Player 1 is then the dresser
        self.finish_round()
        self.check_player_bold_italic("Player0", False)
        self.check_player_bold_italic("Player1", True)
