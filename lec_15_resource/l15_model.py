from typing import Callable
from l15_project_types import *


class ChickMovement:
    def get_deltas(self) -> list[tuple[int, int]]:
        return [self.FORWARD]
 
class ElephantMovement:
    def get_deltas(self) -> list[tuple[int, int]]:
        return self.DIAGONALS
 
class GiraffeMovement:
    def get_deltas(self) -> list[tuple[int, int]]:
        return self.ORTHOGONALS
 
class LionMovement:
    def get_deltas(self) -> list[tuple[int, int]]:
        return [*self.ORTHOGONALS,
                *self.DIAGONALS]
 
class CatMovement:
    def get_deltas(self) -> list[tuple[int, int]]:
        return [*self.DIAGONALS, *self.FORWARD]
 
class DogMovement:
    def get_deltas(self) -> list[tuple[int, int]]:
        return [*self.ORTHOGONALS,
                *self.FORWARD_DIAGONALS]


class Board[T]:
    """Represents a 2D board."""
    def __init__(self, width: int, height: int):
        ...
 
    @property
    def width(self):
        ...
 
    @property
    def height(self):
        ...
 
    def get(self, x: int, y: int) -> T | None:
        ...
 
    def put(self, x: int, y: int, value: T):
        ...
 
    def is_any(self, pred: Callable[[T | None], bool]) -> bool:
        ...
 
    def is_within_bounds(self, x: int, y: int) -> bool:
        ...


class RowColBoard(Protocol):
    """Represents a 2D board."""
    @property
    def width(self):
        ...
 
    @property
    def height(self):
        ...
 
    def get(self, location: Location) -> Piece | None:
        ...
 
    def put(self, location: Location, value: Piece):
        ...
 
    def move(self, fromeu: Location, toeu: Location):
        # Not present in `Board`
        ...
 
    def is_any(self, pred: Callable[[Piece | None], bool]) -> bool:
        ...
 
    def is_within_bounds(self, location: Location) -> bool:
        ...


class RowColToXyBoardAdapter:
    def __init__(self, board: Board[Piece]):
        self._board = board
 
    @property
    def width(self):
        return self._board.width
 
    @property
    def height(self):
        return self._board.height
    
    def _convert(self, location: Location) -> tuple[int, int]:
        return (location.col, location.row)
 
    def get(self, location: Location) -> Piece | None:
        return self._board.get(*self._convert(location))
 
    def put(self, location: Location, piece: Piece):
        return self._board.put(*self._convert(location), piece)
 
    def move(self, fromeu: Location, toeu: Location):
        if (src := self.get(fromeu)) is not None:
            self.put(toeu, src)
 
    def is_any(self, pred: Callable[[Piece | None], bool]) -> bool:
        return self._board.is_any(pred)
 
    def is_within_bounds(self, location: Location) -> bool:
        return self._board.is_within_bounds(*self._convert(location))


class PieceFactory:
    """Instantiates a Piece based on a PieceKind."""
 
    @classmethod
    def make(cls, piece_kind: PieceKind,
             location: Location) -> Piece:
        match piece_kind:
            case PieceKind.CHICK:
                movement = ChickMovement()
 
            case PieceKind.HEN | PieceKind.EMPOWERED_CAT | PieceKind.DOG:
                movement = DogMovement()
 
            case PieceKind.ELEPHANT:
                movement = ElephantMovement()
 
            case PieceKind.GIRAFFE:
                movement = GiraffeMovement()
 
            case PieceKind.LION:
                movement = LionMovement()
 
            case PieceKind.CAT:
                movement = CatMovement()
 
        return Piece(piece_kind, location, movement)


class PiecePositions(Protocol):
    def get_positions(self) -> list[tuple[Location, Player, PieceKind]]:
        ...
 
 
class DoubutsuPiecePositions:
    def get_positions(self) -> list[tuple[Location, Player, PieceKind]]:
        return [
            (Location(2, 1), Player.PLAYER_1, PieceKind.CHICK),
            (Location(3, 0), Player.PLAYER_1, PieceKind.ELEPHANT),
            (Location(3, 1), Player.PLAYER_1, PieceKind.LION),
            (Location(3, 2), Player.PLAYER_1, PieceKind.GIRAFFE),
            (Location(0, 0), Player.PLAYER_2, PieceKind.GIRAFFE),
            (Location(0, 1), Player.PLAYER_2, PieceKind.LION),
            (Location(0, 2), Player.PLAYER_2, PieceKind.ELEPHANT),
            (Location(1, 1), Player.PLAYER_2, PieceKind.CHICK),
        ]
 
 
class GoroGoroPiecePositions:
    def get_positions(self) -> list[tuple[Location, Player, PieceKind]]:
        return [
            (Location(3, 0), Player.PLAYER_1, PieceKind.CHICK),
            (Location(3, 1), Player.PLAYER_1, PieceKind.CHICK),
            (Location(3, 2), Player.PLAYER_1, PieceKind.CHICK),
            (Location(5, 0), Player.PLAYER_1, PieceKind.CAT),
            (Location(5, 1), Player.PLAYER_1, PieceKind.DOG),
            (Location(5, 2), Player.PLAYER_1, PieceKind.LION),
            (Location(5, 3), Player.PLAYER_1, PieceKind.DOG),
            (Location(5, 4), Player.PLAYER_1, PieceKind.CAT),
            (Location(0, 0), Player.PLAYER_2, PieceKind.CAT),
            (Location(0, 1), Player.PLAYER_2, PieceKind.DOG),
            (Location(0, 2), Player.PLAYER_2, PieceKind.LION),
            (Location(0, 3), Player.PLAYER_2, PieceKind.DOG),
            (Location(0, 4), Player.PLAYER_2, PieceKind.CAT),
            (Location(2, 0), Player.PLAYER_2, PieceKind.CHICK),
            (Location(2, 1), Player.PLAYER_2, PieceKind.CHICK),
            (Location(2, 2), Player.PLAYER_2, PieceKind.CHICK),
        ]


class BoardSetter:
    """Sets pieces up on the board."""
    def __init__(self, positions: PiecePositions):  # DoubutsuPiecePositions <: PiecePositions
        self._positions = positions                 # GoroGoroPiecePositions <: PiecePositions
 
    def setup_board(self, board: RowColBoard):
        for piece_kind, player, location in self._positions.get_positions():
            piece = PieceFactory.make(piece_kind, location)
            board.put(location, piece)

    def make_piece_positions(self) -> PiecePositions:
        raise NotImplementedError()

class DoubutsuBoardSetter(BoardSetter):
    """Sets pieces up on the board consistent with Doubutsu rules."""
 
    def make_piece_positions(self) -> PiecePositions:
        return DoubutsuPiecePositions()
 
 
class GoroGoroBoardSetter(BoardSetter):
    """Sets pieces up on the board consistent with Goro Goro rules."""
 
    def make_piece_positions(self) -> PiecePositions:
        return GoroGoroPiecePositions()
    
