import pygame

from project_types import (
    TILE_PIXELS, BOARD_ROWS, BOARD_COLS, GameStatus,
    LivePiece, Location, GameState, PieceKind, ActionType, PlayerAction, PlayerNumber,
    MakeTurnObserver, NewGameObserver,
    )
from view import *

class OnlineView(GameView):
    """MVC class for online implementation"""
    def __init__(self, state: GameState):
        super().__init__(state)
    
    def _init_view_state(self):
        return super()._init_view_state()
    
    def on_state_change(self, state: GameState):
        return super().on_state_change(state)
    
    def _rerender_after_turn(self):
        return super()._rerender_after_turn()
    
    def register_make_turn_observer(self, observer: MakeTurnObserver):
        return super().register_make_turn_observer(observer)
    
    def register_new_game_observer(self, observer: NewGameObserver):
        return super().register_new_game_observer(observer)
    
    def _evaluate_winner(self):
        return super()._evaluate_winner()
    
    def _make_turn(self, action: PlayerAction):
        return super()._make_turn(action)
    
    def _new_game(self):
        return super()._new_game()
    
    def _render_text_result(self, text: str):
        return super()._render_text_result(text)

    def _mouse_press_on_board(self, abs_pos: tuple[int, int]):
        return super()._mouse_press_on_board(abs_pos)
    
    def _mouse_press_on_captures(self, abs_pos: tuple[int, int], player: PlayerNumber):
        return super()._mouse_press_on_captures(abs_pos, player)

    def run(self):
        return super().run()