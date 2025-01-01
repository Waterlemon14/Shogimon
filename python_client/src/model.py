from typing import Self

from project_types import GameState, Movement, PieceKind, Location, PlayerNumber, MovePossibilities, PiecePositions, LivePiece, PlayerAction, ActionType, GameStatus

class EeveeMovement(Movement):
    def get_movement_range(self, row: int, col: int, valid_locations: dict[tuple[int, int], bool]) -> list[tuple[int, int]]:
        
        return [
            (row + dr, col + dc)
            for dr, dc in MovePossibilities.FORWARD.value
            if 0 <= row + dr < 8 and 0 <= col + dc < 8 and (row + dr, col + dc) in valid_locations
        ]

class EeveeShinyMovement(Movement):
    def get_movement_range(self, row: int, col: int, valid_locations: dict[tuple[int, int], bool]) -> list[tuple[int, int]]:
        
        return [
            (row + dr, col + dc)
            for dr, dc in MovePossibilities.FORWARD_OPPOSITE.value
            if 0 <= row + dr < 8 and 0 <= col + dc < 8 and (row + dr, col + dc) in valid_locations
        ]

class PikachuMovement(Movement):
    def get_movement_range(self, row: int, col: int, valid_locations: dict[tuple[int, int], bool]) -> list[tuple[int, int]]:
        diagonals: list[tuple[int, int]] = []
        
        for dr, dc in MovePossibilities.DIAGONALS.value:

            temp_row, temp_col = row, col
            while 0 <= temp_row + dr < 8 and 0 <= temp_col + dc < 8 and (temp_row + dr, temp_col + dc) in valid_locations:
                temp_row += dr
                temp_col += dc
                if not valid_locations[(temp_row,temp_col)]: # if encounters a location with opponent piece (False), block the range
                    diagonals.append((temp_row, temp_col))
                    break
                diagonals.append((temp_row, temp_col))
        
        return diagonals

class TurtwigMovement(Movement):
    def get_movement_range(self, row: int, col: int, valid_locations: dict[tuple[int, int], bool]) -> list[tuple[int, int]]:
        orthogonals: list[tuple[int, int]] = []
        
        for dr, dc in MovePossibilities.ORTHOGONALS.value:

            temp_row, temp_col = row, col
            while 0 <= temp_row + dr < 8 and 0 <= temp_col + dc < 8 and (temp_row + dr, temp_col + dc) in valid_locations:
                temp_row += dr
                temp_col += dc
                if not valid_locations[(temp_row,temp_col)]: # if encounters a location with opponent piece (False), block the range
                    orthogonals.append((temp_row, temp_col))
                    break
                orthogonals.append((temp_row, temp_col))
        
        return orthogonals

class LatiosMovement(Movement):
    def get_movement_range(self, row: int, col: int, valid_locations: dict[tuple[int, int], bool]) -> list[tuple[int, int]]:
        return [
            (row + dr, col + dc)
            for dr, dc in MovePossibilities.ORTHOGONALS.value
            if 0 <= row + dr < 8 and 0 <= col + dc < 8 and (row + dr, col + dc) in valid_locations and valid_locations[(row + dr, col + dc)] # Latios cannot capture hence only locations with True values are considered
        ]
    
class LatiasMovement(Movement):
    def get_movement_range(self, row: int, col: int, valid_locations: dict[tuple[int, int], bool]) -> list[tuple[int, int]]:
         return [
            (row + dr, col + dc)
            for dr, dc in MovePossibilities.DIAGONALS.value
            if 0 <= row + dr < 8 and 0 <= col + dc < 8 and (row + dr, col + dc) in valid_locations and valid_locations[(row + dr, col + dc)]
            # Latias cannot capture hence only locations with True values are considered
        ]

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
    def __init__(self, id: int, kind: PieceKind, location: Location, movement: Movement, owner: PlayerNumber):
        self._id = id
        self._kind = kind
        self.location = location
        self._is_captured = False
        self._movement = movement
        self._owner = owner

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
    def owner(self) -> PlayerNumber:
        return self._owner

    @property
    def is_captured(self) -> bool:
        return self._is_captured

    def can_move(self, row: int, col: int, grid: dict[tuple[int, int], bool]) -> bool:
        
        return (row, col) in self._movement.get_movement_range(self.row, self.col, grid)
    
    def get_movement_range(self, grid: dict[tuple[int, int], bool]) -> list[tuple[int, int]]:
        return self._movement.get_movement_range(self.row, self.col, grid)
    
    def switch_ownership(self):
        self._owner = PlayerNumber.ONE if self._owner == PlayerNumber.TWO else PlayerNumber.ONE
  

class ProtectedPiece(Piece):
    def __init__(self, id: int, kind: PieceKind, location: Location, movement: Movement, owner: PlayerNumber):
        super().__init__(id, kind, location, movement, owner)
        self.is_immobile = False
    

class Board:
    def __init__(self, height: int, width: int):
        self._height: int = height
        self._width: int = width
        self._protected_pieces: dict[PlayerNumber, list[ProtectedPiece]] = {PlayerNumber.ONE: [], PlayerNumber.TWO: []}
        self._live_pieces: dict[PlayerNumber, list[Piece]] = {PlayerNumber.ONE: [], PlayerNumber.TWO: []}
        self._captured_pieces: dict[PlayerNumber, list[Piece]] = {PlayerNumber.ONE: [], PlayerNumber.TWO: []}
        self._grid: list[list[Piece | ProtectedPiece | None]] = [[ None for _ in range(width)] for _ in range(height)]
        ...

    def get_live_pieces(self) -> list[LivePiece]:
        """
        For GameState
        """
        return [

                LivePiece(piece.kind, piece.id, piece.owner, self.get_piece_movable_locations(piece), Location(piece.row, piece.col)) 
                for piece in (self._live_pieces[PlayerNumber.ONE] + self._protected_pieces[PlayerNumber.ONE])

            ] + [

                LivePiece(piece.kind, piece.id, piece.owner, self.get_piece_movable_locations(piece), Location(piece.row, piece.col)) 
                for piece in (self._live_pieces[PlayerNumber.TWO] + self._protected_pieces[PlayerNumber.TWO])
                
            ]

    def get_captured_pieces(self) -> list[LivePiece]:
        """
        For GameState
        """
        return [
            
                LivePiece(piece.kind, piece.id, piece.owner, None, None) 
                for piece in self._captured_pieces[PlayerNumber.ONE]

            ] + [

                LivePiece(piece.kind, piece.id, piece.owner, None, None) 
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
            captured_piece.switch_ownership()
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
    
    def get_movable_locations_mapping(self, owner: PlayerNumber) -> dict[tuple[int, int], bool]:

        grid = self._grid
        locations: dict[tuple[int, int], bool] = {}
        """
        Location will be true if empty 
        Location will be false if opponent piece
        """

        for row in range(self._height):
            for col in range(self._width):
                piece = grid[row][col]

                if not piece:
                    locations[(row, col)] = True
                elif piece.owner != owner:
                    locations[(row, col)] = False

        return locations
    
    def get_all_movable_locations(self, player: PlayerNumber) -> list[tuple[int, int]]:
        locations: list[tuple[int, int]] = []

        for piece in self._live_pieces[player] + self._protected_pieces[player]:
            
            
            locations.extend(piece.get_movement_range(self.get_movable_locations_mapping(player)))

            if piece.id == 19:
                print(piece.get_movement_range(self.get_movable_locations_mapping(player)))

        return locations
    
    def get_piece_movable_locations(self, piece: Piece | ProtectedPiece) -> list[Location]:

        return [Location(row, int) for row, int in piece.get_movement_range(self.get_movable_locations_mapping(piece.owner))]
    
    def is_valid_location(self, row: int, col: int) -> bool:
        loc = self._grid[row][col]

        for piece in self._protected_pieces[PlayerNumber.ONE] + self._protected_pieces[PlayerNumber.TWO]:
            if (row, col) in piece.get_movement_range(self.get_movable_locations_mapping(piece.owner)):
                return False
            
        return not loc

    def is_safe_location(self, row: int, col: int, curr_player: PlayerNumber) -> bool:
        opponent = PlayerNumber.TWO if curr_player == PlayerNumber.ONE else PlayerNumber.ONE

        unsafe_locations = self.get_all_movable_locations(opponent)

        if (row, col) in unsafe_locations:
            return False
            
        return True

    def is_checkmate(self, curr_player: PlayerNumber) -> bool:
        opponent = PlayerNumber.TWO if curr_player == PlayerNumber.ONE else PlayerNumber.ONE
        """
        Checks if Latias and Latios of each player can still move
        """
        unsafe_locations = self.get_all_movable_locations(curr_player)

        for protected in self._protected_pieces[opponent]:
            possible_moves = protected.get_movement_range(self.get_movable_locations_mapping(opponent))
            danger: list[bool] = []

            for r, c in possible_moves:
                if (r, c) in unsafe_locations:
                    danger.append(True)
                else:
                    danger.append(False)

            protected.is_immobile = True  if all(danger) else False
            
        return all([piece.is_immobile for piece in self._protected_pieces[opponent]])
    
class PieceFactory:
    _piece_count = 0

    @classmethod
    def make(cls, piece_kind: PieceKind,
             location: Location, owner: PlayerNumber) -> Piece | ProtectedPiece:
        piece_id = cls._piece_count
        cls._piece_count += 1

        match piece_kind:
            case PieceKind.EEVEE:
                movement = EeveeMovement()
                return Piece(piece_id, piece_kind, location, movement, owner)

            case PieceKind.EEVEE_SHINY:
                movement = EeveeShinyMovement()
                return Piece(piece_id, piece_kind, location, movement, owner)

            case PieceKind.PIKACHU:
                movement = PikachuMovement()
                return Piece(piece_id, piece_kind, location, movement, owner)
 
            case PieceKind.TURTWIG:
                movement = TurtwigMovement()
                return Piece(piece_id, piece_kind, location, movement, owner)
 
            case PieceKind.LATIOS:
                movement = LatiosMovement()
                return ProtectedPiece(piece_id, piece_kind, location, movement, owner)
 
            case PieceKind.LATIAS:
                movement = LatiasMovement()
                return ProtectedPiece(piece_id, piece_kind, location, movement, owner)

class DefaultPositions:
    def get_positions(self) -> list[tuple[PlayerNumber, PieceKind, Location]]:

        # Player Two
        positions = [
            (PlayerNumber.TWO, PieceKind.TURTWIG, Location(0, 0)),
            (PlayerNumber.TWO, PieceKind.PIKACHU, Location(0, 1)),
            (PlayerNumber.TWO, PieceKind.LATIOS, Location(0, 3)),
            (PlayerNumber.TWO, PieceKind.LATIAS, Location(0, 4)),
            (PlayerNumber.TWO, PieceKind.PIKACHU, Location(0, 6)),
            (PlayerNumber.TWO, PieceKind.TURTWIG, Location(0, 7)),
        ]

        positions += [
            (PlayerNumber.TWO, PieceKind.EEVEE_SHINY, Location(1, n)) for n in range(8)
        ]

        # Player One
        positions += [
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

# If we need to add game pieces, we create another PiecePosition Class

class BoardSetter:
    def __init__(self, positions: PiecePositions):
        self._positions = positions.get_positions()
    
    def set_board(self, board: Board):


        for player, kind, location in self._positions:
            piece = PieceFactory.make(kind, location, player)
            board.put(location.row, location.col, piece, player)

class GameModel:
    @classmethod
    def default(cls) -> Self:

        board = Board(8, 8)

        setter = BoardSetter(DefaultPositions())
        setter.set_board(board)


        state = GameState(
            player_number = PlayerNumber.ONE,
            active_player = PlayerNumber.ONE,
            captured_pieces= board.get_captured_pieces(),
            live_pieces=board.get_live_pieces(),
            action_count=3,
            game_status=GameStatus.ONGOING
        )

        return cls(state, board, PlayerNumber.ONE, 3)


    def __init__(self, state: GameState, board: Board, player: PlayerNumber, action_count: int):
        self._state = state
        self._board = board
        self._active_player = player
        self._action_count = action_count
        self._is_game_over = False
        self._winner: PlayerNumber
    
    @property
    def state(self) -> GameState:
        return self._state
    
    def _update_state(self):

        if self._action_count == 0:
            self._active_player = PlayerNumber.ONE if self._active_player == PlayerNumber.TWO else PlayerNumber.TWO
            self._action_count = 3

        self._state = GameState(
            player_number = PlayerNumber.ONE,
            active_player = self._active_player,
            captured_pieces= self._board.get_captured_pieces(),
            live_pieces=self._board.get_live_pieces(),
            action_count=self._action_count,
            game_status=GameStatus.PLAYER_WIN if self._winner == PlayerNumber.ONE else GameStatus.PLAYER_LOSE
        )


    def _check_if_game_over(self) -> PlayerNumber | None:
        board = self._board
        if board.is_checkmate(self._active_player):
            self._winner = self._active_player

        self._is_game_over = True

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
                if piece_to_move:
                    
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
                    elif type(piece_to_move) == ProtectedPiece and board.is_safe_location(target_row, target_col, player_number):

                        board.take(piece_to_move.row, piece_to_move.col)
                        board.move(target_row, target_col, piece_to_move)


            case ActionType.DROP:
                piece_to_drop = board.get_captured_piece(id, player_number)

                if piece_to_drop and board.is_valid_location(target_row, target_col):
                    board.drop(target_row, target_col, piece_to_drop, player_number)

        self._action_count -= 1
        self._check_if_game_over()
        self._update_state()

    def mouse_click(self, id: int):
        ...
        
    def new_game(self):
        ...