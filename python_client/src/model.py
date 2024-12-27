from typing import Self

from project_types import GameState, Movement, PieceKind
from view import Tile

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