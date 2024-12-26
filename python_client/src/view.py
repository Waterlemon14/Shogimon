import pygame
from project_types import (Movement, Piece, Player)

class Eevee(Piece):
    def __init__(self):
        ...

    def is_captured(self) -> bool:
        ...

    def possible_moves(self) -> list:
        ...

class Pikachu(Piece):
    def __init__(self):
        ...

    def is_captured(self) -> bool:
        ...

    def possible_moves(self) -> list:
        ...

class Tile:
    def __init__(self, x: int, y: int):
        self._x = x
        self._y = y
        self._width = 64
        self._height = 64
        # self._occupant = Character()

    def mark_occupied(self, piece: Piece):
        """
        Set tile occupant to character
        """
        ...

    def mark_empty(self):
        """
        Render tile as empty
        """
        ...

    def render_to_screen(self):
        """
        Render to screen -- get from GameView
        """
        ...

class GameView:
    def __init__(self):
        self._width = 1280
        self._height = 720

        pygame.font.init()
        self._font = pygame.font.SysFont('Arial', 25)

    def render_all(self):
        ...

    def run(self):
        ...