from dataclasses import dataclass
from typing import Protocol
from enum import StrEnum, auto

class GameStatus(StrEnum):
    ONGOING = 'Ongoing'
    PLAYER_WIN = 'Round win'
    PLAYER_LOSE = 'Round lose'

class PieceKind(StrEnum):
    EEVEE = auto()
    PIKACHU = auto()
    LATIAS = auto()
    TURTWIG = auto()
    SYLVEON = auto()
    UMBREON = auto()

class PlayerNumber(StrEnum):
    ONE = auto()
    TWO = auto()

@dataclass(frozen=True)
class GameState():
    ...

class Movement(Protocol):
    FORWARD = [(-1, 0)]
    FORWARD_DIAGONALS = [(-1, -1), (-1, +1)]
 
    ORTHOGONALS = [(dr, dc) for dr in {-1, 0 +1}
                   for dc in {-1, 0 +1}
                   if 0 in {dr, dc}]
 
    DIAGONALS = [(dr, dc) for dr in {-1, +1}
                 for dc in {-1, +1}]
    
    def get_movement_range(self) -> list:
        ...

class Tile:
    row: int
    col: int

class MakeTurnObserver(Protocol):
    """
    For view; Communicator between turn of each player
    """
    def on_make_turn(self, turn: Movement):
        ...

class NewGameObserver(Protocol):
    """
    For view; Communicator for when new game start
    """
    def on_new_game(self):
        ...

class GameStateChangeObserver(Protocol):
    """
    For controller;
    Communicator of change in game state (i.e., ongoing, player 1 win, player 1 lose)
    """
    def on_state_change(self, state: GameState):
        ...