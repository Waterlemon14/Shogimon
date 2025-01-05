from online_model import OnlineModel
from online_view import OnlineView
from controller import GameController
from cs150241project_networking import CS150241ProjectNetworking

if __name__ == '__main__':
    networking = CS150241ProjectNetworking.connect('localhost', 15000)
    model = OnlineModel.default()

    model.register_network(networking)
    
    for message in networking.recv():
        model.receive_board_settings(message)
        break

    view = OnlineView(model.state, networking)
    controller = GameController(model, view)

    controller.start()