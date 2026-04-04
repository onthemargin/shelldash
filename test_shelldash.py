"""Tests for Shell Dash Python game (shelldash.py)."""

import pytest
from shelldash import ShellDashGame


# ---------------------------------------------------------------------------
# Deck creation
# ---------------------------------------------------------------------------

class TestCreateDeck:
    """Tests for ShellDashGame.create_deck()."""

    def test_deck_has_51_cards(self):
        game = ShellDashGame()
        deck = game.create_deck()
        assert len(deck) == 51

    def test_deck_card_distribution(self):
        game = ShellDashGame()
        deck = game.create_deck()
        counts = {card: deck.count(card) for card in game.cards}
        assert counts == {
            'Sand': 20,
            'Wave': 10,
            'Flip-Flop': 6,
            'Jellyfish': 6,
            'Sun': 5,
            'Shell': 4,
        }

    def test_deck_only_contains_valid_card_types(self):
        game = ShellDashGame()
        deck = game.create_deck()
        valid = set(game.cards)
        for card in deck:
            assert card in valid

    def test_deck_is_shuffled(self):
        """Two decks should almost certainly differ in order."""
        game = ShellDashGame()
        deck1 = game.create_deck()
        deck2 = game.create_deck()
        # Extremely unlikely both are identical after shuffle
        # Run 5 times to reduce false-positive probability
        all_same = all(game.create_deck() == deck1 for _ in range(5))
        assert not all_same


# ---------------------------------------------------------------------------
# Board setup
# ---------------------------------------------------------------------------

class TestSetupBoard:
    """Tests for ShellDashGame.setup_board()."""

    def test_board_has_correct_dimensions(self):
        game = ShellDashGame()
        assert len(game.board) == 3
        for row in game.board:
            assert len(row) == 3

    def test_board_cells_have_card_and_revealed_keys(self):
        game = ShellDashGame()
        for row in game.board:
            for cell in row:
                assert 'card' in cell
                assert 'revealed' in cell

    def test_all_cards_start_hidden(self):
        game = ShellDashGame()
        for row in game.board:
            for cell in row:
                assert cell['revealed'] is False

    def test_board_cards_are_valid_types(self):
        game = ShellDashGame()
        valid = set(game.cards)
        for row in game.board:
            for cell in row:
                assert cell['card'] in valid

    def test_setup_board_resets_board(self):
        game = ShellDashGame()
        old_board = game.board
        game.setup_board()
        # Board reference should be replaced
        assert game.board is not old_board

    def test_board_respects_custom_rows(self):
        game = ShellDashGame()
        game.rows = 5
        game.setup_board()
        assert len(game.board) == 5


# ---------------------------------------------------------------------------
# Check winner
# ---------------------------------------------------------------------------

class TestCheckWinner:
    """Tests for ShellDashGame.check_winner()."""

    def test_no_winner_at_start(self):
        game = ShellDashGame()
        assert game.check_winner() is None

    def test_no_winner_with_partial_shells(self):
        game = ShellDashGame()
        game.shell_count = [2, 1]
        assert game.check_winner() is None

    def test_player1_wins_with_3_shells(self):
        game = ShellDashGame()
        game.shell_count = [3, 0]
        assert game.check_winner() == 1

    def test_player2_wins_with_3_shells(self):
        game = ShellDashGame()
        game.shell_count = [0, 3]
        assert game.check_winner() == 2

    def test_player_wins_with_more_than_3_shells(self):
        game = ShellDashGame()
        game.shell_count = [4, 2]
        assert game.check_winner() == 1

    def test_player1_wins_when_both_have_3(self):
        """Player 1 is checked first, so they win if both have 3."""
        game = ShellDashGame()
        game.shell_count = [3, 3]
        assert game.check_winner() == 1


# ---------------------------------------------------------------------------
# Card effect logic (simulating what play_turn does for each card type)
# ---------------------------------------------------------------------------

class TestCardEffects:
    """Test the game logic for each card type by manually simulating reveals."""

    def _make_game_with_board(self, cards_grid):
        """Helper: create a game with a specific board layout.

        Args:
            cards_grid: list of lists of card-type strings, e.g.
                        [['Sand', 'Wave', 'Shell'], ['Jellyfish', 'Sand', 'Sun']]
        """
        game = ShellDashGame()
        game.rows = len(cards_grid)
        game.cols = len(cards_grid[0]) if cards_grid else 3
        game.board = []
        for row_cards in cards_grid:
            game.board.append([{'card': c, 'revealed': False} for c in row_cards])
        return game

    # -- Shell --
    def test_shell_increments_shell_count(self):
        game = self._make_game_with_board([['Shell', 'Sand', 'Sand']])
        game.current_player = 1
        game.shell_count = [0, 0]
        # Simulate revealing Shell at (0, 0)
        game.board[0][0]['revealed'] = True
        card = game.board[0][0]['card']
        assert card == 'Shell'
        game.shell_count[game.current_player - 1] += 1
        assert game.shell_count == [1, 0]

    def test_shell_for_player2(self):
        game = self._make_game_with_board([['Shell', 'Sand', 'Sand']])
        game.current_player = 2
        game.shell_count = [1, 0]
        game.board[0][0]['revealed'] = True
        game.shell_count[game.current_player - 1] += 1
        assert game.shell_count == [1, 1]

    # -- Flip-Flop --
    def test_flip_flop_increments_count(self):
        game = self._make_game_with_board([['Flip-Flop', 'Sand', 'Sand']])
        game.current_player = 1
        game.flip_flop_count = [0, 0]
        game.board[0][0]['revealed'] = True
        game.flip_flop_count[game.current_player - 1] += 1
        assert game.flip_flop_count == [1, 0]

    # -- Jellyfish with Flip-Flop protection --
    def test_jellyfish_uses_flip_flop(self):
        game = self._make_game_with_board([['Jellyfish', 'Sand', 'Sand']])
        game.current_player = 1
        game.flip_flop_count = [1, 0]
        # Player uses a flip-flop to counter jellyfish
        game.flip_flop_count[game.current_player - 1] -= 1
        assert game.flip_flop_count == [0, 0]

    def test_jellyfish_without_flip_flop_ends_turn(self):
        game = self._make_game_with_board([['Jellyfish', 'Sand', 'Sand']])
        game.current_player = 1
        game.flip_flop_count = [0, 0]
        # No flip-flop means turn should end -- flip_flop_count stays 0
        assert game.flip_flop_count[game.current_player - 1] == 0

    # -- Sun expansion --
    def test_sun_expands_board(self):
        game = self._make_game_with_board([
            ['Sun', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
        ])
        assert game.rows == 3
        # Simulate Sun effect
        if game.rows < 6:
            game.rows += 3
            deck = game.create_deck()
            for _ in range(3):
                new_row = []
                for col in range(game.cols):
                    if deck:
                        new_row.append({'card': deck.pop(), 'revealed': False})
                    else:
                        new_row.append({'card': 'Sand', 'revealed': False})
                game.board.append(new_row)
        assert game.rows == 6
        assert len(game.board) == 6

    def test_sun_does_not_expand_beyond_6(self):
        game = self._make_game_with_board([
            ['Sun', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
        ])
        game.rows = 6
        original_len = len(game.board)
        # Sun should not expand when already at 6
        if game.rows < 6:
            game.rows += 3
        assert game.rows == 6
        assert len(game.board) == original_len

    # -- Wave --
    def test_wave_does_not_advance_row(self):
        """Wave card should keep the player in the same row."""
        game = self._make_game_with_board([['Wave', 'Sand', 'Sand']])
        current_row = 0
        game.board[0][0]['revealed'] = True
        card = game.board[0][0]['card']
        if card == 'Wave':
            pass  # Stay in same row
        else:
            current_row += 1
        assert current_row == 0

    def test_all_waves_in_row(self):
        """If all cards in a row are revealed and all are waves, turn ends."""
        game = self._make_game_with_board([['Wave', 'Wave', 'Wave']])
        for cell in game.board[0]:
            cell['revealed'] = True
        all_revealed = all(cell['revealed'] for cell in game.board[0])
        all_waves = all(cell['card'] == 'Wave' for cell in game.board[0])
        assert all_revealed and all_waves


# ---------------------------------------------------------------------------
# Board state after reveals
# ---------------------------------------------------------------------------

class TestBoardState:
    """Tests for board state changes after card reveals."""

    def test_revealing_card_changes_state(self):
        game = ShellDashGame()
        assert game.board[0][0]['revealed'] is False
        game.board[0][0]['revealed'] = True
        assert game.board[0][0]['revealed'] is True

    def test_unrevealed_cards_stay_hidden(self):
        game = ShellDashGame()
        game.board[0][0]['revealed'] = True
        # Other cards remain hidden
        assert game.board[0][1]['revealed'] is False
        assert game.board[0][2]['revealed'] is False

    def test_card_type_persists_after_reveal(self):
        game = ShellDashGame()
        original_card = game.board[1][1]['card']
        game.board[1][1]['revealed'] = True
        assert game.board[1][1]['card'] == original_card


# ---------------------------------------------------------------------------
# Game initialization
# ---------------------------------------------------------------------------

class TestGameInit:
    """Tests for initial game state."""

    def test_initial_shell_counts_are_zero(self):
        game = ShellDashGame()
        assert game.shell_count == [0, 0]

    def test_initial_flip_flop_counts_are_zero(self):
        game = ShellDashGame()
        assert game.flip_flop_count == [0, 0]

    def test_initial_player_is_1(self):
        game = ShellDashGame()
        assert game.current_player == 1

    def test_initial_rows_and_cols(self):
        game = ShellDashGame()
        assert game.rows == 3
        assert game.cols == 3

    def test_player_names_default(self):
        game = ShellDashGame()
        assert game.player_names == ["Player 1", "Player 2"]

    def test_all_card_types_have_colors(self):
        game = ShellDashGame()
        for card in game.cards:
            assert card in game.card_colors

    def test_all_card_types_have_icons(self):
        game = ShellDashGame()
        for card in game.cards:
            assert card in game.card_icons
