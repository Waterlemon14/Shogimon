from typing import Self
from cs150241project_networking import CS150241ProjectNetworking

from model import *
from project_types import PlayerAction, PlayerNumber

class OnlineModel(GameModel):
    def __init__(self, state: GameState, board: Board, player: PlayerNumber, action_count: int):
        super().__init__(state, board, player, action_count)

    def _update_state(self):
        return super()._update_state()
    
    def _check_if_game_over(self) -> PlayerNumber | None:
        return super()._check_if_game_over()
    
    
    def make_action(self, action: PlayerAction):
        return super().make_action(action)

    def new_game(self):
        return super().new_game()
