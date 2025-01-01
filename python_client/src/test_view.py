from view import GameView
from model import GameModel

if __name__ == '__main__':
    model = GameModel.default()
    view = GameView(model.state)
    view.run()