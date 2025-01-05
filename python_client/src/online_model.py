from typing import Self
from cs150241project_networking import CS150241ProjectNetworking

from model import *
from project_types import PlayerAction, PlayerNumber

class OnlineModel(GameModel):
    def __init__(self, state: GameState, board: Board, player: PlayerNumber, action_count: int):
        super().__init__(state, board, player, action_count)
        self._network = CS150241ProjectNetworking.connect('localhost', 15000)
    
    def send_message():
        pass

    def receive_message():
        
