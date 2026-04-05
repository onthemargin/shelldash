/**
 * Tests for Shell Dash JavaScript game (shelldash.js).
 *
 * Uses Node.js built-in test runner (node:test) and assert module.
 * DOM-dependent methods are tested with a minimal mock.
 */

const { describe, it, beforeEach } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

// ---------------------------------------------------------------------------
// Load the source file into an isolated context with a minimal DOM mock
// ---------------------------------------------------------------------------

function createMockDOM() {
    const elements = {};
    const mockElement = (id) => ({
        id,
        innerHTML: '',
        innerText: '',
        value: '',
        scrollTop: 0,
        scrollHeight: 0,
        style: {},
        className: '',
        classList: {
            _classes: new Set(),
            add(c) { this._classes.add(c); },
            remove(c) { this._classes.delete(c); },
            contains(c) { return this._classes.has(c); },
        },
        firstChild: null,
        removeChild() { this.firstChild = null; },
        appendChild() {},
        addEventListener() {},
        disabled: false,
    });

    return {
        getElementById(id) {
            if (!elements[id]) {
                elements[id] = mockElement(id);
            }
            return elements[id];
        },
        createElement() {
            return mockElement('_dynamic');
        },
    };
}

function loadShellDash() {
    const src = fs.readFileSync(
        path.join(__dirname, 'shelldash.js'),
        'utf-8'
    );

    const document = createMockDOM();

    // The source defines ShellDash as a class declaration (not assigned to a var
    // visible from the outside in strict vm contexts). We append a line to
    // explicitly expose it on the sandbox object.
    const patchedSrc = src + '\nthis.ShellDash = ShellDash;\n';

    const context = vm.createContext({
        document,
        console,
        setTimeout: globalThis.setTimeout,
        clearTimeout: globalThis.clearTimeout,
        String,
        Math,
        Array,
        JSON,
        Object,
        Set,
    });

    vm.runInContext(patchedSrc, context);
    return context.ShellDash;
}

const ShellDash = loadShellDash();

// ---------------------------------------------------------------------------
// createDeck()
// ---------------------------------------------------------------------------

describe('createDeck', () => {
    it('returns 51 cards', () => {
        const game = new ShellDash();
        const deck = game.createDeck();
        assert.equal(deck.length, 51);
    });

    it('has correct card distribution', () => {
        const game = new ShellDash();
        const deck = game.createDeck();
        const counts = {};
        for (const card of deck) {
            counts[card] = (counts[card] || 0) + 1;
        }
        assert.deepEqual(counts, {
            Sand: 20,
            Wave: 10,
            'Flip-Flop': 6,
            Jellyfish: 6,
            Sun: 5,
            Shell: 4,
        });
    });

    it('only contains valid card types', () => {
        const game = new ShellDash();
        const deck = game.createDeck();
        const valid = new Set(game.cards);
        for (const card of deck) {
            assert.ok(valid.has(card), `Unexpected card type: ${card}`);
        }
    });

    it('shuffles the deck (not always the same order)', () => {
        const game = new ShellDash();
        const deck1 = game.createDeck();
        let allSame = true;
        for (let i = 0; i < 5; i++) {
            const deck2 = game.createDeck();
            if (JSON.stringify(deck1) !== JSON.stringify(deck2)) {
                allSame = false;
                break;
            }
        }
        assert.ok(!allSame, 'Deck should be shuffled differently across calls');
    });
});

// ---------------------------------------------------------------------------
// setupBoard()
// ---------------------------------------------------------------------------

describe('setupBoard', () => {
    it('creates a 3x3 board by default', () => {
        const game = new ShellDash();
        assert.equal(game.board.length, 3);
        for (const row of game.board) {
            assert.equal(row.length, 3);
        }
    });

    it('all cells have card and revealed properties', () => {
        const game = new ShellDash();
        for (const row of game.board) {
            for (const cell of row) {
                assert.ok('card' in cell);
                assert.ok('revealed' in cell);
            }
        }
    });

    it('all cards start hidden', () => {
        const game = new ShellDash();
        for (const row of game.board) {
            for (const cell of row) {
                assert.equal(cell.revealed, false);
            }
        }
    });

    it('all cards are valid types', () => {
        const game = new ShellDash();
        const valid = new Set(game.cards);
        for (const row of game.board) {
            for (const cell of row) {
                assert.ok(valid.has(cell.card));
            }
        }
    });

    it('respects custom row count', () => {
        const game = new ShellDash();
        game.rows = 5;
        game.setupBoard();
        assert.equal(game.board.length, 5);
    });
});

// ---------------------------------------------------------------------------
// checkWinner()
// ---------------------------------------------------------------------------

describe('checkWinner', () => {
    it('returns null when no one has shells', () => {
        const game = new ShellDash();
        assert.equal(game.checkWinner(), null);
    });

    it('returns null with partial shells', () => {
        const game = new ShellDash();
        game.shellCount = [2, 1];
        assert.equal(game.checkWinner(), null);
    });

    it('returns 1 when player 1 has 3 shells', () => {
        const game = new ShellDash();
        game.shellCount = [3, 0];
        assert.equal(game.checkWinner(), 1);
    });

    it('returns 2 when player 2 has 3 shells', () => {
        const game = new ShellDash();
        game.shellCount = [0, 3];
        assert.equal(game.checkWinner(), 2);
    });

    it('returns 1 when player 1 has more than 3 shells', () => {
        const game = new ShellDash();
        game.shellCount = [4, 2];
        assert.equal(game.checkWinner(), 1);
    });

    it('returns 1 when both have 3 (player 1 checked first)', () => {
        const game = new ShellDash();
        game.shellCount = [3, 3];
        assert.equal(game.checkWinner(), 1);
    });
});

// ---------------------------------------------------------------------------
// processCard() — core game logic
// ---------------------------------------------------------------------------

describe('processCard', () => {
    /** Helper: create a game with a specific board so processCard works. */
    function gameWithBoard(grid) {
        const game = new ShellDash();
        game.rows = grid.length;
        game.cols = grid[0].length;
        game.board = grid.map(row =>
            row.map(card => ({ card, revealed: false }))
        );
        game.currentRow = 0;
        game.shellCount = [0, 0];
        game.flipFlopCount = [0, 0];
        game.currentPlayer = 1;
        game.gameOver = false;
        game.waitingForJellyfishChoice = false;
        return game;
    }

    it('Sand advances to next row', () => {
        const game = gameWithBoard([
            ['Sand', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
        ]);
        game.processCard('Sand');
        assert.equal(game.currentRow, 1);
    });

    it('Wave does not advance the row', () => {
        const game = gameWithBoard([
            ['Wave', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
        ]);
        game.processCard('Wave');
        assert.equal(game.currentRow, 0);
    });

    it('Flip-Flop increments flip-flop count and advances', () => {
        const game = gameWithBoard([
            ['Flip-Flop', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
        ]);
        game.processCard('Flip-Flop');
        assert.equal(game.flipFlopCount[0], 1);
        assert.equal(game.currentRow, 1);
    });

    it('Shell increments shell count and advances', () => {
        const game = gameWithBoard([
            ['Shell', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
        ]);
        game.processCard('Shell');
        assert.equal(game.shellCount[0], 1);
        assert.equal(game.currentRow, 1);
    });

    it('Shell for player 2 increments correct index', () => {
        const game = gameWithBoard([
            ['Shell', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
        ]);
        game.currentPlayer = 2;
        game.processCard('Shell');
        assert.equal(game.shellCount[1], 1);
        assert.equal(game.shellCount[0], 0);
    });

    it('Sun expands board from 3 to 6 rows', () => {
        const game = gameWithBoard([
            ['Sun', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
        ]);
        game.processCard('Sun');
        assert.equal(game.rows, 6);
        assert.equal(game.board.length, 6);
        assert.equal(game.currentRow, 1);
    });

    it('Sun does not expand beyond 6 rows', () => {
        const game = gameWithBoard([
            ['Sun', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
        ]);
        game.rows = 6;
        game.processCard('Sun');
        // Should not expand, but should still advance
        assert.equal(game.rows, 6);
        assert.equal(game.board.length, 6);
        assert.equal(game.currentRow, 1);
    });

    it('Jellyfish without flip-flop triggers sting (endTurn called)', () => {
        const game = gameWithBoard([
            ['Jellyfish', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
        ]);
        game.flipFlopCount = [0, 0];
        game.processCard('Jellyfish');
        // Row should NOT advance on jellyfish sting
        assert.equal(game.currentRow, 0);
    });

    it('Jellyfish with flip-flop triggers waiting state', () => {
        const game = gameWithBoard([
            ['Jellyfish', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
        ]);
        game.flipFlopCount = [1, 0];
        game.processCard('Jellyfish');
        assert.equal(game.waitingForJellyfishChoice, true);
    });

    it('All-wave row ends turn', () => {
        const game = gameWithBoard([
            ['Wave', 'Wave', 'Wave'],
            ['Sand', 'Sand', 'Sand'],
            ['Sand', 'Sand', 'Sand'],
        ]);
        // Reveal all cards in row 0
        for (const cell of game.board[0]) {
            cell.revealed = true;
        }
        game.processCard('Wave');
        // Row should not have advanced
        assert.equal(game.currentRow, 0);
    });
});

// ---------------------------------------------------------------------------
// Game initialization
// ---------------------------------------------------------------------------

describe('game initialization', () => {
    it('shell counts start at zero', () => {
        const game = new ShellDash();
        assert.equal(game.shellCount[0], 0);
        assert.equal(game.shellCount[1], 0);
        assert.equal(game.shellCount.length, 2);
    });

    it('flip-flop counts start at zero', () => {
        const game = new ShellDash();
        assert.equal(game.flipFlopCount[0], 0);
        assert.equal(game.flipFlopCount[1], 0);
        assert.equal(game.flipFlopCount.length, 2);
    });

    it('current player starts at 1', () => {
        const game = new ShellDash();
        assert.equal(game.currentPlayer, 1);
    });

    it('default rows and cols are 3', () => {
        const game = new ShellDash();
        assert.equal(game.rows, 3);
        assert.equal(game.cols, 3);
    });

    it('game is not over at start', () => {
        const game = new ShellDash();
        assert.equal(game.gameOver, false);
    });

    it('all card types have icons', () => {
        const game = new ShellDash();
        for (const card of game.cards) {
            assert.ok(card in game.cardIcons, `Missing icon for ${card}`);
        }
    });
});

// ---------------------------------------------------------------------------
// startNewGame()
// ---------------------------------------------------------------------------

describe('startNewGame', () => {
    it('resets shell and flip-flop counts', () => {
        const game = new ShellDash();
        game.shellCount = [2, 1];
        game.flipFlopCount = [3, 1];
        game.startNewGame('Alice', 'Bob');
        assert.equal(game.shellCount[0], 0);
        assert.equal(game.shellCount[1], 0);
        assert.equal(game.flipFlopCount[0], 0);
        assert.equal(game.flipFlopCount[1], 0);
    });

    it('sets player names', () => {
        const game = new ShellDash();
        game.startNewGame('Alice', 'Bob');
        assert.equal(game.playerNames[0], 'Alice');
        assert.equal(game.playerNames[1], 'Bob');
    });

    it('uses defaults for empty names', () => {
        const game = new ShellDash();
        game.startNewGame('', '');
        assert.equal(game.playerNames[0], 'Player 1');
        assert.equal(game.playerNames[1], 'Player 2');
    });

    it('resets game state', () => {
        const game = new ShellDash();
        game.gameOver = true;
        game.currentRow = 5;
        game.rows = 6;
        game.currentPlayer = 2;
        game.startNewGame('A', 'B');
        assert.equal(game.gameOver, false);
        assert.equal(game.currentRow, 0);
        assert.equal(game.rows, 3);
        assert.equal(game.currentPlayer, 1);
    });
});

// ---------------------------------------------------------------------------
// renderBoard() — touch event support for mobile
// ---------------------------------------------------------------------------

describe('renderBoard mobile support', () => {
    /** Helper: create a richer mock DOM that tracks event listeners */
    function createTrackingDOM() {
        const elements = {};
        const createdElements = [];

        const mockElement = (id) => {
            const listeners = {};
            const el = {
                id,
                innerHTML: '',
                innerText: '',
                value: '',
                scrollTop: 0,
                scrollHeight: 0,
                style: {},
                className: '',
                classList: {
                    _classes: new Set(),
                    add(c) { this._classes.add(c); },
                    remove(c) { this._classes.delete(c); },
                    contains(c) { return this._classes.has(c); },
                },
                children: [],
                firstChild: null,
                removeChild() { this.firstChild = null; this.children = []; },
                appendChild(child) { this.children.push(child); this.firstChild = this.firstChild || child; },
                addEventListener(event, handler) {
                    if (!listeners[event]) listeners[event] = [];
                    listeners[event].push(handler);
                },
                _listeners: listeners,
                disabled: false,
            };
            return el;
        };

        return {
            getElementById(id) {
                if (!elements[id]) {
                    elements[id] = mockElement(id);
                }
                return elements[id];
            },
            createElement() {
                const el = mockElement('_dynamic_' + createdElements.length);
                createdElements.push(el);
                return el;
            },
            _createdElements: createdElements,
        };
    }

    it('no inline onclick handlers in HTML (CSP compliance)', () => {
        const html = fs.readFileSync(path.join(__dirname, 'shelldash.html'), 'utf-8');
        const onclickMatches = html.match(/onclick\s*=/gi) || [];
        assert.equal(onclickMatches.length, 0, 'HTML should not use inline onclick handlers (blocked by CSP script-src self)');
    });

    it('attaches touchend listeners to clickable cards', () => {
        // Load a fresh instance with tracking DOM
        const src = fs.readFileSync(path.join(__dirname, 'shelldash.js'), 'utf-8');
        const trackingDoc = createTrackingDOM();
        const patchedSrc = src + '\nthis.ShellDash = ShellDash;\n';
        const context = vm.createContext({
            document: trackingDoc,
            console,
            setTimeout: globalThis.setTimeout,
            clearTimeout: globalThis.clearTimeout,
            String, Math, Array, JSON, Object, Set,
        });
        vm.runInContext(patchedSrc, context);
        const SD = context.ShellDash;

        const game = new SD();
        game.startNewGame('A', 'B');

        // Find card elements created for the current row (row 0)
        // Cards in current row should have both click and touchend listeners
        const cardElements = trackingDoc._createdElements.filter(el =>
            el._listeners['touchend'] && el._listeners['touchend'].length > 0
        );

        assert.ok(cardElements.length > 0, 'Clickable cards should have touchend listeners for mobile');
    });
});
