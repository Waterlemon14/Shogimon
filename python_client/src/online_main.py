from online_model import OnlineModel
from online_view import OnlineView
from controller import GameController

if __name__ == '__main__':


    model = OnlineModel.default()
    view = OnlineView(model.state)

    controller = GameController(model, view)

    controller.start()