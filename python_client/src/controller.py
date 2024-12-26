from model import GameModel
from view import GameView

class GameController:
    def __init__(self, model: GameModel, view: GameView):
        self._model = model
        self._view = view

    def on_make_turn(self):
        ...

    def on_next_round(self):
        self._model.next_round()

    def on_new_game(self):
        ...

    def start(self):
        self._view.run()