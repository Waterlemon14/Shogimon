from typing import Self

from project_types import GameState, Movement, PieceKind, Tile, PlayerNumber
# from view import Tile

# Movements

class EeveeMovement(Movement):
    def get_movement_range(self) -> list[tuple[int, int]]:
        return [self.FORWARD]
    
class Pickachu(Movement):
    def get_movement_range(self) -> list[tuple[int, int]]:
        pass

class Turtwig(Movement):
    def get_movement_range(self) -> list[tuple[int, int]]:
        pass

class Sylveon(Movement):
    def get_movement_range(self) -> list[tuple[int, int]]:
        pass

class Piece:
    def __init__(self, kind: PieceKind, tile: Tile, movement: Movement, protected: bool):
        self._kind = kind
        self._tile = tile
        self._is_captured = False
        self._movement = movement
        self._protected = protected

    @property
    def kind(self) -> PieceKind:
        return self._kind
    
    @property
    def row(self) -> int:
        return self._tile.row
    
    @property
    def col(self) -> int:
        return self._tile.col
    
    @property
    def protected(self) -> bool:
        return self._protected

    @property
    def is_captured(self) -> bool:
        return self._is_captured

    def can_move(self, target: Tile) -> bool:
        """
        To verifiy, from Lecture 15
        """
        return any(
          True for dr, dc in self._movement.get_movement_range()
          if self.row + dr == target.row and
          self.col + dc == target.col
        )
    
    # TO DO: Board Class
    # TO DO: Board Setter
    # TO DO: Piece Factory 
    # TO DO: Bunch of methods for present classes

    """See project_types.py, movement classes above

    def get_movement_range(self) -> list[Movement]:
        
        i still need help wrapping my head around the EeveeMovement part jasjdasjd
        tama ba implementation ko here pasabi na lang if yes or no
        
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
        
        Returns list of possible moves given board state and list from get_movement_range()
        
        ..."""

"""class ProtectedPiece:
    def __init__(self, piece: PieceKind, tile: Tile):
        self._piece = piece
        self._tile = tile
    
    def is_immobile(self) -> bool:
        return self.possible_moves == []

    def get_movement_range(self) -> list[Movement]:
        ...

    def possible_moves(self) -> list[Movement]:
        ..."""

class Player:
    def __init__(self, number: PlayerNumber):
        self._number = number
        pass

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