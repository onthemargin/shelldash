import random

class ShellDashGame:
    """
    Shell Dash is a card-based beach adventure game where two players take turns
    navigating through a randomly generated board to collect 3 Shell cards.
    Players must avoid obstacles like Waves and Jellyfish while using special
    cards like Flip-Flops to help them advance.
    """
    
    def __init__(self):
        """
        Initialize the Shell Dash game with all necessary game components.
        Sets up the card types, their quantities, visual styling, and game state.
        """
        # Define all available card types in the game
        # Each card has a specific function: Sand (advance), Wave (stay), 
        # Flip-Flop (protection), Jellyfish (obstacle), Sun (expand board), Shell (goal)
        self.cards = ['Sand', 'Wave', 'Flip-Flop', 'Jellyfish', 'Sun', 'Shell']
        
        # Card distribution for a balanced 51-card deck
        # Sand cards are most common (safe advancement), Shells are rarest (winning condition)
        self.card_counts = [20, 10, 6, 6, 5, 4]  # Exact counts for 51-card deck
        
        # ANSI color codes for visual card representation in terminal
        # Each card type has a unique color for easy identification
        self.card_colors = {
            'Sand': '\033[93m',      # Yellow - represents beach sand
            'Wave': '\033[94m',      # Blue - represents ocean waves
            'Flip-Flop': '\033[95m', # Magenta - represents beach footwear
            'Jellyfish': '\033[91m', # Red - represents dangerous sea creature
            'Sun': '\033[33m',       # Orange - represents expanding sunshine
            'Shell': '\033[92m'      # Green - represents collectible treasure
        }
        
        # Icon representation for each card type
        self.card_icons = {
            'Sand': '🏖️',       # Beach/sand icon
            'Wave': '🌊',       # Water wave icon
            'Flip-Flop': '🩴',  # Flip-flop/sandal icon
            'Jellyfish': '🪼',  # Jellyfish icon
            'Sun': '☀️',        # Sun icon
            'Shell': '🐚'       # Shell icon
        }
        
        # ANSI reset code to return text to normal color
        self.reset_color = '\033[0m'
        
        # Player name colors for consistent identification
        self.player_colors = {
            1: '\033[96m',  # Cyan for Player 1
            2: '\033[93m'   # Yellow for Player 2
        }
        
        # Game state variables
        self.board = []  # 2D array representing the game board grid
        self.rows = 3    # Initial number of rows (can expand with Sun cards)
        self.cols = 3    # Number of columns (fixed at 3 for A, B, C choices)
        
        # Player tracking
        self.current_player = 1  # Player 1 goes first
        self.player_names = ["Player 1", "Player 2"]  # Default names, will be updated
        
        # Score tracking: index 0 = Player 1, index 1 = Player 2
        self.shell_count = [0, 0]      # Number of Shell cards collected (win at 3)
        self.flip_flop_count = [0, 0]  # Number of Flip-Flop cards held (used against Jellyfish)
        
        # Initialize the game board with shuffled cards
        self.setup_board()
    
    def create_deck(self):
        """
        Create and shuffle a complete deck of cards for the game.
        
        The deck contains 51 cards total with specific distributions:
        - 20 Sand cards (safe advancement)
        - 10 Wave cards (forced to stay in row)
        - 6 Flip-Flop cards (protection against Jellyfish)
        - 6 Jellyfish cards (obstacles that end turn)
        - 5 Sun cards (expand the board)
        - 4 Shell cards (collectible win condition)
        
        Returns:
            list: A shuffled deck of card names ready for distribution
        """
        deck = []  # Initialize empty deck list
        total_cards = 51  # Total cards in complete deck
        
        # Build deck by adding the specified count of each card type
        for i, card_type in enumerate(self.cards):
            count = self.card_counts[i]  # Get count for this card type
            deck.extend([card_type] * count)  # Add 'count' copies of this card
        
        # Randomize card order to ensure unpredictable gameplay
        random.shuffle(deck)
        return deck
    
    def setup_board(self):
        """
        Initialize the game board with a fresh shuffled deck of cards.
        
        Creates a grid of cards (initially 3x3) where each position contains
        a hidden card that players will reveal during their turns. Each cell
        stores both the card type and whether it has been revealed.
        
        If the deck runs out of cards (unlikely with 51 cards for 9 positions),
        Sand cards are used as fallbacks to ensure the board is complete.
        """
        # Get a fresh shuffled deck for this board setup
        deck = self.create_deck()
        
        # Reset board to empty state
        self.board = []
        
        # Create rows x cols grid of hidden cards
        for row in range(self.rows):
            board_row = []  # Initialize new row
            
            for col in range(self.cols):
                if deck:  # If cards remain in deck
                    # Place card from deck with hidden state
                    board_row.append({'card': deck.pop(), 'revealed': False})
                else:
                    # Fallback to Sand card if deck is exhausted (rare)
                    board_row.append({'card': 'Sand', 'revealed': False})
            
            # Add completed row to board
            self.board.append(board_row)
    
    def display_board(self, current_row=None, clear_screen=False):
        """
        Display the current game board in a formatted ASCII box.
        
        Shows a visual representation of the board with:
        - Revealed cards in their assigned colors with card names
        - Hidden cards as letter choices (A, B, C)
        - Proper padding and alignment within a bordered box
        - Header showing current board dimensions
        - Optional row marker showing which row is currently active
        
        The display uses Unicode box-drawing characters for clean borders
        and ANSI color codes to make different card types easily distinguishable.
        
        Args:
            current_row (int, optional): The row index to highlight as current turn
            clear_screen (bool): Whether to clear screen for inline updates
        """
        
        # Clear screen for inline updates if requested
        if clear_screen:
            import os
            os.system('clear' if os.name == 'posix' else 'cls')
        
        # Define box dimensions for consistent formatting
        box_width = 50  # Total box width including left and right borders
        inner_width = box_width - 2  # Available space inside borders
        
        # Get terminal width for centering
        import shutil
        terminal_width = shutil.get_terminal_size().columns
        left_margin = max(0, (terminal_width - box_width) // 2)
        margin = " " * left_margin
        
        # Draw top border of the display box (centered)
        print(f"{margin}┌{'─' * inner_width}┐")
        
        # Create centered header showing current board size
        header_text_plain = f"Shell Dash - Card Game (Rows: {self.rows})"
        header_text_colored = f"\033[94mShell Dash - Card Game\033[0m (Rows: {self.rows})"
        left_pad = (inner_width - len(header_text_plain)) // 2  # Left padding for centering
        right_pad = inner_width - len(header_text_plain) - left_pad  # Right padding
        print(f"{margin}│{' ' * left_pad}{header_text_colored}{' ' * right_pad}│")
        
        # Draw separator line between header and board content
        print(f"{margin}├{'─' * inner_width}┤")
        
        # Prepare player status for side display (one line per player)
        status_lines = []
        for p in range(2):
            player_name = self.player_names[p]
            shells = self.shell_count[p]
            flip_flops = self.flip_flop_count[p]
            player_color = self.player_colors[p + 1]
            shell_color = self.card_colors['Shell'] if shells > 0 else ''
            
            # Combine all player info on one line
            status_line = f"{player_color}{player_name}{self.reset_color}: {shell_color}{shells}🐚/3{self.reset_color} {flip_flops}🩴"
            status_lines.append(status_line)
        
        # Display each row of the game board with status on the right
        for i, row in enumerate(self.board):
            # Create consistent spacing by using fixed-width markers
            if current_row is not None and i == current_row:
                # Current row gets colored arrow marker (using text instead of emoji for consistent width)
                content = f" \033[91m▶\033[0m Row {i+1}: "
                # Calculate visible length excluding ANSI color codes
                visible_length = len(f" ▶ Row {i+1}: ")
            else:
                # Other rows get space padding for alignment
                content = f"   Row {i+1}: "
                visible_length = len(content)
            
            # Process each cell in the current row
            for j, cell in enumerate(row):
                if cell['revealed']:
                    # Show revealed cards with their icons, names and colors
                    color = self.card_colors.get(cell['card'], '')
                    icon = self.card_icons.get(cell['card'], '?')
                    card_display = f"{color}[{icon} {cell['card']}]{self.reset_color} "
                    content += card_display
                    # Calculate visible length (icon is 2 chars, brackets and spaces add to actual card name length)
                    visible_length += len(f"[{cell['card']}] ") + 2  # +2 for emoji visual width
                else:
                    # Show hidden cards as selectable letters (A=0, B=1, C=2)
                    letter = chr(65 + j)  # Convert column index to letter (A, B, C)
                    content += f"[{letter}] "
                    visible_length += len(f"[{letter}] ")
            
            # Calculate padding needed to fill the remaining space in the box
            padding_needed = inner_width - visible_length
            content += " " * padding_needed  # Add spaces to reach box edge
            
            # Add player status on the right side if available
            status_text = ""
            if i < len(status_lines):
                status_text = f"  {status_lines[i]}"
            
            # Print the complete row with borders and status (centered)
            print(f"{margin}│{content}│{status_text}")
            
        # Draw bottom border to close the display box (centered)
        print(f"{margin}└{'─' * inner_width}┘")
    
    def play_turn(self):
        """
        Execute a complete turn for the current player.
        
        A turn consists of:
        1. Display player status (shells collected, flip-flops held)
        2. Navigate through rows by selecting and revealing cards
        3. Handle card effects (advancement, obstacles, special abilities)
        4. Continue until reaching the end or encountering a game-ending obstacle
        5. Reset the board and switch to the next player
        
        The player progresses row by row, with each card type having different effects:
        - Sand: Safe advancement to next row
        - Wave: Must choose another card in the same row
        - Flip-Flop: Gain protection item and advance
        - Jellyfish: End turn (unless Flip-Flop is used)
        - Sun: Expand board and advance
        - Shell: Collect point and advance
        """
        # Display current player and their status with colored name and clear demarcation
        current_name = self.player_names[self.current_player-1]
        player_color = self.player_colors[self.current_player]
        
        # Clear turn demarcation
        print("\n" + "="*60)
        print(f"🎯 {player_color}{current_name}'s Turn{self.reset_color} 🎯")
        print("="*60)
        print(f"Shells collected: {self.shell_count[self.current_player-1]}/3")
        
        # Show available Flip-Flop cards if player has any
        if self.flip_flop_count[self.current_player-1] > 0:
            print(f"You have {self.flip_flop_count[self.current_player-1]} Flip-Flop card(s)!")
        
        # Start player's journey from row 0
        current_row = 0
        
        # Continue until player reaches the end or encounters an obstacle
        while current_row < self.rows:
            # Show the current board state with current row highlighted
            self.display_board(current_row)
            
            # Prompt player for card selection in current row (same line input)
            choice_input = input(f"Choose a card from row {current_row + 1} (A-{chr(64 + self.cols)}, Q to quit): ").upper().strip()
            
            try:
                # Check for quit command
                if choice_input == 'Q':
                    print("Exiting game...")
                    exit()  # Exit the entire program
                
                # Validate input format (single letter within valid range)
                if len(choice_input) != 1 or choice_input < 'A' or choice_input > chr(64 + self.cols):
                    print("Invalid choice!")
                    continue
                
                # Convert letter to column index (A=0, B=1, C=2)
                choice = ord(choice_input) - 65
                
                # Double-check column bounds
                if choice < 0 or choice >= self.cols:
                    print("Invalid choice!")
                    continue
                    
                # Check if card has already been revealed
                if self.board[current_row][choice]['revealed']:
                    print("Card already revealed! Choose another.")
                    continue
                
                # Reveal the selected card and show it to the player
                card = self.board[current_row][choice]['card']
                self.board[current_row][choice]['revealed'] = True
                color = self.card_colors.get(card, '')
                icon = self.card_icons.get(card, '?')
                print(f"\nYou revealed: {color}{icon} {card}{self.reset_color}")
                
                # Process the revealed card according to game rules
                # Each card type has specific effects on player progression
                
                if card == 'Sand':
                    # Sand cards provide safe passage to the next row
                    print("Clear path! Advance to next row.")
                    current_row += 1
                
                elif card == 'Wave':
                    # Wave cards force the player to select another card in the same row
                    # This creates a risk/reward dynamic as other cards might be worse
                    print("Wave! Must choose another card in this row.")
                    
                    # Check if all cards in this row are revealed and all are waves
                    all_revealed = all(cell['revealed'] for cell in self.board[current_row])
                    if all_revealed:
                        all_waves = all(cell['card'] == 'Wave' for cell in self.board[current_row])
                        if all_waves:
                            print("All cards in this row are waves! Turn ends.")
                            break  # End turn
                    
                    continue  # Stay in the same row, don't advance
                
                elif card == 'Flip-Flop':
                    # Flip-Flop cards are protective items that can counter Jellyfish
                    # Players can collect multiple Flip-Flops for future use
                    print("Flip-Flop found! This will help with Jellyfish.")
                    self.flip_flop_count[self.current_player-1] += 1
                    current_row += 1  # Advance after collecting the item
                
                elif card == 'Jellyfish':
                    # Jellyfish are obstacles that end the turn unless countered
                    # Players can use Flip-Flop cards to safely pass them
                    if self.flip_flop_count[self.current_player-1] > 0:
                        # Player has Flip-Flop protection available
                        print(f"Jellyfish! You have {self.flip_flop_count[self.current_player-1]} Flip-Flop(s).")
                        choice = input("Use a Flip-Flop to pass? (y/n): ").lower().strip()
                        
                        if choice == 'y':
                            # Consume one Flip-Flop to safely pass the Jellyfish
                            print("Used Flip-Flop to pass Jellyfish!")
                            self.flip_flop_count[self.current_player-1] -= 1
                            current_row += 1  # Successfully advance
                        else:
                            # Player chooses not to use protection
                            print("Jellyfish sting! Turn ends.")
                            break  # End turn immediately
                    else:
                        # No protection available - turn ends
                        print("Jellyfish sting! Turn ends.")
                        break
                
                elif card == 'Sun':
                    # Sun cards expand the game board, making it longer but adding more opportunities
                    # Expansion is limited to prevent infinite games
                    if self.rows < 6:  # Maximum of 6 rows to keep game manageable
                        self.rows += 3  # Add 3 new rows
                        print(f"Sun card! Added 3 more rows. Total rows: {self.rows}")
                        
                        # Generate new rows with fresh cards from a new deck
                        deck = self.create_deck()
                        for _ in range(3):  # Create 3 new rows
                            new_row = []
                            for col in range(self.cols):  # Fill each column
                                if deck:
                                    # Use cards from the fresh deck
                                    new_row.append({'card': deck.pop(), 'revealed': False})
                                else:
                                    # Fallback if deck is somehow empty
                                    new_row.append({'card': 'Sand', 'revealed': False})
                            self.board.append(new_row)  # Add new row to board
                    # Note: If already at max rows, Sun card still allows advancement
                    current_row += 1
                
                elif card == 'Shell':
                    # Shell cards are the main objective - collect 3 to win
                    print("Shell collected!")
                    self.shell_count[self.current_player-1] += 1
                    current_row += 1  # Advance after collecting
                    
            except (ValueError, IndexError):
                # Handle any unexpected input errors gracefully
                print("Please enter a valid letter!")
                continue
        
        # Check if player successfully traversed all rows
        if current_row >= self.rows:
            current_name = self.player_names[self.current_player-1]
            player_color = self.player_colors[self.current_player]
            print(f"{player_color}{current_name}{self.reset_color} reached the end!")
        
        # Display final board state so player can see their complete path
        self.display_board()
        
        # Player status is now shown alongside the board
        
        # Prepare fresh board for the next player's turn
        # Each player gets a completely new, randomly shuffled board
        self.setup_board()
        
        # Alternate between Player 1 and Player 2
        self.current_player = 2 if self.current_player == 1 else 1
        
    
    def show_player_status(self):
        """
        Display a formatted status summary for both players.
        
        Shows the current progress of each player including:
        - Shell cards collected (main win condition)
        - Flip-Flop cards held (protective items)
        - Visual formatting with colors and borders for clear readability
        
        Shell counts are colored green when > 0 to highlight progress.
        """
        # Create a visually distinct status section
        print("\n" + "="*40)
        print("           PLAYER STATUS")
        print("="*40)
        
        # Display status for each player with colored names
        for i in range(2):
            player_name = self.player_names[i]
            shells = self.shell_count[i]  # Shells collected (win condition)
            flip_flop_count = self.flip_flop_count[i]  # Protection items held
            
            # Get player color and shell color
            player_color = self.player_colors[i + 1]
            shell_color = self.card_colors['Shell'] if shells > 0 else ''
            
            # Display player stats in a clean format with colored name
            print(f"{player_color}{player_name}{self.reset_color}: {shell_color}Shells: {shells}/3{self.reset_color} | Flip-Flop: {flip_flop_count}")
        
        # Close the status section
        print("="*40)
    
    def check_winner(self):
        """
        Check if any player has reached the win condition.
        
        The game is won by collecting 3 Shell cards. This function
        scans both players' shell counts to determine if there's a winner.
        
        Returns:
            int or None: Player number (1 or 2) if they have 3+ shells,
                        None if no winner yet
        """
        # Check each player's shell count for win condition
        for i, shells in enumerate(self.shell_count):
            if shells >= 3:  # Win condition: 3 or more shells
                return i + 1  # Return player number (1-indexed)
        
        return None  # No winner yet
    
    def play(self):
        """
        Main game loop that orchestrates the entire Shell Dash experience.
        
        Manages the complete game flow:
        1. Display welcome message and rules
        2. Alternate player turns until someone wins or players quit
        3. Check for victory condition after each turn
        4. Handle early game termination with score comparison
        5. Declare final winner or draw
        
        The game continues until:
        - A player collects 3 shells (automatic win)
        - Players choose to stop (winner determined by shell count)
        """
        # Clear screen and display welcome message with detailed rules explanation
        import os
        os.system('clear' if os.name == 'posix' else 'cls')
        print("Welcome to \033[94mShell Dash - Card Game\033[0m!")
        print("\n\033[1mGOAL & RULES:\033[0m")
        print("• Collect 3 \033[92m🐚 Shell\033[0m cards to win!")
        print("• Navigate row by row, choosing cards A, B, or C")
        print("• \033[93m🏖️ Sand\033[0m: Safe passage to next row")
        print("• \033[94m🌊 Wave\033[0m: Must choose another card in same row")
        print("• \033[95m🩴 Flip-Flop\033[0m: Protection against Jellyfish")
        print("• \033[91m🪼 Jellyfish\033[0m: Ends turn (unless you use Flip-Flop)")
        print("• \033[33m☀️ Sun\033[0m: Expands the board with 3 more rows")
        print("• \033[92m🐚 Shell\033[0m: Collect and advance - your winning objective!")
        
        # Collect player names
        print("\n\033[1mPLAYER SETUP:\033[0m")
        self.player_names[0] = input("Enter name for Player 1: ").strip() or "Player 1"
        self.player_names[1] = input("Enter name for Player 2: ").strip() or "Player 2"
        p1_color = self.player_colors[1]
        p2_color = self.player_colors[2]
        print(f"\nGreat! {p1_color}{self.player_names[0]}{self.reset_color} vs {p2_color}{self.player_names[1]}{self.reset_color} - Let's begin!")
        
        # Main game loop - continues until win condition or player quits
        while True:
            # Execute one complete turn for current player
            self.play_turn()
            
            # Check if current turn resulted in a victory
            winner = self.check_winner()
            if winner:
                # Immediate victory - player reached 3 shells
                winner_name = self.player_names[winner-1]
                winner_color = self.player_colors[winner]
                print(f"\n🎉 {winner_color}{winner_name}{self.reset_color} wins with 3 shells! 🎉")
                break
            
            # Automatically continue to next turn without asking

# Game entry point - only runs when script is executed directly
if __name__ == "__main__":
    """
    Initialize and start a new Shell Dash game.
    
    This block only executes when the script is run directly,
    not when imported as a module. Creates a game instance
    and starts the main game loop.
    """
    # Create a new game instance with default settings
    game = ShellDashGame()
    
    # Begin the interactive game experience
    game.play()
