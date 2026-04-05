class ShellDash {
    constructor() {
        this.cards = ['Sand', 'Wave', 'Flip-Flop', 'Jellyfish', 'Sun', 'Shell'];
        this.cardCounts = [20, 10, 6, 6, 5, 4];
        this.cardIcons = {
            'Sand': '🏖️',
            'Wave': '🌊',
            'Flip-Flop': '🩴',
            'Jellyfish': '🪼',
            'Sun': '☀️',
            'Shell': '🐚'
        };

        this.board = [];
        this.rows = 3;
        this.cols = 3;
        this.currentPlayer = 1;
        this.playerNames = ["Player 1", "Player 2"];
        this.shellCount = [0, 0];
        this.flipFlopCount = [0, 0];
        this.currentRow = 0;
        this.gameOver = false;
        this.waitingForJellyfishChoice = false;
        this.jellyfishTimeout = null;

        this.setupBoard();
    }

    createDeck() {
        const deck = [];
        for (let i = 0; i < this.cards.length; i++) {
            const cardType = this.cards[i];
            const count = this.cardCounts[i];
            for (let j = 0; j < count; j++) {
                deck.push(cardType);
            }
        }

        // Shuffle deck
        for (let i = deck.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [deck[i], deck[j]] = [deck[j], deck[i]];
        }

        return deck;
    }

    setupBoard() {
        const deck = this.createDeck();
        this.board = [];

        for (let row = 0; row < this.rows; row++) {
            const boardRow = [];
            for (let col = 0; col < this.cols; col++) {
                if (deck.length > 0) {
                    boardRow.push({ card: deck.pop(), revealed: false });
                } else {
                    boardRow.push({ card: 'Sand', revealed: false });
                }
            }
            this.board.push(boardRow);
        }

    }

    logMessage(message) {
        const log = document.getElementById("game-log");
        log.innerHTML += `<div>${message}</div>`;
        log.scrollTop = log.scrollHeight;
    }

    updatePlayerDisplay() {
        for (let i = 0; i < 2; i++) {
            const playerNum = i + 1;
            document.getElementById(`player${playerNum}-display`).innerText = this.playerNames[i];
            document.getElementById(`player${playerNum}-shells`).innerText = this.shellCount[i];
            document.getElementById(`player${playerNum}-flipflops`).innerText = this.flipFlopCount[i];

            const playerCard = document.getElementById(`player${playerNum}-info`);
            if (playerNum === this.currentPlayer) {
                playerCard.classList.add("current");
            } else {
                playerCard.classList.remove("current");
            }
        }
    }

    renderBoard() {
        const boardElement = document.getElementById("game-board");

        // Completely clear the board and remove all event listeners
        while (boardElement.firstChild) {
            boardElement.removeChild(boardElement.firstChild);
        }

        for (let rowIdx = 0; rowIdx < this.board.length; rowIdx++) {
            const row = this.board[rowIdx];
            const rowDiv = document.createElement("div");
            rowDiv.className = "board-row";

            for (let colIdx = 0; colIdx < row.length; colIdx++) {
                const cell = row[colIdx];
                const cardDiv = document.createElement("div");
                cardDiv.className = "card";

                if (cell.revealed) {
                    const cardType = cell.card.toLowerCase().replace('-', '');
                    cardDiv.classList.add(cardType, "revealed");
                    const icon = this.cardIcons[cell.card] || '?';
                    cardDiv.innerHTML = `${icon}<br>${cell.card}`;
                } else {
                    cardDiv.classList.add("hidden");
                    const letter = String.fromCharCode(65 + colIdx); // A, B, C
                    cardDiv.innerHTML = letter;

                    // Add click handler for hidden cards in current row
                    if (rowIdx === this.currentRow && !this.gameOver && !this.waitingForJellyfishChoice) {
                        cardDiv.classList.add("clickable");

                        // Apply reasonable z-index for game context
                        cardDiv.style.zIndex = "200";
                        cardDiv.style.pointerEvents = "auto";
                        cardDiv.style.cursor = "pointer";

                        // Add click and touch handlers for mobile support
                        const self = this;
                        const handler = function(e) {
                            self.selectCard(colIdx);
                        };
                        cardDiv.addEventListener('click', handler);
                        cardDiv.addEventListener('touchend', function(e) {
                            e.preventDefault();
                            self.selectCard(colIdx);
                        });
                    } else {
                        cardDiv.style.cursor = "not-allowed";
                        cardDiv.style.opacity = "0.5";
                    }
                }

                rowDiv.appendChild(cardDiv);
            }

            boardElement.appendChild(rowDiv);
        }

    }

    updateCurrentRowIndicator() {
        if (!this.gameOver) {
            const indicator = document.getElementById("current-row-indicator");
            if (this.currentRow < this.rows) {
                indicator.innerText = `Choose a card from Row ${this.currentRow + 1}`;
            } else {
                indicator.innerText = "Turn complete!";
            }
        }
    }

    selectCard(col) {
        if (this.gameOver || this.waitingForJellyfishChoice) {
            return;
        }

        if (this.currentRow >= this.rows) {
            return;
        }

        if (!this.board || !this.board[this.currentRow] || !this.board[this.currentRow][col]) {
            return;
        }

        if (this.board[this.currentRow][col].revealed) {
            this.logMessage("Card already revealed! Choose another.");
            return;
        }

        const card = this.board[this.currentRow][col].card;
        this.board[this.currentRow][col].revealed = true;

        const icon = this.cardIcons[card] || '?';
        this.logMessage(`${this.playerNames[this.currentPlayer-1]} revealed: ${icon} ${card}`);

        // Update the board display immediately to show the revealed card
        this.renderBoard();
        this.updatePlayerDisplay();
        this.updateCurrentRowIndicator();

        // Process card immediately
        this.processCard(card);
    }

    processCard(card) {
        switch (card) {
            case 'Sand':
                this.logMessage("Clear path! Advance to next row.");
                this.currentRow++;
                break;

            case 'Wave':
                this.logMessage("Wave! Must choose another card in this row.");
                const allRevealed = this.board[this.currentRow].every(cell => cell.revealed);
                if (allRevealed) {
                    const allWaves = this.board[this.currentRow].every(cell => cell.card === 'Wave');
                    if (allWaves) {
                        this.logMessage("All cards in this row are waves! Turn ends.");
                        this.endTurn("🌊 Caught in an endless wave! Turn ends!");
                    }
                }
                break;

            case 'Flip-Flop':
                this.logMessage("Flip-Flop found! This will help with Jellyfish.");
                this.flipFlopCount[this.currentPlayer-1]++;
                this.currentRow++;
                break;

            case 'Jellyfish':
                if (this.flipFlopCount[this.currentPlayer-1] > 0) {
                    this.logMessage(`Jellyfish! You have ${this.flipFlopCount[this.currentPlayer-1]} Flip-Flop(s).`);
                    this.waitingForJellyfishChoice = true;
                    document.getElementById("use-flipflop-btn").disabled = false;
                    this.logMessage("Click 'Use Flip-Flop' to pass, or wait 3 seconds to get stung.");
                    if (this.jellyfishTimeout) clearTimeout(this.jellyfishTimeout);
                    this.jellyfishTimeout = setTimeout(() => this.autoJellyfishSting(), 3000);
                } else {
                    this.logMessage("Jellyfish sting! Turn ends.");
                    this.endTurn("🪼 Jellyfish sting! Turn ends!");
                }
                break;

            case 'Sun':
                if (this.rows < 6) {
                    this.rows += 3;
                    this.logMessage(`Sun card! Added 3 more rows. Total rows: ${this.rows}`);

                    const deck = this.createDeck();
                    for (let i = 0; i < 3; i++) {
                        const newRow = [];
                        for (let col = 0; col < this.cols; col++) {
                            if (deck.length > 0) {
                                newRow.push({ card: deck.pop(), revealed: false });
                            } else {
                                newRow.push({ card: 'Sand', revealed: false });
                            }
                        }
                        this.board.push(newRow);
                    }
                }
                this.currentRow++;
                break;

            case 'Shell':
                this.logMessage("Shell collected!");
                this.shellCount[this.currentPlayer-1]++;
                this.currentRow++;
                break;
        }

        if (this.currentRow >= this.rows) {
            this.logMessage(`${this.playerNames[this.currentPlayer-1]} reached the end!`);
            this.endTurn("🏁 Reached the end! Turn complete!");
        }

        const winner = this.checkWinner();
        if (winner) {
            this.showWinner(winner);
        }

        // Update the board display after processing the card
        this.renderBoard();
        this.updatePlayerDisplay();
        this.updateCurrentRowIndicator();
    }

    useFlipFlop() {
        if (!this.waitingForJellyfishChoice) {
            return;
        }

        this.waitingForJellyfishChoice = false;
        document.getElementById("use-flipflop-btn").disabled = true;
        if (this.jellyfishTimeout) clearTimeout(this.jellyfishTimeout);

        this.logMessage("Used Flip-Flop to pass Jellyfish!");
        this.flipFlopCount[this.currentPlayer-1]--;
        this.currentRow++;

        if (this.currentRow >= this.rows) {
            this.logMessage(`${this.playerNames[this.currentPlayer-1]} reached the end!`);
            this.endTurn("🏁 Reached the end! Turn complete!");
        }

        this.renderBoard();
        this.updatePlayerDisplay();
        this.updateCurrentRowIndicator();

        const winner = this.checkWinner();
        if (winner) {
            this.showWinner(winner);
        }
    }

    autoJellyfishSting() {
        if (this.waitingForJellyfishChoice) {
            this.waitingForJellyfishChoice = false;
            document.getElementById("use-flipflop-btn").disabled = true;
            if (this.jellyfishTimeout) clearTimeout(this.jellyfishTimeout);
            this.logMessage("Too slow! Jellyfish sting! Turn ends.");
            this.endTurn("⏰ Too slow! Jellyfish sting!");
        }
    }

    endTurn(reason = "Turn ended") {
        const nextPlayer = this.currentPlayer === 1 ? 2 : 1;
        const nextPlayerName = this.playerNames[nextPlayer-1];

        // Show transition popup
        this.showTurnTransition(reason, nextPlayerName);

        // Wait for popup to finish before continuing
        setTimeout(() => {
            this.setupBoard();
            this.currentRow = 0;
            this.currentPlayer = nextPlayer;
            this.logMessage(`--- ${this.playerNames[this.currentPlayer-1]}'s turn ---`);

            this.renderBoard();
            this.updatePlayerDisplay();
            this.updateCurrentRowIndicator();
        }, 3000);
    }

    checkWinner() {
        for (let i = 0; i < this.shellCount.length; i++) {
            if (this.shellCount[i] >= 3) {
                return i + 1;
            }
        }
        return null;
    }

    showWinner(winner) {
        this.gameOver = true;
        const winnerName = this.playerNames[winner-1];

        const winnerScreen = document.getElementById("winner-screen");
        const winnerMessage = document.getElementById("winner-message");
        winnerMessage.innerHTML = `🎉 ${winnerName} wins with 3 shells! 🎉`;
        winnerScreen.classList.remove("hidden");
    }

    showTurnTransition(reason, nextPlayerName) {
        const transitionElement = document.getElementById("turn-transition");
        const reasonElement = document.getElementById("turn-reason");
        const nextPlayerElement = document.getElementById("turn-next-player");

        reasonElement.innerHTML = reason;
        nextPlayerElement.innerHTML = `${nextPlayerName}'s Turn`;

        // Show the popup
        transitionElement.classList.remove("hidden");
        setTimeout(() => {
            transitionElement.classList.add("show");
        }, 10);

        // Hide after 2.5 seconds
        setTimeout(() => {
            transitionElement.classList.remove("show");
            setTimeout(() => {
                transitionElement.classList.add("hidden");
            }, 300);
        }, 2500);
    }

    startNewGame(player1Name, player2Name) {
        this.playerNames = [player1Name || "Player 1", player2Name || "Player 2"];
        this.shellCount = [0, 0];
        this.flipFlopCount = [0, 0];
        this.currentPlayer = 1;
        this.currentRow = 0;
        this.rows = 3;
        this.gameOver = false;
        this.waitingForJellyfishChoice = false;

        this.setupBoard();

        document.getElementById("game-log").innerHTML = "<div>Game started! Good luck!</div>";
        this.logMessage(`--- ${this.playerNames[0]}'s turn ---`);

        document.getElementById("winner-screen").classList.add("hidden");

        this.renderBoard();
        this.updatePlayerDisplay();
        this.updateCurrentRowIndicator();
    }
}

// Global game instance
let game = null;

function startGame() {
    const player1Name = document.getElementById("player1-name").value.trim();
    const player2Name = document.getElementById("player2-name").value.trim();

    document.getElementById("setup-screen").classList.add("hidden");
    document.getElementById("game-screen").classList.remove("hidden");

    game = new ShellDash();
    game.startNewGame(player1Name, player2Name);
}

function newGame() {
    document.getElementById("game-screen").classList.add("hidden");
    document.getElementById("setup-screen").classList.remove("hidden");

    document.getElementById("player1-name").value = "";
    document.getElementById("player2-name").value = "";
}

function useFlipFlop() {
    if (game) {
        game.useFlipFlop();
    }
}

// Wire up button event listeners (CSP blocks inline onclick handlers)
document.getElementById("start-game-btn").addEventListener("click", startGame);
document.getElementById("play-again-btn").addEventListener("click", newGame);
document.getElementById("new-game-btn").addEventListener("click", newGame);
document.getElementById("use-flipflop-btn").addEventListener("click", useFlipFlop);
