from dataclasses import dataclass
from typing import Protocol
from enum import Enum, StrEnum, auto

TILE_SIZE = 64

class GameStatus(StrEnum):
    ONGOING = 'Ongoing'
    PLAYER_WIN = 'Round win'
    PLAYER_LOSE = 'Round lose'

class PieceKind(StrEnum):
    EEVEE = auto()
    PIKACHU = auto()
    LATIAS = auto()
    LATIOS = auto()
    TURTWIG = auto()

    def image_path(self, shiny: bool) -> str:
        if shiny:
            return "../../img/" + self.value + "-shiny.png"
        
        return "../../img/" + self.value + ".png"
    
class ActionType(StrEnum):
    MOVE = auto()
    DROP = auto()

class PlayerNumber(StrEnum):
    ONE = auto()
    TWO = auto()

@dataclass(frozen=True)
class Location:
    row: int
    col: int

    def pixels(self) -> tuple[int, int]:
        return (self.row * TILE_SIZE, self.col * TILE_SIZE)

@dataclass(frozen=True)
class LivePiece:
    piece_kind: PieceKind
    piece_id: int
    location: Location

@dataclass(frozen=True)
class CapturedPiece:
    """-> for this, peep my PM sa messenger"""
    piece_kind: PieceKind
    piece_id: int

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
    is_still_playable: bool
    captured_pieces: dict[PlayerNumber, list[CapturedPiece]]
    live_pieces: dict[PlayerNumber, list[LivePiece]]
    move_count: int
    """-> semantics; rename to action_count? to avoid ambiguity"""

class MovePossibilities(Enum):
    FORWARD = [(-1, 0)]
    ORTHOGONALS = [
        (dr, dc)
        for dr in {-1, 0 +1}
        for dc in {-1, 0 +1}
        if 0 in {dr, dc}
    ]
    DIAGONALS = [
        (dr, dc)
        for dr in {-1, +1}
        for dc in {-1, +1}
    ]
    SINGLE_DIAGONALS = [(-1, -1), (-1, +1), (+1, +1), (+1, -1)]
    SINGLE_ORTHOGONALS = [(0, -1), (0, +1), (-1, 0), (+1, 0),]

class Movement(Protocol):    
    def get_movement_range(self) -> list[tuple[int, int]]:
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