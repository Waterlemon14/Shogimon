from dataclasses import dataclass
from typing import Protocol
from enum import Enum, StrEnum, auto

@dataclass(frozen=True)
class Location:
    row: int
    col: int
 

class Player(StrEnum):
    PLAYER_1 = auto()
    PLAYER_2 = auto()


class PieceKind(StrEnum):
    CHICK = auto()
    HEN = auto()
    ELEPHANT = auto()
    GIRAFFE = auto()
    LION = auto()
    CAT = auto()
    EMPOWERED_CAT = auto()
    DOG = auto()
 

class Movement(Protocol):
    FORWARD = [(-1, 0)]
    FORWARD_DIAGONALS = [(-1, -1), (-1, +1)]
 
    ORTHOGONALS = [(dr, dc) for dr in {-1, 0 +1}
                   for dc in {-1, 0 +1}
                   if 0 in {dr, dc}]
 
    DIAGONALS = [(dr, dc) for dr in {-1, +1}
                 for dc in {-1, +1}]
 
    def get_deltas(self) -> list[tuple[int, int]]:
        ...

 
class Piece:
    def __init__(self, piece_kind: PieceKind,
                 location: Location,
                 movement: Movement):
        self._piece_kind = piece_kind
        self._location = location
        self._movement = movement
 
    @property
    def piece_kind(self):
        return self._piece_kind
 
    @property
    def row(self):
        return self._location.row
 
    @property
    def col(self):
        return self._location.col
 
    def can_move(self, to: Location) -> bool:
        return any(
          True for dr, dc in self._movement.get_deltas()
          if self.row + dr == to.row and
          self.col + dc == to.col
        )