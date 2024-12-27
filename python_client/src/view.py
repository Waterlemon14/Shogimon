import pygame

from project_types import (GameState, Movement, Player, MakeTurnObserver, NewGameObserver)
from model import Piece

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 1280

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
        self._occupant: Piece | None = None

    def mark_occupied(self, piece: Piece):
        self._occupant = piece

    def mark_empty(self):
        self._occupant = None

    def render_to_screen(self, screen: pygame.Surface):
        """
        Render to screen --- take screen from GameView
        """
        ...

class GameView:
    def __init__(self):
        self._width = SCREEN_WIDTH
        self._height = SCREEN_HEIGHT
        self._make_turn_observers: list[MakeTurnObserver] = []
        self._new_game_observers: list[NewGameObserver] = []

        pygame.font.init()
        self._font = pygame.font.SysFont('Arial', 25)

    def register_make_turn_observer(self, observer: MakeTurnObserver):
        self._make_turn_observers.append(observer)

    def register_new_game_observer(self, observer: NewGameObserver):
        self._new_game_observers.append(observer)

    def on_state_change(self, state: GameState):
        ...

    def render_all(self):
        """
        Render all game components
        """
        ...

    def run(self):
        pygame.init()

        self._screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._clock = pygame.time.Clock()

        _game_is_running = True

        while _game_is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    _game_is_running = False

                elif event.type == pygame.KEYDOWN:
                    ...

            self._screen.fill('#FFFFFF')

            ...

            pygame.display.flip()
            self._clock.tick(30)

        pygame.quit()