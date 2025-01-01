import pygame
from collections import Counter

from project_types import (
    TILE_PIXELS, BOARD_ROWS, BOARD_COLS, GameStatus,
    LivePiece, Location, GameState, PieceKind,
    PlayerNumber,
    MakeTurnObserver, NewGameObserver,
    )
from model import Board

SCREEN_WIDTH = 768
SCREEN_HEIGHT = 720
BOARD_WIDTH = TILE_PIXELS*BOARD_ROWS
BOARD_HEIGHT = TILE_PIXELS*BOARD_COLS


def get_blittable(piece: LivePiece) -> pygame.Surface:
    """Return surface from piece, for use with blit"""
    if piece.piece_kind == PieceKind.EEVEE_SHINY:
        _path = "../../img/eevee-shiny.png"
    elif piece.piece_owner == PlayerNumber.TWO:
        _path = "../../img/" + piece.piece_kind.value + "-shiny.png"
    else:
        _path = "../../img/" + piece.piece_kind.value + ".png"

    _transformable = pygame.image.load(_path).convert_alpha()
    returnable = pygame.transform.scale(_transformable, (64, 64))

    return returnable


class Captures:
    """Renderable class for player captures (top and bottom of game screen)"""
    def __init__(self, number: PlayerNumber):
        self._captures: list[LivePiece] = []
        self._owner = number

        pygame.font.init()
        self._font = pygame.font.SysFont('Arial', 25)

    @property
    def captures(self) -> list[LivePiece]:
        return self._captures
    
    @property
    def owner(self) -> PlayerNumber:
        return self._owner
    
    def render_to_screen(self, screen: pygame.Surface):
        actual_captures = self._render_row()

        match self._owner:
            case PlayerNumber.ONE:
                _blittable = actual_captures.get_rect(midbottom=(SCREEN_WIDTH//2, SCREEN_HEIGHT))
            case PlayerNumber.TWO:
                _blittable = actual_captures.get_rect(midtop=(SCREEN_WIDTH//2, 0))

        screen.blit(actual_captures, _blittable)

    def _render_row(self) -> pygame.Surface:
        returnable = pygame.Surface((TILE_PIXELS*12, TILE_PIXELS))
        _counted_list = Counter(self._captures)

        order_in_screen = 0

        for piece in _counted_list:
            _blittable = get_blittable(piece)
            returnable.blit(_blittable, (TILE_PIXELS*order_in_screen, 0))

            _count = self._font.render(
                "x" + str(_counted_list[piece]),
                True, "#FFFFFF"
            )
            returnable.blit(_count, (TILE_PIXELS*order_in_screen, TILE_PIXELS))

            order_in_screen += 1

        return returnable

class Tile:
    """Renderable class for each tile inside board"""
    def __init__(self, location: Location):
        """
        Infer implicit info from occupier:
        type LivePiece => occupied, type None => unoccupied
        """
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
        """
        Render tile (and assigned attributes) to board surface;
        Help with the _image part, I think that's where the rendering issue is coming from?
        """
        actual_tile = pygame.Surface((TILE_PIXELS, TILE_PIXELS))
        pygame.Surface.fill(actual_tile, '#FFFFFF')
        pygame.draw.rect(actual_tile, "#000000", pygame.Rect(0, 0, TILE_PIXELS, TILE_PIXELS), width=1)
        
        if self._occupier is not None:
            _blittable = get_blittable(self._occupier)
            actual_tile.blit(_blittable, (0,0))

        if self._is_targetable:
            pygame.draw.circle(actual_tile, 'red', (TILE_PIXELS//2, TILE_PIXELS//2), 4.0)

        board.blit(actual_tile, (self._x_coord, self._y_coord))

class RenderableBoard:
    """Renderable class for board; contains all tiles"""
    def __init__(self, board: Board):
        self._location_to_tile: dict[Location: Tile] = {
            Location(i, j) : Tile(Location(i, j))
            for i in range(BOARD_ROWS)
            for j in range(BOARD_COLS)
        }

        self.set_board_state(board)

    def set_board_state(self, live_pieces: list[LivePiece]):
        """Set board according to current live pieces (preferably take from game state instance)"""
        for piece in live_pieces:
            self._location_to_tile[piece.location].mark_occupied(piece)

    def render_to_screen(self, screen: pygame.Surface):
        actual_board = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT))
        pygame.Surface.fill(actual_board, '#000000')

        for k in self._location_to_tile:
            self._location_to_tile[k].render_to_board(actual_board)
        
        _blittable = actual_board.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(actual_board, _blittable)

class GameView:
    """Actual MVC view class"""
    def __init__(self, state: GameState):
        """Initialize observers, Pygame font"""
        self.on_state_change(state)

        self._make_turn_observers: list[MakeTurnObserver] = []
        self._new_game_observers: list[NewGameObserver] = []

        pygame.font.init()
        self._font = pygame.font.SysFont('Arial', 25)

        self._init_view_state()

    def _init_view_state(self):
        """
        Initialize view-specific properties
        --- Might need to add viewing player?
        """
        self._renderable_board = RenderableBoard(self._live_pieces)

        self._captures_p1 = Captures(PlayerNumber.ONE)
        self._captures_p2 = Captures(PlayerNumber.TWO)

    def on_state_change(self, state: GameState):
        self._active_player = state.active_player
        self._captured_pieces = state.captured_pieces
        self._live_pieces = state.live_pieces
        self._action_count = state.action_count
        self._game_status = state.game_status

    def register_make_turn_observer(self, observer: MakeTurnObserver):
        self._make_turn_observers.append(observer)

    def register_new_game_observer(self, observer: NewGameObserver):
        self._new_game_observers.append(observer)

    def _evaluate_winner(self):
        """
        Evaluate game-end on-screen printout
        --- Might need viewing player?
        """
        if self._game_status == GameStatus.PLAYER_WIN:
            self._render_text_result("YOU WIN")
        elif self._game_status == GameStatus.PLAYER_LOSE:
            self._render_text_result("YOU LOSE")
        elif self._game_status == GameStatus.GAME_DRAW:
            self._render_text_result("GAME RESULTED IN STALEMATE")

    def _make_turn(self):
        for observer in self._make_turn_observers:
            observer.on_make_turn()

    def _new_game(self):
        for observer in self._new_game_observers:
            observer.on_new_game()

    def _render_text_result(self, text: str):
        result_text = self._font.render(text, True, '#000000')
        _blittable = result_text.get_rect(center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))

        self._screen.blit(result_text, _blittable)

    def _on_mouse_press(self, event: pygame.Event):
        curr_player = self._active_player

        if self._game_status == GameStatus.ONGOING:
            ...

    def run(self):
        """Main game running logic; Equivalent to main()"""
        pygame.init()

        self._screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._clock = pygame.time.Clock()

        _game_is_running = True

        while _game_is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    _game_is_running = False

                # elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                #     self._on_mouse_press(event)

            self._screen.fill('#FFFFFF')

            self._renderable_board.render_to_screen(self._screen)
            self._captures_p1.render_to_screen(self._screen)
            self._captures_p2.render_to_screen(self._screen)

            if self._game_status != GameStatus.ONGOING:
                self._evaluate_winner()

            pygame.display.flip()
            self._clock.tick(60)

        pygame.quit()