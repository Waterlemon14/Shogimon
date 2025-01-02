import pygame
from collections import Counter

from project_types import (
    TILE_PIXELS, BOARD_ROWS, BOARD_COLS, GameStatus,
    LivePiece, Location, GameState, PieceKind, ActionType, PlayerAction, PlayerNumber,
    MakeTurnObserver, NewGameObserver,
    )

SCREEN_WIDTH = 768
SCREEN_HEIGHT = 720
BOARD_WIDTH = TILE_PIXELS*BOARD_ROWS
BOARD_HEIGHT = TILE_PIXELS*BOARD_COLS


def get_blittable(piece: LivePiece) -> pygame.Surface:
    """Return surface from piece, for use with blit"""
    if piece.kind == PieceKind.EEVEE_SHINY:
        _path = "./../img/eevee-shiny.png"
    elif piece.owner == PlayerNumber.TWO:
        _path = "./../img/" + piece.kind.value + "-shiny.png"
    else:
        _path = "./../img/" + piece.kind.value + ".png"

    _transformable = pygame.image.load(_path).convert_alpha()
    returnable = pygame.transform.scale(_transformable, (64, 64))

    return returnable


class Captures:
    """Renderable class for player captures (top and bottom of game screen)"""
    def __init__(self, number: PlayerNumber):
        self._captures: list[LivePiece] = []
        self._owner = number

        self._actual_row = pygame.Surface((TILE_PIXELS*12, TILE_PIXELS))

        pygame.font.init()
        self._font = pygame.font.SysFont('Arial', 25)

    @property
    def captures(self) -> list[LivePiece]:
        return self._captures
    
    @property
    def owner(self) -> PlayerNumber:
        return self._owner
    
    @property
    def rect(self) -> pygame.Rect:
        '''UNTESTED'''
        match self._owner:
            case PlayerNumber.ONE:
                return self._actual_row.get_rect(centerx=SCREEN_WIDTH//2, bottom=SCREEN_HEIGHT)
            case PlayerNumber.TWO:
                return self._actual_row.get_rect(centerx=SCREEN_WIDTH//2, top=0)
    
    def render_to_screen(self, screen: pygame.Surface):
        actual_captures = self._render_row()
        screen.blit(actual_captures, self.rect)

    def _render_row(self) -> pygame.Surface:
        pygame.Surface.fill(self._actual_row, 'black')
        _counted_list = Counter(self._captures)

        order_in_screen = 0

        for piece in _counted_list:
            _blittable = get_blittable(piece)
            self._actual_row.blit(_blittable, (TILE_PIXELS*order_in_screen, 0))

            _count = self._font.render(
                "x" + str(_counted_list[piece]),
                True, "white"
            )
            self._actual_row.blit(_count, (TILE_PIXELS*order_in_screen, 0))

            order_in_screen += 1

        return self._actual_row

class Tile:
    """Renderable class for each tile inside board"""
    def __init__(self, location: Location):
        """Infer implicit info from occupier: type LivePiece => occupied, type None => unoccupied"""
        self._location = location
        self._x_coord = location.pixels[0]
        self._y_coord = location.pixels[1]
        self._occupier: LivePiece | None = None
        self._is_targetable = False

        self._actual_tile = pygame.Surface((TILE_PIXELS, TILE_PIXELS))

    @property
    def rect(self) -> pygame.Rect:
        '''UNTESTED'''
        return self._actual_tile.get_rect(center=(TILE_PIXELS//2, TILE_PIXELS//2))

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
        pygame.Surface.fill(self._actual_tile, 'white')
        pygame.draw.rect(self._actual_tile, "black", pygame.Rect(0, 0, TILE_PIXELS, TILE_PIXELS), width=1)
        
        if self._occupier is not None:
            _blittable = get_blittable(self._occupier)
            self._actual_tile.blit(_blittable, (0,0))

        if self._is_targetable:
            pygame.draw.circle(self._actual_tile, 'red', (TILE_PIXELS//2, TILE_PIXELS//2), 4.0)

        board.blit(self._actual_tile, (self._x_coord, self._y_coord))

class RenderableBoard:
    """Renderable class for board; contains all tiles"""
    def __init__(self, live_pieces: list[LivePiece]):
        self._location_to_tile: dict[Location, Tile] = {
            Location(i, j) : Tile(Location(i, j))
            for i in range(BOARD_ROWS)
            for j in range(BOARD_COLS)
        }

        self._actual_board = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT))

        self.set_board_state(live_pieces)

    @property
    def rect(self) -> pygame.Rect:
        '''UNTESTED'''
        return self._actual_board.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))

    def set_board_state(self, live_pieces: list[LivePiece]):
        """Set board according to current live pieces (preferably take from game state instance)"""
        for piece in live_pieces:
            if piece.location:
                self._location_to_tile[piece.location].mark_occupied(piece)

    def mark_nearby_targetable(self, location: Location):
        ...

    def click_pixels(self, coords: tuple[int, int], player: PlayerNumber):
        ...

    def render_to_screen(self, screen: pygame.Surface):
        pygame.Surface.fill(self._actual_board, 'black')

        for k in self._location_to_tile:
            self._location_to_tile[k].render_to_board(self._actual_board)
        
        screen.blit(self._actual_board, self.rect)

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

    def _make_turn(self, action: PlayerAction):
        for observer in self._make_turn_observers:
            observer.on_make_turn(action)

    def _new_game(self):
        for observer in self._new_game_observers:
            observer.on_new_game()

    def _render_text_result(self, text: str):
        result_text = self._font.render(text, True, 'black')
        _blittable = result_text.get_rect(center = (SCREEN_WIDTH//2, SCREEN_HEIGHT//2))

        self._screen.blit(result_text, _blittable)

    def _mouse_press_on_board(self, abs_pos: tuple[int, int]):
        """When mouse is clicked inside rect Board"""
        rel_x = abs_pos[0] - 129
        rel_y = abs_pos[1] - 105

        if self._game_status == GameStatus.ONGOING:
            self._renderable_board.click_pixels((rel_x, rel_y), self._active_player)

    def _mouse_press_on_captures(self, abs_pos: tuple[int, int], player: PlayerNumber):
        """When mouse is clicked inside rect Captures"""
        rel_x = abs_pos[0]
        rel_y = abs_pos[1] - 656 if player == PlayerNumber.ONE else abs_pos[1]

        if self._game_status == GameStatus.ONGOING:
            '''TO DO: add something missing inside class Captures'''
            match player:
                case PlayerNumber.ONE:
                    ...
                    
                case PlayerNumber.TWO:
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

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self._renderable_board.rect.collidepoint(event.pos):
                        self._mouse_press_on_board(event.pos)
                    
                    elif (self._active_player == PlayerNumber.ONE and self._captures_p1.rect.collidepoint(event.pos)) \
                    or (self._active_player == PlayerNumber.TWO and self._captures_p2.rect.collidepoint(event.pos)):
                        print(self._active_player)
                        self._mouse_press_on_captures(event.pos, self._active_player)

            self._screen.fill('black')

            self._renderable_board.render_to_screen(self._screen)
            self._captures_p1.render_to_screen(self._screen)
            self._captures_p2.render_to_screen(self._screen)

            if self._game_status != GameStatus.ONGOING:
                self._evaluate_winner()

            pygame.display.flip()
            self._clock.tick(60)

        pygame.quit()