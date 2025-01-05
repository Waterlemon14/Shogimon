import pygame
from cs150241project_networking import CS150241ProjectNetworking, Message

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
        """When mouse is clicked inside RenderableBoard rect"""
        if self._game_status == GameStatus.ONGOING:
            _row = (abs_pos[1] - 105) // TILE_PIXELS
            _col = (abs_pos[0] - 129) // TILE_PIXELS

            tile = self._renderable_board.get_tile(Location(_row,_col))

            if tile.occupier is not None and tile.occupier.owner == self._active_player:
                self._start_move_turn(Location(_row,_col))

            elif tile.is_targetable and self._current_hovered_piece is not None:
                _returned = self._finish_turn(Location(_row, _col))
                self._send_message(_returned)
                
    
    def _start_move_turn(self, loc: Location):
        return super()._start_move_turn(loc)
    
    def _finish_turn(self, loc: Location) -> PlayerAction:
        return super()._finish_turn(loc)
    
    def _is_cursor_on_captures(self, pos: tuple[int, int]):
        return super()._is_cursor_on_captures(pos)
    
    def _send_message(self, action: PlayerAction):
        """Same as make_turn, but for online purposes"""
        message = self._parse_to_message(action)

        if message:
            self._networking.send(message.payload)

    def _receive_message(self, message: Message):
        """Use received message to manipulate client"""
        action = self._parse_to_player_action(message)

        if action:
            self._make_turn(action)
            self._rerender_after_turn()
        ...
    
    def _parse_to_player_action(self, message: Message) -> PlayerAction | None:
        """Convert type message to PlayerAction (if valid; else None)"""
        properties = message.payload.split('%')

        if len(properties) != 5:
            return None
        
        action_type = ActionType.MOVE if properties[0] == ActionType.MOVE else ActionType.DROP

        player_number = PlayerNumber.ONE if properties[1] == PlayerNumber.ONE else PlayerNumber.TWO

        if action_type == ActionType.DROP:
            source_location = None
        else:
            source_location = Location(int(properties[2][0]), int(properties[2][2]))

        kind = PieceKind.EEVEE
        for k in PieceKind:
            if k.value == properties[4]:
                kind = k

        return PlayerAction(
            action_type,
            player_number,
            source_location,
            Location(int(properties[3][0]), int(properties[3][2])),
            kind
            )
    
    def _parse_to_message(self, action: PlayerAction) -> Message | None:
        """Convert type PlayerAction to message (if valid; else None)"""
        source_loc = f"{action.source_location.row}-{action.source_location.col}" if action.source_location else f""
        payload = f"{action.action_type.value}%{action.player.value}%{source_loc}%{action.target_location.row}-{action.target_location.col}%{action.kind}"

        return Message(source=self._server_id, payload=payload)


    def run(self):
        """Edited to incorporate networking"""
        pygame.init()

        self._screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self._clock = pygame.time.Clock()

        _game_is_running = True

        while _game_is_running:
            for message in self._networking.recv():
                self._receive_message(message)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    _game_is_running = False

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self._new_game()
                    self._init_view_state()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and ((self._server_id == 1 and self._active_player == PlayerNumber.ONE) or (self._server_id == 2 and self._active_player == PlayerNumber.TWO)):
                    """Create string _to_message; to be sent to the networking server"""
                    _to_send = 'INVALID'

                    if self._renderable_board.rect.collidepoint(event.pos):
                        self._mouse_press_on_board(event.pos)
                        _to_send = '...'
                    
                    elif self._is_cursor_on_captures(event.pos):
                        self._mouse_press_on_captures(event.pos, self._active_player)
                        _to_send = '...'
                        
                    self._networking.send(_to_send)

            self._screen.fill('black')
            self._renderable_board.render_to_screen(self._screen)
            self._captures_p1.render_to_screen(self._screen)
            self._captures_p2.render_to_screen(self._screen)

            if self._game_status != GameStatus.ONGOING:
                self._evaluate_winner()

            pygame.display.flip()
            self._clock.tick(60)

        pygame.quit()