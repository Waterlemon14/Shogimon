import pygame

class Character:
    def __init__(self):
        ...

    def render_to_tile(self):
        """
        Render to respective tile
        """
        ...

class Tile:
    def __init__(self, x: int, y: int):
        ...

    def mark_occupied(self, char: Character):
        ...

    def mark_unoccupied(self):
        ...

    def render_to_screen(self):
        """
        Render to screen -- get from GameView
        """
        ...

class GameView:
    def __init__(self):
        ...

    def render_tile(self):
        ...

    def render_to_screen(self):
        ...