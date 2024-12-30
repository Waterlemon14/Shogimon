from typing import Self

from project_types import GameState, Movement, PieceKind, Location, PlayerNumber, MovePossibilities, PiecePositions, LivePiece, PlayerAction, ActionType

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
        self.location = location
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
        return self.location.row
    
    @property
    def col(self) -> int:
        return self.location.col

    @property
    def is_captured(self) -> bool:
        return self._is_captured

    def can_move(self, row: int, col: int) -> bool:
        return any(
            True for dr, dc in self._movement.get_movement_range()
            if self.row + dr == row and
            self.col + dc == col
        )
    
    def get_possible_moves(self) -> list[tuple[int, int]]:

        possible_moves: list[tuple[int, int]] = []

        for dr, dc in self._movement.get_movement_range():
            possible_moves.append((self.row + dr, self.col + dc))

        return possible_moves

class ProtectedPiece:
    def __init__(self, id: int, kind: PieceKind, location: Location, movement: Movement):
        self._id = id
        self._kind = kind
        self.location = location
        self._movement = movement
    
    @property
    def id(self) -> int:
        return self._id

    @property
    def kind(self) -> PieceKind:
        return self._kind
    
    @property
    def row(self) -> int:
        return self.location.row
    
    @property
    def col(self) -> int:
        return self.location.col

    def can_move(self, row: int, col: int) -> bool:
        
        return any(
            True for dr, dc in self._movement.get_movement_range()
            if self.row + dr == row and
            self.col + dc == col
        )

class Board:
    def __init__(self, height: int, width: int):
        self._height: int = height
        self._width: int = width
        self._protected_pieces: dict[PlayerNumber, list[ProtectedPiece]] = {}
        self._live_pieces: dict[PlayerNumber, list[Piece]] = {}
        self._captured_pieces: dict[PlayerNumber, list[Piece]] = {}
        self._grid: list[list[Piece | ProtectedPiece | None]]
        ...

    def get_live_pieces(self) -> list[LivePiece]:
        """
        For GameState
        """
        return [

                LivePiece(piece.kind, piece.id, PlayerNumber.ONE, Location(piece.row, piece.col)) 
                for piece in (self._live_pieces[PlayerNumber.ONE] + self._protected_pieces[PlayerNumber.ONE])

            ] + [

                LivePiece(piece.kind, piece.id, PlayerNumber.TWO, Location(piece.row, piece.col)) 
                for piece in (self._live_pieces[PlayerNumber.TWO] + self._protected_pieces[PlayerNumber.TWO])
                
            ]

    def get_captured_pieces(self) -> list[LivePiece]:
        """
        For GameState
        """
        return [
            
                LivePiece(piece.kind, piece.id, PlayerNumber.ONE, None) 
                for piece in self._captured_pieces[PlayerNumber.ONE]

            ] + [

                LivePiece(piece.kind, piece.id, PlayerNumber.TWO, None) 
                for piece in self._captured_pieces[PlayerNumber.TWO]
                
            ]


    def get_live_piece(self, id: int, player: PlayerNumber) -> Piece | ProtectedPiece | None:
        for piece in self._live_pieces[player] + self._protected_pieces[player]:
            if piece.id == id:
                return piece
            
    def get_captured_piece(self, id: int, player: PlayerNumber) -> Piece | None:
        for piece in self._captured_pieces[player]:
            if piece.id == id:
                return piece
    
    def _live_to_captured(self, id: int, captured_player: PlayerNumber, capturing_player: PlayerNumber):
        for piece in self._live_pieces[captured_player]:
            if piece.id == id and type(piece) == Piece:
                self._live_pieces[captured_player].remove(piece)
                self._captured_pieces[capturing_player].append(piece)

    def _captured_to_live(self, id: int, player: PlayerNumber):
        for piece in self._captured_pieces[player]:
            if piece.id == id:
                self._captured_pieces[player].remove(piece)
                self._live_pieces[player].append(piece)
    
    def put(self, row: int, col: int, piece: Piece | ProtectedPiece, player: PlayerNumber):
        live_pieces = self._live_pieces[player]
        protected_pieces = self._protected_pieces[player]
        if type(piece) == Piece:
            live_pieces.append(piece)
        elif type(piece) == ProtectedPiece:
            protected_pieces.append(piece)
        self._grid[row][col] = piece

    def take(self, row: int, col: int):
        self._grid[row][col] = None
        
    def move(self, row: int, col: int, piece: Piece | ProtectedPiece):
        piece.location = Location(row, col)
        self._grid[row][col] = piece
    
    def capture(self, row: int, col: int, capturing_player: PlayerNumber, capturing_piece: Piece):
        captured_player = PlayerNumber.TWO if capturing_player == PlayerNumber.ONE else PlayerNumber.ONE

        captured_piece = self._grid[row][col]

        capturing_piece.location = Location(row, col)
        self._grid[row][col] = capturing_piece

        if captured_piece:
            self._live_to_captured(captured_piece.id, captured_player, capturing_player)

    def drop(self, row: int, col: int, piece: Piece, player: PlayerNumber):
        self._grid[row][col] = piece
        piece.location = Location(row, col)
        self._captured_to_live(piece.id, player)

    def can_capture(self, row: int, col: int) -> bool:
        piece = self._grid[row][col]
        if piece and type(piece) == Piece:
            return True
        
        return False

    def is_unoccupied(self, row: int, col: int) -> bool:
        loc = self._grid[row][col]
        return not loc

    def is_safe(self, row: int, col: int, curr_player: PlayerNumber) -> bool:
        opponent = PlayerNumber.TWO if curr_player == PlayerNumber.ONE else PlayerNumber.ONE

        for piece in self._live_pieces[opponent]:
            if (row, col) in piece.get_possible_moves():
                return False
            
        return True

    
    def is_checkmate(self) -> bool:
        """
        Checks if Latias and Latios of each player can still move
        """
        # player1_protected = self._protected_pieces[PlayerNumber.ONE]
        # player2_protected = self._protected_pieces[PlayerNumber.TWO]
        
        return True

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
    
    def set_board(self, board: Board):

        for player, kind, location in self._positions:
            piece = PieceFactory.make(kind, location)
            board.put(location.row, location.col, piece, player)

class GameModel:
    @classmethod
    def default(cls) -> Self:

        board = Board(8, 8)

        setter = BoardSetter(PlayerOnePositions(), PlayerTwoPositions())
        setter.set_board(board)


        state = GameState(
            player_number = PlayerNumber.ONE,
            active_player = PlayerNumber.ONE,
            is_still_playable=True,
            captured_pieces= board.get_captured_pieces(),
            live_pieces=board.get_live_pieces(),
            action_count=3
        )

        return cls(state, board, PlayerNumber.ONE)


    def __init__(self, state: GameState, board: Board, player: PlayerNumber):
        self._state = state
        self._board = board
        self._active_player = player
    
    @property
    def state(self) -> GameState:
        return self._state

    def _update_state(self):
        pass

    def _check_if_game_over(self) -> PlayerNumber | None:
        board = self._board

        pass

    def make_action(self, action: PlayerAction):
        board = self._board
        target_row = action.target_location.row
        target_col = action.target_location.col
        player_number = action.player_number
        id = action.piece_id

        match action.action_type:

            case ActionType.MOVE:
                piece_to_move = board.get_live_piece(id, player_number)

                # Narrow type down
                if piece_to_move and piece_to_move.can_move(target_row, target_col):
                    
                    # If regular piece, capture or move
                    if type(piece_to_move) == Piece:
                        board.take(piece_to_move.row, piece_to_move.col)

                        # Check if can capture
                        if board.can_capture(target_row, target_col):
                            
                            board.capture(target_row, target_col, player_number, piece_to_move)

                        # Move piece simply  
                        else:
                            board.move(target_row, target_col, piece_to_move)

                    # If protected piece, check if target location is valid
                    elif type(piece_to_move) == ProtectedPiece and board.is_safe(target_row, target_col, player_number):

                        board.take(piece_to_move.row, piece_to_move.col)
                        board.move(target_row, target_col, piece_to_move)


            case ActionType.DROP:
                piece_to_drop = board.get_captured_piece(id, player_number)

                if piece_to_drop and board.is_unoccupied(target_row, target_col):
                    board.drop(target_row, target_col, piece_to_drop, player_number)

        # will check if game over here
        # will update game state here

    def new_game(self):
        ...