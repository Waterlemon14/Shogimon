from typing import Self

from project_types import GameState, Movement, PieceKind, Location, PlayerNumber, MovePossibilities, PiecePositions, LivePiece, PlayerAction, ActionType, CapturedPiece

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
    def __init__(self, id: int, kind: PieceKind, location: Location, movement: Movement):
        self._id = id
        self._kind = kind
        self._location = location
        self._is_captured = False
        self._movement = movement

    @property
    def id(self) -> int:
        return self._id

    @property
    def kind(self) -> PieceKind:
        return self._kind
    
    @property
    def row(self) -> int:
        return self._location.row
    
    @property
    def col(self) -> int:
        return self._location.col

    @property
    def is_captured(self) -> bool:
        return self._is_captured

    def can_move(self, target: Location) -> bool:
        """
        To verifiy, from Lecture 15
        """
        return any(
            True for dr, dc in self._movement.get_movement_range()
            if self.row + dr == target.row and
            self.col + dc == target.col
        )

class ProtectedPiece:
    def __init__(self, id: int, kind: PieceKind, location: Location, movement: Movement):
        self._id = id
        self._kind = kind
        self._location = location
        self._movement = movement
    
    @property
    def id(self) -> int:
        return self._id

    @property
    def kind(self) -> PieceKind:
        return self._kind
    
    @property
    def row(self) -> int:
        return self._location.row
    
    @property
    def col(self) -> int:
        return self._location.col

    def can_move(self, target: Location) -> bool:
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
        self._grid: list[list[Piece | ProtectedPiece]]
        ...

    def put(self, row: int, col: int, piece: Piece | ProtectedPiece):
        self._grid[row][col] = piece

    def take(self, row: int, col: int) -> Piece | None:
        ...

    def is_valid_location(self, row: int, col: int) -> bool:
        # To fix
        return row < self._height and col < self._width
    
class Player:
    def __init__(self, number: PlayerNumber, deployed_pieces: list[Piece | ProtectedPiece], captured_pieces: list[Piece | ProtectedPiece]):
        self._number: PlayerNumber = number
        self._deployed_pieces: list[Piece | ProtectedPiece] = deployed_pieces
        self._captured_pieces: list[Piece | ProtectedPiece] = captured_pieces
        pass

    def get_deployed_pieces(self) -> list[LivePiece]:
        return [LivePiece(piece.kind, piece.id, Location(piece.row, piece.col)) for piece in self._deployed_pieces]

    def get_captured_pieces(self) -> list[CapturedPiece]:
        return [CapturedPiece(piece.kind, piece.id) for piece in self._captured_pieces]

    def make_turn(self, board: Board, action: PlayerAction):
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
class PieceFactory:
    _piece_count = 0

    @classmethod
    def make(cls, piece_kind: PieceKind,
             location: Location) -> Piece | ProtectedPiece:
        piece_id = cls._piece_count
        cls._piece_count += 1

        match piece_kind:
            case PieceKind.EEVEE:
                movement = EeveeMovement()
                return Piece(piece_id, piece_kind, location, movement)
 
            case PieceKind.PIKACHU:
                movement = PikachuMovement()
                return Piece(piece_id, piece_kind, location, movement)
 
            case PieceKind.TURTWIG:
                movement = TurtwigMovement()
                return Piece(piece_id, piece_kind, location, movement)
 
            case PieceKind.LATIOS:
                movement = LatiosMovement()
                return ProtectedPiece(piece_id, piece_kind, location, movement)
 
            case PieceKind.LATIAS:
                movement = LatiasMovement()
                return ProtectedPiece(piece_id, piece_kind, location, movement)

class PlayerTwoPositions:
    def get_positions(self) -> list[tuple[PlayerNumber, PieceKind, Location]]:

        positions = [
            (PlayerNumber.TWO, PieceKind.TURTWIG, Location(0, 0)),
            (PlayerNumber.TWO, PieceKind.PIKACHU, Location(0, 1)),
            (PlayerNumber.TWO, PieceKind.LATIOS, Location(0, 3)),
            (PlayerNumber.TWO, PieceKind.LATIAS, Location(0, 4)),
            (PlayerNumber.TWO, PieceKind.PIKACHU, Location(0, 6)),
            (PlayerNumber.TWO, PieceKind.TURTWIG, Location(0, 7)),
        ]

        positions += [
            (PlayerNumber.TWO, PieceKind.EEVEE, Location(1, n)) for n in range(8)
        ]

        return positions

class PlayerOnePositions:
    def get_positions(self) -> list[tuple[PlayerNumber, PieceKind, Location]]:

        positions = [
            (PlayerNumber.ONE, PieceKind.TURTWIG, Location(7, 0)),
            (PlayerNumber.ONE, PieceKind.PIKACHU, Location(7, 1)),
            (PlayerNumber.ONE, PieceKind.LATIOS, Location(7, 3)),
            (PlayerNumber.ONE, PieceKind.LATIAS, Location(7, 4)),
            (PlayerNumber.ONE, PieceKind.PIKACHU, Location(7, 6)),
            (PlayerNumber.ONE, PieceKind.TURTWIG, Location(7, 7)),
        ]

        positions += [
            (PlayerNumber.ONE, PieceKind.EEVEE, Location(6, n)) for n in range(8)
        ]

        return positions

class BoardSetter:
    def __init__(self, p1_positions: PiecePositions, p2_positions: PiecePositions):
        self._positions = p1_positions.get_positions() + p2_positions.get_positions()
    
    def set_board(self, board: Board) -> tuple[list[Piece | ProtectedPiece], list[Piece | ProtectedPiece]]:
        player1: list[Piece | ProtectedPiece] = []
        player2: list[Piece | ProtectedPiece] = []

        for player, kind, location in self._positions:
            piece = PieceFactory.make(kind, location)
            board.put(location.row, location.col, piece)

            if player == PlayerNumber.ONE:
                player1.append(piece)
            else:
                player2.append(piece)

        return player1, player2



class GameModel:
    @classmethod
    def default(cls) -> Self:

        board = Board(8, 8)

        setter = BoardSetter(PlayerOnePositions(), PlayerTwoPositions())
        player1_pieces, player2_pieces = setter.set_board(board)

        player1 = Player(PlayerNumber.ONE, player1_pieces, [])
        player2 = Player(PlayerNumber.TWO, player2_pieces, [])

        state = GameState(
            player_number = PlayerNumber.ONE,
            active_player = PlayerNumber.ONE,
            is_still_playable=True,
            captured_pieces= {PlayerNumber.ONE: player1.get_captured_pieces(), PlayerNumber.TWO: player2.get_captured_pieces()},
            board_pieces={PlayerNumber.ONE: player1.get_deployed_pieces(), PlayerNumber.TWO: player2.get_deployed_pieces()},
            move_count=3
        )

        return cls(state, board, player1, player2)


    def __init__(self, state: GameState, board: Board, player1: Player, player2: Player):
        self.state = state
        self._board = board
        self._player1 = player1
        self._player2 = player2
        
        ...

    def make_turn(self, action: PlayerAction):
        board = self._board
        player1 = self._player1
        player2 = self._player2

        match action.player_number:
            case PlayerNumber.ONE:
                player1.make_turn(board, action)
            case PlayerNumber.TWO:
                player2.make_turn(board, action)

    def new_game(self):
        ...