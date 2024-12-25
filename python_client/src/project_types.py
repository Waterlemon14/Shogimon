from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class BoardState():
    ...

class Movement(Protocol):
    def get_movement_range(self) -> list:
        ...

class Piece(Protocol):
    def is_captured(self) -> bool:
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