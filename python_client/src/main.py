from model import GameModel
from view import GameView
from controller import GameController

if __name__ == '__main__':
    model = GameModel()
    view = GameView()

    controller = GameController(model, view)

    controller.start()