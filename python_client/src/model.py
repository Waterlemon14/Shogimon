from typing import Self

from project_types import GameState, Movement, PieceKind, Tile, PlayerNumber, MovePossibilities
# from view import Tile

class EeveeMovement(Movement):
    def get_movement_range(self) -> list[tuple[int, int]]:
        return MovePossibilities.FORWARD.value
    
class PikachuMovement(Movement):
    def get_movement_range(self) -> list[tuple[int, int]]:
        return MovePossibilities.DIAGONALS.value

class TurtwigMovement(Movement):
    def get_movement_range(self) -> list[tuple[int, int]]:
        return MovePossibilities.ORTHOGONALS.value

class LatiosMovement(Movement):
    def get_movement_range(self) -> list[tuple[int, int]]:
        return MovePossibilities.SINGLE_ORTHOGONALS.value
    
class LatiasMovement(Movement):
    def get_movement_range(self) -> list[tuple[int, int]]:
        return MovePossibilities.SINGLE_ORTHOGONALS.value

class CurrentPlayer:
    """
    Subfamily of protocol Player;
    Get interactions from view
    """
    ...

class Opponent:
    """
    Subfamily of protocol Player;
    Get interactions from server (saka na natin problemahin)
    """
    ...

class Piece:
    def __init__(self, kind: PieceKind, tile: Tile, movement: Movement):
        self._kind = kind
        self._tile = tile
        self._is_captured = False
        self._movement = movement

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

class ProtectedPiece:
    def __init__(self, kind: PieceKind, tile: Tile, movement: Movement):
        self._kind = kind
        self._tile = tile
        self._movement = movement
    
    @property
    def kind(self) -> PieceKind:
        return self._kind
    
    @property
    def row(self) -> int:
        return self._tile.row
    
    @property
    def col(self) -> int:
        return self._tile.col

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
class Board:

    def __init__(self, height: int, width: int):
        self._height: int = height
        self._width: int = width
        ...

    def put(self, row: int, col: int, piece: Piece):
        ...

    def take(self, row: int, col: int) -> Piece | None:
        ...

    def is_valid_tile(self, row: int, col: int) -> bool:
        # To fix
        return row < self._height and col < self._width
    

    # TO DO: Board Setter
    # will set board, clear board, etc.


class PieceFactory:
    def make(self, piece_kind: PieceKind,
             tile: Tile) -> Piece | ProtectedPiece:
        match piece_kind:
            case PieceKind.EEVEE:
                movement = EeveeMovement()
                return Piece(piece_kind, tile, movement)
 
            case PieceKind.PIKACHU:
                movement = PikachuMovement()
                return Piece(piece_kind, tile, movement)
 
            case PieceKind.TURTWIG:
                movement = TurtwigMovement()
                return Piece(piece_kind, tile, movement)
 
            case PieceKind.LATIOS:
                movement = LatiosMovement()
                return ProtectedPiece(piece_kind, tile, movement)
 
            case PieceKind.LATIAS:
                movement = LatiasMovement()
                return ProtectedPiece(piece_kind, tile, movement)

class Player:
    def __init__(self, number: PlayerNumber, deployed_pieces: list[Piece | ProtectedPiece], captured_pieces: list[Piece | ProtectedPiece]):
        self._number: PlayerNumber = number
        self._deployed_pieces: list[Piece | ProtectedPiece] = deployed_pieces
        self._captured_pieces: list[Piece | ProtectedPiece] = captured_pieces
        pass

    def get_deployed_pieces(self) -> list[tuple[PieceKind, Tile]]:
        return [(piece.kind, Tile(piece.row, piece.col)) for piece in self._deployed_pieces]

    def get_captured_pieces(self) -> list[PieceKind]:
        return [piece.kind for piece in self._captured_pieces]

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

        board = Board(8, 8)
        player1 = Player(PlayerNumber.ONE, [], [])
        player2 = Player(PlayerNumber.TWO, [], [])

        state = GameState(
            player_number = PlayerNumber.ONE,
            active_player = PlayerNumber.ONE,
            is_still_playable=True,
            captured_pieces= {PlayerNumber.ONE: [], PlayerNumber.TWO: []},
            board_pieces= board.get_pieces(),
            move_count=3
        )

        return cls(state)


    def __init__(self, state: GameState, board: Board, player1: Player, player2: Player):
        self.state = state
        
        ...

    def make_turn(self, turn: Movement):
        ...

    def new_game(self):
        ...