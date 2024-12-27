from typing import Self

from project_types import GameState, Movement, PieceKind
from view import Tile

class Piece:
    def __init__(self, kind: PieceKind, tile: Tile):
        self._kind = kind
        self._tile = tile
        self._is_captured = False

    def is_captured(self) -> bool:
        return self._is_captured

    def get_movement_range(self) -> list[Movement]:
        match self._kind:
            case PieceKind.EEVEE:
                ...

            case PieceKind.PIKACHU:
                ...

            case PieceKind.TURTWIG:
                ...

            case PieceKind.SYLVEON:
                ...

            case default:
                ...

        return []

    def possible_moves(self) -> list[Movement]:
        """
        Returns list of possible moves given board state and list from get_movement_range()
        """
        ...

class ProtectedPiece:
    def __init__(self, piece: PieceKind, tile: Tile):
        self._piece = piece
        self._tile = tile
    
    def is_immobile(self) -> bool:
        return self.possible_moves == []

    def get_movement_range(self) -> list[Movement]:
        ...

    def possible_moves(self) -> list[Movement]:
        ...

class GameModel:
    @classmethod
    def default(cls) -> Self:
        ...

    def __init__(self, state: GameState):
        self.state = state
        ...

    def make_turn(self, turn: Movement):
        ...

    def new_game(self):
        ...