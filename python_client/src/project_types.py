from dataclasses import dataclass
from typing import Protocol
from enum import Enum, StrEnum, auto


BOARD_ROWS = 8
BOARD_COLS = 8
TILE_PIXELS = 64


class GameStatus(StrEnum):
    ONGOING = 'Ongoing'
    PLAYER_WIN = 'Game win'
    PLAYER_LOSE = 'Game lose'
    GAME_DRAW = 'Game draw'

class PieceKind(StrEnum):
    EEVEE = auto()
    EEVEE_SHINY = auto()
    PIKACHU = auto()
    LATIAS = auto()
    LATIOS = auto()
    TURTWIG = auto()

class ActionType(StrEnum):
    MOVE = auto()
    DROP = auto()

class PlayerNumber(StrEnum):
    """Default (i.e. first one to launch): player one"""
    ONE = auto()
    TWO = auto()


@dataclass(frozen=True)
class Location:
    row: int
    col: int

    @property
    def pixels(self) -> tuple[int, int]:
        return (self.col * TILE_PIXELS, self.row * TILE_PIXELS)

@dataclass(frozen=True)
class LivePiece:
    """
    Infer implicit type from location:
    type Location => piece is on board, type None => piece is captured
    """
    piece_kind: PieceKind
    piece_id: int
    piece_owner: PlayerNumber
    location: Location | None

@dataclass(frozen=True)
class PlayerAction:
    action_type: ActionType
    player_number: PlayerNumber
    piece_id: int
    target_location: Location

@dataclass(frozen=True)
class GameState:
    player_number: PlayerNumber
    active_player: PlayerNumber
    captured_pieces: list[LivePiece]
    live_pieces: list[LivePiece]
    action_count: int
    game_status: GameStatus


class MovePossibilities(Enum):
    FORWARD = [(-1, 0)]
    FORWARD_OPPOSITE = [(1, 0)]
    DIAGONALS = [(-1, -1), (-1, +1), (+1, +1), (+1, -1)]
    ORTHOGONALS = [(0, -1), (0, +1), (-1, 0), (+1, 0),]


class Movement(Protocol):    
    def get_movement_range(self, row: int, col: int, valid_locations: dict[tuple[int, int], bool]) -> list[tuple[int, int]]:
        ...

class PiecePositions(Protocol):
    def get_positions(self) -> list[tuple[PlayerNumber, PieceKind, Location]]:
        ...

class MakeTurnObserver(Protocol):
    """For view; Communicator between turn of each player"""
    def on_make_turn(self, action: PlayerAction):
        ...

class NewGameObserver(Protocol):
    """For view; Communicator for when new game start"""
    def on_new_game(self):
        ...

class GameStateChangeObserver(Protocol):
    """For controller; Communicator of change in game state (ongoing, player 1 win, player 1 lose)"""
    def on_state_change(self, state: GameState):
        ...