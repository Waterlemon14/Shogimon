module Main
  ( main
  , onKeyDown
  , onKeyUp
  , onMessage
  , onMouseDown
  , onRender
  , onTick
  )
  where

import Prelude

import CS150241Project.GameEngine (startNetworkGame)
import CS150241Project.Graphics (clearCanvas, drawImageScaled, drawText, drawRect, drawCircle)
import CS150241Project.Networking (Message)
import Data.Int (toNumber, floor)
import Data.Map as Map
import Data.Maybe (Maybe(..))
import Data.List (List(..), (:), concat)
import Data.Array (replicate, (!!))
import Data.Foldable (elem)
import Effect (Effect)
import Effect.Console (log)
import Graphics.Canvas as Canvas

import Movements
  ( getPossibleMoves
  , accessCell
  )

import ProjectTypes
  ( Kind(..)
  , Position
  , Board
  , PlayerNum(..)
  , Piece
  , Captured
  , GameState
  )

import Config
  ( width
  , height
  , rows
  , columns
  , cell_width
  , cell_height
  , board_start_x
  , board_start_y
  , canvas_offset_x
  , canvas_offset_y
  , fps
  , images
  )


createBishop :: Int -> Int -> PlayerNum -> Maybe Piece
createBishop col row player_num = Just {kind: Bishop, position: {col:col,row:row}, image: "pikachu.png", player: player_num}

createPawn :: Int -> Int -> PlayerNum -> Maybe Piece
createPawn col row One = Just {kind: Pawn, position: {col:col,row:row}, image: "eevee.png", player: One}
createPawn col row Two = Just {kind: Pawn, position: {col:col,row:row}, image: "eevee-shiny.png", player: Two}

createRook :: Int -> Int -> PlayerNum -> Maybe Piece
createRook col row player_num = Just {kind: Rook, position: {col:col,row:row}, image: "turtwig.png", player: player_num}

createPrince :: Int -> Int -> PlayerNum -> Maybe Piece
createPrince col row player_num = Just {kind: Prince, position: {col:col,row:row}, image: "latios.png", player: player_num}

createPrincess :: Int -> Int -> PlayerNum -> Maybe Piece
createPrincess col row player_num = Just {kind: Princess, position: {col:col,row:row}, image: "latias.png", player: player_num}

-- Returns a GameState representinng the initial state of the game.
-- The initial board is constructed here, as well as the initial
-- values of the other properties.
initialState :: Effect GameState
initialState = do
  let
    -- Replace these to change the initial board
    nothing_row = replicate columns Nothing
    init_board = [getBackRow 0 Two] <> [getPawnRow 1 Two 0] <> replicate (rows-4) nothing_row <> [getPawnRow (rows-2) One 0] <> [getBackRow (rows-1) One]
    
    getBackRow :: Int -> PlayerNum -> Array (Maybe Piece)
    getBackRow row player_num = [ createRook 0 row player_num, 
                                  Nothing,
                                  createBishop 2 row player_num, 
                                  createPrince 3 row player_num,
                                  createPrincess 4 row player_num,
                                  createBishop 5 row player_num, 
                                  Nothing,
                                  createRook 7 row player_num
                                ]

    getPawnRow :: Int -> PlayerNum -> Int -> Array (Maybe Piece)
    getPawnRow row player_num col | col == columns = []
                                  | otherwise = [createPawn col row player_num] <> getPawnRow row player_num (col+1)

  pure { tickCount: 0
  , lastReceivedMessage: Nothing
  , board: init_board
  , currentPlayer: One
  , clickedCell: {col: -1, row: -1}
  , possibleMoves: Nil
  , activePiece: Nothing
  , playerOneCaptures : Nil
  , playerTwoCaptures : Nil
  }


-- Access a specific row of the board
-- 0 indexed, 1st row is getBoardRow 0 board
-- Returns an Array (Maybe Pieces) which represents the
-- columns of the row. Returns an empty array if out of bounds
getBoardRow :: Int -> Board -> Array (Maybe Piece)
getBoardRow row board = case board !! row of
  Nothing -> []
  Just current_row -> current_row
  
-- Called every tick to update GameState if a change is detected
-- Returns an updated Effect Gamestate
onTick :: (String -> Effect Unit) -> GameState -> Effect GameState
onTick send gameState = do
  let
    clicked_col = gameState.clickedCell.col
    clicked_row = gameState.clickedCell.row

    clicked_piece = accessCell clicked_col clicked_row gameState.board

    -- Assigns state active piece to clicked piece
    updateActivePiece :: Maybe Piece -> GameState -> GameState
    updateActivePiece maybe_piece state = case maybe_piece of
      Nothing -> state { activePiece = Nothing }
      Just piece -> if piece.player == state.currentPlayer then state { activePiece = Just piece } else state { activePiece = Nothing }
    
    updateTickCount :: GameState -> GameState
    updateTickCount state = state { tickCount = gameState.tickCount + 1 }

    -- get possible moves for piece kind
    updatePossibleMoves :: Maybe Piece -> GameState -> GameState
    updatePossibleMoves maybe_piece state = case maybe_piece of
      Nothing -> state { possibleMoves = Nil }
      Just piece | piece.player /= gameState.currentPlayer -> state { possibleMoves = Nil }
                 | otherwise -> state { possibleMoves = getPossibleMoves piece.kind gameState.board piece.position piece.player }
    
    -- Update the board if a valid move is made (clicked cell is a possible move)
    makeMove :: GameState -> GameState
    makeMove state = if valid_move == true
      then case state.activePiece of
        Nothing -> state
        Just activePiece -> if state.currentPlayer == One
          then state { board = movePiece state.board activePiece.position state.clickedCell, currentPlayer = next_player, playerOneCaptures = concat (captured_piece : state.playerOneCaptures : Nil) }
          else state { board = movePiece state.board activePiece.position state.clickedCell, currentPlayer = next_player, playerTwoCaptures = concat (captured_piece : state.playerTwoCaptures : Nil) }
          where next_player = if state.currentPlayer == One then Two else One
      else state
      where
        valid_move = elem state.clickedCell state.possibleMoves
        new_piece = if valid_move == true 
          then case state.activePiece of
            Nothing -> Nothing
            Just piece -> Just (piece { position = state.clickedCell })
          else state.activePiece
        
        captured_piece = if valid_move == true
          then case accessCell state.clickedCell.col state.clickedCell.row state.board of
            Nothing -> Nil
            Just piece -> piece : Nil
          else Nil

        -- Remove the piece from its original position
        removePiece :: Array (Maybe Piece) -> Array (Maybe Piece)
        removePiece row = map checker row
          where
            checker :: Maybe Piece -> Maybe Piece
            checker to_compare = if state.activePiece == to_compare then Nothing else to_compare
        
        -- Move piece to the destination
        addPiece :: Array (Maybe Piece) -> Int -> Array (Maybe Piece)
        addPiece row col_num = helper 0
          where
            helper :: Int -> Array (Maybe Piece)
            helper current_col
              | current_col == columns = []
              | current_col == col_num = [new_piece] <> helper (current_col + 1)
              | otherwise = case row !! current_col of
                Nothing -> [Nothing] <> helper (current_col + 1)
                Just piece -> [piece] <> helper (current_col + 1)

        -- Used as a helper function to construct the whole board
        -- using the add and remove piece functions
        movePiece :: Board -> Position -> Position -> Board
        movePiece board piece_position target_position = helper 0
          where
            helper :: Int -> Board
            helper current_row
              | current_row == rows = []
              | current_row == target_position.row && current_row == piece_position.row 
                = [removePiece (addPiece (getBoardRow current_row board) target_position.col) ] <> helper (current_row + 1)
              | current_row == target_position.row = [addPiece (getBoardRow current_row board) target_position.col ] <> helper (current_row + 1)
              | current_row == piece_position.row = [removePiece (getBoardRow current_row board) ] <> helper (current_row + 1)
              | otherwise = [getBoardRow current_row board] <> helper (current_row + 1)
    
    updateCapturedPiece :: Maybe Piece -> GameState -> GameState
    updateCapturedPiece Nothing state = state { activePiece = Nothing }
    updateCapturedPiece (Just piece) state | state.currentPlayer == One = 
      if (elem piece state.playerOneCaptures) 
        then state { activePiece = Just piece } 
        else state
    updateCapturedPiece (Just piece) state | otherwise = 
       if (elem piece state.playerTwoCaptures) 
        then state { activePiece = Just piece } 
        else state

    showPieceKind :: Maybe Piece -> String
    showPieceKind Nothing = "Nothing"
    showPieceKind (Just piece) = show piece.kind


  if gameState.tickCount `mod` fps == 0 then do
    send $ "Current Piece: " <> showPieceKind clicked_piece <> "\n" --<> 
      --show gameState.currentPlayer <> "\n" <> 
      -- showBoard gameState.board --<> "\n" 
    else pure unit

  pure $ gameState
    # makeMove
    # updateActivePiece clicked_piece
    # updatePossibleMoves clicked_piece
    # updateTickCount
    -- # updateCapturedPiece clicked_piece



onMouseDown :: (String -> Effect Unit) -> { x :: Int, y :: Int } -> GameState -> Effect GameState
onMouseDown send { x, y } gameState = do
  let
    -- Get the column and row of the clicked cell given its coordinates
    -- Formula is coordinate - offset - cell_width to translate the point
    -- where x = 0 and y = 0 is row 0 col 0 (0 indexed board)
    cell_col = floor $ (toNumber x - canvas_offset_x-cell_width) / cell_width
    cell_row = floor $ (toNumber y - canvas_offset_y-cell_height) / cell_height

  send $ "Clicked Cell: " <> show cell_col <> "," <> show cell_row
  pure gameState {clickedCell = {col: cell_col, row: cell_row}}

-- Not sure if we will be using this? Didn't remove it first
-- since I just buit on the demo
onKeyDown :: (String -> Effect Unit) -> String -> GameState -> Effect GameState
onKeyDown send key gameState = do
  send $ "I pressed " <> key
  pure gameState

-- Not sure if we will be using this? Didn't remove it first
-- since I just buit on the demo
onKeyUp :: (String -> Effect Unit) -> String -> GameState -> Effect GameState
onKeyUp _ _ gameState = pure gameState

-- Haven't used this yet, please update this comment when utilized
onMessage :: (String -> Effect Unit) -> Message -> GameState -> Effect GameState
onMessage _ message gameState = do
  log $ "Received message: " <> show message
  pure $ gameState { lastReceivedMessage = Just message }

-- Draws the game on the screen using information from the GameState
onRender :: Map.Map String Canvas.CanvasImageSource -> Canvas.Context2D -> GameState -> Effect Unit
onRender images ctx gameState = do
  clearCanvas ctx { color: "black", width, height }

  let
    -- Sets the printed texts color, font, and size
    color = "black"
    font = "arial"
    size = 18

    -- Draws the board using board from GameState
    -- Iterates through all column-row pairs
    -- Takes in 0-indexed input
    drawBoard :: Int -> Int -> Effect Unit
    drawBoard col row 
      | row >= rows = pure unit  -- Base case, return pure unit once everything is printed
      | col >= columns = drawBoard 0 (row+1) -- Once whole row is printed, print next row
      | otherwise = do 
          let
            temp_x = (cell_width+1.0) * (toNumber (col+1))  -- cell_width + 1.0 for cell border, col+1 to account for board border
            temp_y = (cell_height+1.0) * (toNumber (row+1)) -- same formula as temp_x, except for y
          -- Draw cell background
          -- Can swap this to draw image if desired
          drawRect ctx { x: temp_x, y:temp_y, color: "white", width: cell_width, height: cell_height}
          -- Print the piece to the board if present, else go to next cell
          case accessCell col row gameState.board of
            Nothing -> drawBoard (col+1) row
            Just piece -> case Map.lookup piece.image images of
              Nothing -> drawBoard (col+1) row
              Just img -> do
                drawImageScaled ctx img { x: temp_x, y: temp_y, width: cell_width, height: cell_height }
                drawBoard (col+1) row

    -- Draws the indicators for the possible moves on the board
    drawMoves :: List(Position) -> Effect Unit
    drawMoves Nil = pure unit
    drawMoves (Cons { col, row } tail) = do
      drawCircle ctx { x: board_start_x + (cell_width+1.0) * (toNumber col) + cell_width/2.0
        , y:  board_start_y + (cell_height+1.0) * (toNumber row) + cell_width/2.0
        , radius: cell_width/4.0, color: "cornflowerblue" }
      drawMoves tail
    
    -- Draws the captured pieces on the border of the board
    drawCaptured :: List Piece -> List Piece -> Effect Unit
    drawCaptured playerOneCaptures playerTwoCaptures = do
      let
        -- Given a list of captured pieces, it counts the number of pieces
        -- per kind captured and returns as a List Captured.
        countKinds :: List Piece -> List Captured -> List Captured
        countKinds Nil captured_list = captured_list
        countKinds (Cons piece piece_tail) captured_list = countKinds piece_tail updateCaptured
          where
            -- Checker function for if a piece of that kind
            -- is already in the list of captured pieces
            hasBeenCaptured :: List Captured -> Boolean
            hasBeenCaptured Nil = false
            hasBeenCaptured (Cons captured captured_tail) = if captured.kind == piece.kind then true else hasBeenCaptured captured_tail

            -- Updates the list of captured pieces by adding it to the list if
            -- that kind has not been captured yet, or incrementing the counter
            -- for a piece that has already been captured
            updateCaptured :: List Captured
            updateCaptured = if in_captured == true
              then map updateHelper captured_list
              else { kind: piece.kind, count: 1, image: piece.image } : captured_list
              where
                in_captured = hasBeenCaptured captured_list

                updateHelper :: Captured -> Captured
                updateHelper captured = if piece.kind == captured.kind
                  then captured { count = captured.count + 1 }
                  else captured


        player_one_kinds = countKinds playerOneCaptures Nil
        player_two_kinds = countKinds playerTwoCaptures Nil

        
        player_one_y_offset = (cell_height+1.0) * (1.0 + toNumber rows)

        -- Takes a list of captured pieces and draw them on the board
        -- with their respective counts using the given y offset
        -- that depends on the current player's captures being drawn
        drawKinds :: List Captured -> Number -> Number -> Effect Unit
        drawKinds Nil _ _ = pure unit
        drawKinds (Cons captured tail) y_offset count = do
          -- Values for the counter can still be updated to fit better
          -- Should be updated if height, width, rows, or columns is changed
          case Map.lookup captured.image images of
            Nothing -> pure unit
            Just img -> drawImageScaled ctx img { x: (cell_width+1.0) * count, y: y_offset, width: cell_width, height: cell_height }
          drawRect ctx { x: (cell_width+1.0) * count + cell_width/2.0 - cell_width/8.0, y: y_offset + cell_height/1.25, color: "white", width: cell_width/4.0, height: cell_height/4.0}
          drawText ctx { x: (cell_width+1.0) * count + cell_width/2.0, y: y_offset + cell_height/1.25 + 15.0, color, font, size, text: show captured.count }
          drawKinds tail y_offset (count+1.0)
      
      drawKinds player_one_kinds player_one_y_offset 0.0
      drawKinds player_two_kinds 0.0 0.0
      pure unit


  drawBoard 0 0
  drawMoves gameState.possibleMoves
  drawCaptured gameState.playerOneCaptures gameState.playerTwoCaptures

  -- This can be used to check messages received or to print something
  -- on the screen for debugging purposes
  -- case gameState.lastReceivedMessage of
  --   Nothing -> drawText ctx { x, y: 50.0, color, font, size, text: "Player One Captures: " <> show gameState.playerOneCaptures }
  --   Just message -> drawText ctx { x, y: 10.0, color, font, size, text: "Last received message: " <> message.payload }

main :: Effect Unit
main =
  startNetworkGame
    { initialState
    , onTick
    , onMouseDown
    , onKeyDown
    , onKeyUp
    , onRender
    , onMessage
    , fps
    , width
    , height
    , ipAddress: "localhost"
    , port: 15000
    , imagePaths: images
    }