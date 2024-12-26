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
        self._x = x
        self._y = y
        self._width = 64
        self._height = 64
        # self._occupant = Character()

    def mark_occupied(self, char: Character):
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

    def render_tile(self):
        ...

    def render_to_screen(self):
        ...

    def run(self):
        ...