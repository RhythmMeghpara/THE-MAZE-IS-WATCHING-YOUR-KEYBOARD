# THE-MAZE-IS-WATCHING-YOUR-KEYBOARD

A Python maze game built with Pygame. The player chooses a custom letter and difficulty mode, then navigates a maze shaped like that letter to reach the exit.

## Features

- Custom letter input for maze shape
- Three difficulty modes: Explorer, Adventurer, Master
- Randomized maze generation inside the letter mask
- Timer displayed during gameplay
- Monster chase mode in Master difficulty

## Requirements

- Python 3
- Pygame

## Run the Game

1. Install Pygame: `pip install pygame`
2. Run `Maze game.py`

## Controls

- Arrow keys to move
- Enter to confirm letter input

## Notes

- The exit is placed at the farthest reachable cell from the player.
- The Master mode adds a moving monster that chases the player.
