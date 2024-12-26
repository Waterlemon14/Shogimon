from model import GameModel
from view import GameView
# TO DO: ADD IMPORTS

class GameController:
    def __init__(self, model: GameModel, view: GameView):
        self._model = model
        self._view = view
        self._game_state_change_observers = []

    def start(self):
        self._view.run()

    def on_make_turn(self):
        self._model.make_turn()

    def on_new_game(self):
        ...

    def register_game_state_change_observer(self, observer: GameStateChangeObserver):
        # TO DO: ADD IMPORTS
        self._game_state_change_observers.append(observer)