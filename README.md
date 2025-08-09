# Shell Dash 🐚

A terminal-based card adventure game where two players race to collect 3 shell cards while navigating through randomly generated boards filled with obstacles and power-ups.

**Author:** On The Margin

## 🎮 Game Overview

Shell Dash is a turn-based strategy game where players navigate through a grid of hidden cards, each with different effects. The first player to collect 3 Shell cards wins!

> **Original Game:** This digital implementation is based on the physical card game by [Manzanita Game Co.](https://www.manzanitagameco.com/shell-dash-card-game.html). All credit for the original game design and mechanics goes to the original creators.

### Card Types

- **🏖️ Sand** - Safe passage to the next row
- **🌊 Wave** - Forces you to choose another card in the same row
- **🩴 Flip-Flop** - Protective gear against Jellyfish
- **🪼 Jellyfish** - Ends your turn (unless you have Flip-Flop protection)
- **☀️ Sun** - Expands the board with 3 additional rows
- **🐚 Shell** - Collectible win condition (need 3 to win)

## 🚀 How to Play

1. Run the game: `python shelldash.py`
2. Enter player names when prompted
3. Take turns choosing cards (A, B, or C) from each row
4. Navigate through obstacles and collect shells
5. First player to collect 3 shells wins!

## 📋 Requirements

- Python 3.6+
- Terminal with Unicode and ANSI color support

## 🎯 Game Rules

- Players alternate turns navigating from top to bottom
- Each turn, players reveal cards by choosing columns (A, B, C)
- Different cards have different effects on progression
- Collect Flip-Flops to protect against Jellyfish
- Sun cards expand the board, giving more opportunities
- Game ends when a player collects 3 Shell cards

## 🎲 Deck Composition

The game uses a 51-card deck with the following distribution:
- 20 Sand cards
- 10 Wave cards
- 6 Flip-Flop cards
- 6 Jellyfish cards
- 5 Sun cards
- 4 Shell cards

## 🖥️ Features

- Colorful terminal interface with Unicode emojis
- Dynamic board expansion
- Player status tracking
- Turn-based gameplay with clear visual feedback
- Centered display formatting

---

## 📄 License

MIT License

Copyright (c) 2025 On The Margin

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## ⚠️ Educational Disclaimer

**This project is created for educational purposes only.** It is intended to demonstrate:
- Python programming concepts
- Game logic implementation
- Terminal-based user interfaces
- Object-oriented programming principles

This software is provided as-is for learning and educational use. Please use responsibly.

