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
        """
        Set tile occupant to character
        """
        ...

    def mark_unoccupied(self):
        """
        Remove occupant from tile
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

    def render_tile(self):
        ...

    def render_to_screen(self):
        ...

    def run(self):
        ...