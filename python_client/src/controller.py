import pygame

from model import GameModel
from view import GameView

class GameController:
    def __init__(self, model: GameModel, view: GameView):
        self._model = model
        self._view = view

    def start(self):
        ...