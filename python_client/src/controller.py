from model import GameModel
from view import GameView
from project_types import GameStateChangeObserver, Movement

class GameController:
    def __init__(self, model: GameModel, view: GameView):
        self._model = model
        self._view = view
        self._game_state_change_observers = []

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

    def on_new_game(self):
        self._model.new_game()