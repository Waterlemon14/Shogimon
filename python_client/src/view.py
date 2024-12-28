import pygame

from project_types import (PieceKind, GameState, Movement, MakeTurnObserver, NewGameObserver, PlayerNumber)
from model import Piece

SCREEN_WIDTH = 700
SCREEN_HEIGHT = 700

class Captures:
    """
    To show captured pieces of each player
    """
    def __init__(self, number: PlayerNumber):
        self._captures: list[PieceKind] = []
        self._capture_owner = number

    @property
    def get_captures(self) -> list[PieceKind]:
        return self._captures
    
    @property
    def get_player_owner(self) -> PlayerNumber:
        return self._capture_owner
    
    def render_captures(self):
        match self._capture_owner:
            case PlayerNumber.ONE:
                ...
                
            case PlayerNumber.TWO:
                ...

class Tile:
    """
    piece will be a link to an img

    load img in pygame:
    pygame.image.load("C:\\Users\\DELL\\Downloads\\gfg.png").convert()
    """
    def __init__(self, piecekind: PieceKind, x: int, y: int):
        self._x = x
        self._y = y
        self._piecekind: PieceKind | None = piecekind
        self._width = 64
        self._height = 64
        self._targetable = False

    def mark_occupied(self, piecekind: PieceKind):
        """
        show img in tile
        """
        self._piecekind = piecekind

    def mark_empty(self):
        """
        remove img from tile
        """
        self._piecekind = None

    def mark_targetable(self):
        self._targetable = True

    def unmark_targetable(self):
        self._targetable = False

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

    def render_piece(self, piece: Piece):
        """
        Some method that will map each Piece object to an image for the view
        """
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