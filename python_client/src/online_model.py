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
        self._send_board_settings()
    
    def register_network(self, networking: CS150241ProjectNetworking):
        self._networking = networking

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

    def _to_string(self, positions: PiecePositions) -> str:
        data = positions.get_positions()
        returnable: list[str] = []

        for item in data:
            returnable.append(f"{ item[0].value }-{ item[1].value }-{ item[2].row },{ item[2].col }")

        return " ".join(returnable)
        
    def _parse_to_piece_positions(self, payload: str) -> PiecePositions:

        intparser: Callable[[list[str]], list[int]] = lambda x : [int(i) for i in x]

        tuples: list[str] = payload.split(" ")

        all: list[list[str]] = [item.split("-") for item in tuples]

        positions = [
            (PlayerNumber(pnum), PieceKind(pkind), Location(*intparser(loc.split(","))))
            for pnum, pkind, loc in all
            ]

        def get_positions() -> list[tuple[PlayerNumber, PieceKind, Location]]:
            return positions

        return type('NewPiecePositions', (), {"get_positions": get_positions})  