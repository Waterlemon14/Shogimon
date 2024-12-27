from dataclasses import dataclass
from typing import Protocol
from enum import StrEnum

from view import Tile

class GameStatus(StrEnum):
    ONGOING = 'Ongoing'
    PLAYER_WIN = 'Round win'
    PLAYER_LOSE = 'Round lose'

class PieceKind(StrEnum):
    EEVEE = 'Eevee'
    PIKACHU = 'Pikachu'
    LATIAS = 'Latias'
    TURTWIG = 'Turtwig'
    SYLVEON = 'Sylveon'
    UMBREON = 'Umbreon'

@dataclass(frozen=True)
class GameState():
    ...

class Movement(Protocol):
    def get_movement_range(self) -> list:
        ...

class Piece:
    def __init__(self, piece: PieceKind, tile: Tile):
        self._piece = piece
        self._tile = tile
        self._is_captured = False

    def is_captured(self) -> bool:
        ...
    
    def is_protected(self) -> bool:
        ...

    def possible_moves(self) -> list:
        """
        Returns list of possible moves given board state and list from get_movement_range()
        """
        ...

class Player(Protocol):
    def make_turn(self):
        """
        If turn of player, choose between _move_piece and _drop_piece
        """
        ...

    def _move_piece(self) -> bool:
        """
        Return TRUE if a piece is captured, else return FALSE
        """
        ...

    def _drop_piece(self) -> bool:
        """
        Return (a) if (r,c) is occupied; and (b) if (r,c) is in movement range of protected piece
        """
        ...

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