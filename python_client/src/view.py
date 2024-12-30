import pygame

from project_types import (
    TILE_PIXELS, BOARD_ROWS, BOARD_COLS, LivePiece,
    PieceKind, Location, GameState, Movement,
    PlayerNumber,
    MakeTurnObserver, NewGameObserver,
    )

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

BOARD_WIDTH = TILE_PIXELS*BOARD_ROWS
BOARD_HEIGHT = TILE_PIXELS*BOARD_COLS

class Captures:
    """Renderable class for player captures (top and bottom of game screen)"""
    def __init__(self, number: PlayerNumber):
        self._captures: list[PieceKind] = []
        self._capture_owner = number

    @property
    def get_captures(self) -> list[PieceKind]:
        return self._captures
    
    @property
    def get_player_owner(self) -> PlayerNumber:
        return self._capture_owner
    
    def render_to_screen(self, screen: pygame.Surface):
        actual_captures = pygame.Surface((BOARD_WIDTH, TILE_PIXELS))

        match self._capture_owner:
            case PlayerNumber.ONE:
                ...
                _blittable = actual_captures.get_rect(midbottom=(...))
                
            case PlayerNumber.TWO:
                ...
                _blittable = actual_captures.get_rect(midtop=(...))

        screen.blit(actual_captures, _blittable)

class Tile:
    """Renderable class for each tile inside board"""
    def __init__(self, location: Location):
        self._location = location
        self._x_coord = location.pixels[0]
        self._y_coord = location.pixels[1]
        self._occupier: LivePiece | None = None
        self._is_targetable = False

    @property
    def occupier(self) -> LivePiece | None:
        return self._occupier

    def mark_occupied(self, piece: LivePiece):
        self._occupier = piece

    def mark_empty(self):
        self._occupier = None

    def mark_targetable(self):
        self._is_targetable = True

    def unmark_targetable(self):
        self._is_targetable = False

    def render_to_board(self, board: pygame.Surface):
        actual_tile = pygame.Surface((TILE_PIXELS, TILE_PIXELS))
        pygame.Surface.fill(actual_tile, '#FFFFFF')
        
        if self._occupier is not None:
            kind = self._occupier.piece_kind
            owner = ...

        if self._is_targetable:
            pygame.draw.circle(actual_tile, 'red', (TILE_PIXELS//2, TILE_PIXELS//2), 4.0)

        board.blit(actual_tile, (self._x_coord, self._y_coord))

class RenderableBoard:
    """Renderable class for board; contains all tiles"""
    def __init__(self):
        self._location_to_tile = {
            Location(i, j) : Tile(Location(i, j))
            for i in range(BOARD_ROWS)
            for j in range(BOARD_COLS)
        }

    def get_tile(self, location) -> Tile:
        return self._location_to_tile[location]

    def render_to_screen(self, screen: pygame.Surface):
        actual_board = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT))
        pygame.Surface.fill(actual_board, '#000000')

        for k in self._location_to_tile:
            self._location_to_tile[k].render_to_board(actual_board)
        
        _blittable = actual_board.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(actual_board, _blittable)

class GameView:
    """Actual MVC view class"""
    def __init__(self):
        self._make_turn_observers: list[MakeTurnObserver] = []
        self._new_game_observers: list[NewGameObserver] = []

        self._captures_p1 = Captures(PlayerNumber.ONE)
        self._captures_p2 = Captures(PlayerNumber.TWO)
        self._renderable_board = RenderableBoard()

        pygame.font.init()
        self._font = pygame.font.SysFont('Arial', 25)

    def register_make_turn_observer(self, observer: MakeTurnObserver):
        self._make_turn_observers.append(observer)

    def register_new_game_observer(self, observer: NewGameObserver):
        self._new_game_observers.append(observer)

    def on_state_change(self, state: GameState):
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
                    '''Should be something mouse movement/click'''
                    ...

            self._screen.fill('#FFFFFF')

            self._renderable_board.render_to_screen(self._screen)
            self._captures_p1.render_to_screen(self._screen)
            self._captures_p2.render_to_screen(self._screen)

            ...
            '''Insert code re: Evaluating user input'''
            ...

            pygame.display.flip()
            self._clock.tick(60)

        pygame.quit()