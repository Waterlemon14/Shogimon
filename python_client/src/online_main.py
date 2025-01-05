from online_model import OnlineModel
from online_view import OnlineView
from online_controller import OnlineController

if __name__ == '__main__':
    model = OnlineModel.default()
    view = OnlineView(model.state)

    controller = OnlineController(model, view)

    controller.start()