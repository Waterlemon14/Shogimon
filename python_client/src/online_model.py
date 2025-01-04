from typing import Self

from project_types import *
from model import *

class OnlineModel(GameModel):
    def __init__(self, state: GameState, board: Board, player: PlayerNumber, action_count: int):
        super().__init__(state, board, player, action_count)

    def _update_state(self):
        return super()._update_state()
    
    # ikaw na magtuloy brother

