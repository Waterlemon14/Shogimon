from cs150241project_networking import CS150241ProjectNetworking, Message
from project_types import (
    TILE_PIXELS, BOARD_ROWS, BOARD_COLS,
    GameStatus, PieceKind, ActionType, Location, PlayerNumber,
    LivePiece, GameState, PlayerAction,
    MakeTurnObserver, NewGameObserver,
    )
from model import *
from typing import Callable

class OnlineModel(GameModel):
    
    def __init__(self, state: GameState, board: Board, player: PlayerNumber, action_count: int, height: int, width: int, positions: PiecePositions):
        super().__init__(state, board, player, action_count, height, width, positions)
        # self._send_board_settings()
    
    def register_network(self, networking: CS150241ProjectNetworking):
        self._networking = networking
        self._send_board_settings()
        self._parse_to_piece_positions(f"{self._height}%{self._width}%{self._to_string(self._positions)}")

    def _adjust_board_settings(self, height: int, width: int, positions: PiecePositions):
        self._board = Board(height, width)
        setter = BoardSetter(positions)
        setter.set_board(self._board)

        self._state = GameState(
            PlayerNumber.ONE,
            self._board.get_captured_pieces(),
            self._board.get_live_pieces(),
            3,
            GameStatus.ONGOING
        )
        pass
    
    def receive_board_settings(self, message: Message):
        
        payload = message.payload
        parameters = payload.split('%')
        height = int(parameters[0])
        width = int(parameters[1])
        positions = self._parse_to_piece_positions(parameters[2])
        self._adjust_board_settings(height, width, positions)

    def _send_board_settings(self):
        positions = self._to_string(self._positions)

        payload = f"{self._height}%{self._width}%{positions}"
        self._networking.send(payload)

    def _kind_to_payload(self, kind: str) -> str:
        match kind:
            case "eevee"    | "eevee_shiny":
                return "p"
            case "turtwig"  | "turtwig_shiny":
                return "r"
            case "pikachu"  | "pikachu_shiny":
                return "b"
            case "latias"   | "latias_shiny":
                return "q"
            case "latios"   | "latios_shiny":
                return "k"
            case _:
                return "x"

    def _payload_to_kind(self, kind: str, pnum: str) -> str:
        proper_kind = ""
        match kind:
            case "p":
                proper_kind = "eevee"
                if pnum == "2":
                    proper_kind += "_shiny"
            case "r":
                proper_kind = "turtwig"
            case "b":
                proper_kind = "pikachu"
            case "q":
                proper_kind = "latias"
            case "k":
                proper_kind = "latios"
            case _:
                proper_kind = "x"       # should not reach this

        

        return proper_kind


    def _to_string(self, positions: PiecePositions) -> str:
        data = positions.get_positions()
        returnable: list[str] = []

        for item in data:
            print(item)
            returnable.append(f"{ "1" if item[0].value == "one" else "2" }{ self._kind_to_payload(item[1].value) \
                                                 }{ item[2].row }{ item[2].col }")

        print(" ".join(returnable))

        return " ".join(returnable)
        
    def _parse_to_piece_positions(self, payload: str) -> PiecePositions:

        intparser: Callable[[list[str]], list[int]] = lambda x : [int(i) for i in x]

        tuples: list[str] = payload.split("%")[-1].split(" ")

        all: list[list[str]] = [[i for i in item] for item in tuples]
        print(all)

        for i in all:
            print(i)

        positions = [
            (PlayerNumber("one" if pnum == "1" else "two"), PieceKind(self._payload_to_kind(pkind, pnum)), Location(*intparser([row, col])))
            for pnum, pkind, row, col in all
            ]

        return NewPiecePositions(positions)

class NewPiecePositions:
    def __init__(self, positions: list[tuple[PlayerNumber, PieceKind, Location]]) -> None:
        self._positions = positions
    def get_positions(self) -> list[tuple[PlayerNumber, PieceKind, Location]]:
        return self._positions