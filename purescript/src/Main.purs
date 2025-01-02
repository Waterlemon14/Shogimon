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
import Data.List (List(..), index, null, concat, (:))
import Data.Array (replicate, (!!))
import Data.Foldable (elem)
import Effect (Effect)
import Effect.Console (log)
import Graphics.Canvas as Canvas

import Movements
  ( getPossibleMoves
  , accessCell
  , protectedPieceMovementCells
  )

import ProjectTypes
  ( Kind(..)
  , Position
  , Board
  , PlayerNum(..)
  , Piece
  , Captured
  , GameState
  , Winner(..)
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
createBishop col row One    = Just {kind: Bishop,   position: {col:col,row:row},  image: "../../img/pikachu.png", player: One, isProtected: false}
createBishop col row Two    = Just {kind: Bishop,   position: {col:col,row:row},  image: "../../img/pikachu-shiny.png", player: Two, isProtected: false}

createPawn :: Int -> Int -> PlayerNum -> Maybe Piece
createPawn col row One      = Just {kind: Pawn,     position: {col:col,row:row},  image: "../../img/eevee.png", player: One, isProtected: false}
createPawn col row Two      = Just {kind: Pawn,     position: {col:col,row:row},  image: "../../img/eevee-shiny.png", player: Two, isProtected: false}

createRook :: Int -> Int -> PlayerNum -> Maybe Piece
createRook col row One      = Just {kind: Rook,     position: {col:col,row:row},  image: "../../img/turtwig.png", player: One, isProtected: false}
createRook col row Two      = Just {kind: Rook,     position: {col:col,row:row},  image: "../../img/turtwig-shiny.png", player: Two, isProtected: false}

createPrince :: Int -> Int -> PlayerNum -> Maybe Piece
createPrince col row One    = Just {kind: Prince,   position: {col:col,row:row},  image: "../../img/latios.png", player: One, isProtected: true}
createPrince col row Two    = Just {kind: Prince,   position: {col:col,row:row},  image: "../../img/latios-shiny.png", player: Two, isProtected: true}

createPrincess :: Int -> Int -> PlayerNum -> Maybe Piece
createPrincess col row One  = Just {kind: Princess, position: {col:col,row:row},  image: "../../img/latias.png", player: One, isProtected: true}
createPrincess col row Two  = Just {kind: Princess, position: {col:col,row:row},  image: "../../img/latias-shiny.png", player: Two, isProtected: true}

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
                                  createBishop 1 row player_num, 
                                  Nothing,
                                  createPrince 3 row player_num,
                                  createPrincess 4 row player_num,
                                  Nothing,
                                  createBishop 6 row player_num, 
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
  , winner : Nothing
  , moveCount : 3
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

    pieceConstructor :: Captured -> Maybe Piece
    pieceConstructor cp 
      | cp.kind == Bishop = createBishop  (-1) (-1) gameState.currentPlayer 
      | cp.kind == Pawn   = createPawn    (-1) (-1) gameState.currentPlayer 
      | otherwise         = createRook    (-1) (-1) gameState.currentPlayer 

    -- Finds currently clicked piece
    pieceFinder :: Int -> Int -> PlayerNum -> Maybe Piece
    pieceFinder col row player
      | row == 8    && player == One = (flip bind) pieceConstructor (index gameState.playerOneCaptures (col+1))
      | row == (-1) && player == Two = (flip bind) pieceConstructor (index gameState.playerTwoCaptures (col+1))
      | otherwise                    = case accessCell col row gameState.board of 
                                        Nothing -> Nothing
                                        Just piece -> if piece.player == player
                                          then Just piece
                                          else Nothing

    clicked_piece = pieceFinder clicked_col clicked_row gameState.currentPlayer

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
      Just piece -> state { possibleMoves = getPossibleMoves piece.kind gameState.board piece.position piece.player piece.isProtected (piece.position.col == (-1) && piece.position.row == (-1))}
    
    -- Update the board if a valid move is made (clicked cell is a possible move)
    makeMove :: GameState -> GameState
    makeMove state = if valid_move == true
      then case state.activePiece of
        Nothing -> state
        Just activePiece -> if state.currentPlayer == One
          then state { board = movePiece state.board activePiece.position state.clickedCell, currentPlayer = next_player, playerOneCaptures = capturedPieces state.playerOneCaptures activePiece, moveCount = checker }
          else state { board = movePiece state.board activePiece.position state.clickedCell, currentPlayer = next_player, playerTwoCaptures = capturedPieces state.playerTwoCaptures activePiece, moveCount = checker }
          where 
            next_player = if state.moveCount == 1 
              then if state.currentPlayer == One then Two else One
              else state.currentPlayer

            checker = if state.moveCount == 1 
              then 3
              else state.moveCount - 1


      else state
      where
        valid_move = elem state.clickedCell state.possibleMoves
        new_piece = if valid_move == true 
          then case state.activePiece of
            Nothing -> Nothing
            Just piece -> Just (piece { position = state.clickedCell })
          else state.activePiece

        capturedPieces :: List Captured -> Piece -> List Captured
        capturedPieces captured activePiece 
          -- remove the placed piece from the list
          | activePiece.position.row == -1 && activePiece.position.col == -1 = decrCount captured activePiece
          -- adds the captured piece into the list if it exists
          | otherwise = case accessCell state.clickedCell.col state.clickedCell.row state.board of
            Nothing -> captured
            Just piece -> addCaptured captured piece

        decrCount :: List Captured -> Piece -> List Captured
        decrCount Nil _ = Nil
        decrCount (Cons h t) p 
          | h.kind == p.kind = if h.count == 1 then t else (Cons (h { count = h.count - 1 }) t)
          | otherwise = Cons h (decrCount t p)

        
        addCaptured :: List Captured -> Piece -> List Captured
        addCaptured Nil piece = Cons { kind: piece.kind, count: 1, image: piece.image } Nil
        addCaptured (Cons h t) piece | h.kind == piece.kind = Cons (h {count = h.count + 1}) t
        addCaptured (Cons h t) piece | otherwise = Cons h (addCaptured t piece)

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


    updateGameOver :: GameState -> GameState
    updateGameOver state = if null (protectedPieceMovementCells 0 0 state.board One) 
      then if null (protectedPieceMovementCells 0 0 state.board Two)
        then state { winner = Just Draw }
        else state { winner = Just Player2 } 
      else if null (protectedPieceMovementCells 0 0 state.board Two) 
        then state { winner = Just Player1 } 
        else state

    -- mapper :: List Position -> String
    -- mapper Nil str = str
    -- mapper (Cons h t) str =  mapper t (str <> show h)

  -- if gameState.tickCount `mod` fps == 0 then do
  --   send $ show (concat $ (protectedPieceMovementCells 0 0 gameState.board One) : (protectedPieceMovementCells 0 0 gameState.board Two) : Nil) <> "\n" --<>
  --     --show gameState.currentPlayer <> "\n" <> 
  --     -- showBoard gameState.board --<> "\n" 
  --   else pure unit

  case gameState.winner of 
    Nothing -> 
      pure $ gameState
        # makeMove
        # updateActivePiece clicked_piece
        # updatePossibleMoves clicked_piece
        # updateTickCount
        # updateGameOver
    Just _ ->
      pure gameState

onMouseDown :: (String -> Effect Unit) -> { x :: Int, y :: Int } -> GameState -> Effect GameState
onMouseDown send { x, y } gameState = do
  let
    -- Get the column and row of the clicked cell given its coordinates
    -- Formula is coordinate - offset - cell_width to translate the point
    -- where x = 0 and y = 0 is row 0 col 0 (0 indexed board)
    cell_col = floor $ (toNumber x - canvas_offset_x-cell_width) / cell_width
    cell_row = floor $ (toNumber y - canvas_offset_y-cell_height) / cell_height

  -- send $ "Clicked Cell: col " <> show cell_col <> ", row " <> show cell_row
  pure gameState {clickedCell = {col: cell_col, row: cell_row}}

-- Not sure if we will be using this? Didn't remove it first
-- since I just buit on the demo
onKeyDown :: (String -> Effect Unit) -> String -> GameState -> Effect GameState
onKeyDown send key gameState = do
  send $ "I pressed " <> key <> show gameState.playerOneCaptures
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
    messageX = width / 2.0
    messageY = width / 2.0

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
    drawCaptured :: List Captured -> List Captured -> Effect Unit
    drawCaptured playerOneCaptures playerTwoCaptures = do
      let
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
      
      drawKinds playerOneCaptures player_one_y_offset 0.0
      drawKinds playerTwoCaptures 0.0 0.0
      pure unit


  drawBoard 0 0
  drawMoves gameState.possibleMoves
  drawCaptured gameState.playerOneCaptures gameState.playerTwoCaptures

  case gameState.winner of 
    Nothing -> pure unit
    Just winner -> drawText ctx { x: messageX, y: messageY, color: color, font: font, size: size, text: "Game Verdict: " <> show winner }

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