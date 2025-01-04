import pygame

from project_types import (
    TILE_PIXELS, BOARD_ROWS, BOARD_COLS, GameStatus,
    LivePiece, Location, GameState, PieceKind, ActionType, PlayerAction, PlayerNumber,
    MakeTurnObserver, NewGameObserver,
    )
from view import (
    Captures, Tile, RenderableBoard, GameView
    )

class OnlineView(GameView):
    ...