import pygame
from cs150241project_networking import CS150241ProjectNetworking
from typing import Generator

from project_types import (
    TILE_PIXELS, BOARD_ROWS, BOARD_COLS,
    GameStatus, PieceKind, ActionType, Location, PlayerNumber,
    LivePiece, GameState, PlayerAction,
    MakeTurnObserver, NewGameObserver,
    )
from view import *

class OnlineView(GameView):
    """MVC class for online implementation"""
    def __init__(self, state: GameState):
        super().__init__(state)

        self._networking = CS150241ProjectNetworking.connect('localhost', 15000)
        self._server_id = self._networking.player_id

    def _init_view_state(self):
        return super()._init_view_state()
    
    def on_state_change(self, state: GameState):
        return super().on_state_change(state)
    
    def _parse_generator_to_gamestate(self, generator: Generator) -> GameState:
        """LOGIC"""
        ...
    
    def _rerender_after_turn(self):
        return super()._rerender_after_turn()
    
    def register_make_turn_observer(self, observer: MakeTurnObserver):
        return super().register_make_turn_observer(observer)
    
    def register_new_game_observer(self, observer: NewGameObserver):
        return super().register_new_game_observer(observer)
    
    def _evaluate_winner(self):
        return super()._evaluate_winner()
    
    def _make_turn(self, action: PlayerAction):
        return super()._make_turn(action)
    
    def _new_game(self):
        return super()._new_game()
    
    def _render_text(self, text: str):
        return super()._render_text(text)

    def _mouse_press_on_board(self, abs_pos: tuple[int, int]):
        return super()._mouse_press_on_board(abs_pos)
    
    def _start_move_turn(self, loc: Location):
        return super()._start_move_turn(loc)
    
    def _finish_turn(self, loc: Location) -> PlayerAction:
        return super()._finish_turn(loc)
    
    def _mouse_press_on_captures(self, abs_pos: tuple[int, int], player: PlayerNumber):
        return super()._mouse_press_on_captures(abs_pos, player)

    def run(self):
        """Main game running logic; Equivalent to main()"""
        pygame.init()

        self._screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._clock = pygame.time.Clock()

        _game_is_running = True

        while _game_is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    _game_is_running = False

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self._new_game()
                    self._init_view_state()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self._renderable_board.rect.collidepoint(event.pos):
                        self._mouse_press_on_board(event.pos)
                        self._networking.send(...)
                    
                    elif (self._active_player == PlayerNumber.ONE and self._captures_p1.rect.collidepoint(event.pos)) \
                    or (self._active_player == PlayerNumber.TWO and self._captures_p2.rect.collidepoint(event.pos)):
                        self._networking.send(...)
                        self._mouse_press_on_captures(event.pos, self._active_player)

            self._screen.fill('black')

            self._renderable_board.render_to_screen(self._screen)

            self._captures_p1.render_to_screen(self._screen)
            self._captures_p2.render_to_screen(self._screen)

            if self._game_status != GameStatus.ONGOING:
                self._evaluate_winner()

            pygame.display.flip()

            self._clock.tick(60)

        pygame.quit()