"""
COMMENT:
I feel like since we're implementing an online-ish game, we're going to need another observer?
Something related to observing input from opposing player (and not input from view.py of current player)
"""

from model import GameModel
from view import GameView
from project_types import GameState, GameStateChangeObserver, Movement

class GameController:
    def __init__(self, model: GameModel, view: GameView):
        self._model = model
        self._view = view
        self._game_state_change_observers: list[GameStateChangeObserver] = []

    def start(self):
        view = self._view

        self.register_game_state_change_observer(view)
        view.register_make_turn_observer(self)
        view.register_new_game_observer(self)

        view.run()

    def register_game_state_change_observer(self, observer: GameStateChangeObserver):
        self._game_state_change_observers.append(observer)

    def on_make_turn(self, turn: Movement):
        self._model.make_turn(turn)
        self._on_state_change(self._model.state)

    def on_new_game(self):
        self._model.new_game()
        self._on_state_change(self._model.state)

    def _on_state_change(self, state: GameState):
        for observer in self._game_state_change_observers:
            observer.on_state_change(state)

    # some method that will map each Piece object to an image for the view