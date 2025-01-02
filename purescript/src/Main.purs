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
import Data.Int (toNumber, floor, fromString)
import Data.String (Pattern(..), split, take, drop, trim)
import Data.Map as Map
import Data.Maybe (Maybe(..), isNothing)
import Data.List (List(..), index, null, foldl) -- , (:), concat, length, snoc)
import Data.Array (replicate, (!!), length, drop, dropEnd) as Array
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
    nothing_row = Array.replicate columns Nothing
    init_board = [getBackRow 0 Two] <> [getPawnRow 1 Two 0] <> Array.replicate (rows-4) nothing_row <> [getPawnRow (rows-2) One 0] <> [getBackRow (rows-1) One]
    
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
  , rows : rows
  , columns : columns
  , gameStart: false
  , initialized: false
  , myPlayerNum: One
  }


-- Access a specific row of the board
-- 0 indexed, 1st row is getBoardRow 0 board
-- Returns an Array (Maybe Pieces) which represents the
-- columns of the row. Returns an empty array if out of bounds
getBoardRow :: Int -> Board -> Array (Maybe Piece)
getBoardRow row board = case board Array.!! row of
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

    valid_move = elem gameState.clickedCell gameState.possibleMoves

    -- Assigns state active piece to clicked piece
    updateActivePiece :: GameState -> GameState
    updateActivePiece state = case pieceFinder state.clickedCell.col state.clickedCell.row state.currentPlayer of
      Nothing -> state { activePiece = Nothing }
      Just piece -> if piece.player == state.currentPlayer 
      then state { activePiece = Just piece } else state { activePiece = Nothing }
    
    updateTickCount :: GameState -> GameState
    updateTickCount state = state { tickCount = gameState.tickCount + 1 }

    -- get possible moves for piece kind
    updatePossibleMoves :: GameState -> GameState
    updatePossibleMoves state = case pieceFinder state.clickedCell.col state.clickedCell.row state.currentPlayer of
      Nothing -> state { possibleMoves = Nil }
      Just piece -> state { possibleMoves = getPossibleMoves piece.kind gameState.board piece.position piece.player piece.isProtected (piece.position.col == (-1) && piece.position.row == (-1)) }

    -- Update the board if a valid move is made (clicked cell is a possible move)
    makeMove :: GameState -> GameState
    makeMove state = if valid_move == true
      then case state.activePiece of
        Nothing -> state
        Just activePiece -> if state.currentPlayer == One
          then state { board = movePiece state.board activePiece.position state.clickedCell, currentPlayer = next_player, playerOneCaptures = capturedPieces state.playerOneCaptures activePiece, moveCount = checker, clickedCell = clicked_cell }
          else state { board = movePiece state.board activePiece.position state.clickedCell, currentPlayer = next_player, playerTwoCaptures = capturedPieces state.playerTwoCaptures activePiece, moveCount = checker, clickedCell = clicked_cell }
          where 
            next_player = if state.moveCount == 1 
              then if state.currentPlayer == One then Two else One
              else state.currentPlayer

            checker = if state.moveCount == 1 
              then 3
              else state.moveCount - 1
            
            clicked_cell = if next_player /= state.currentPlayer
              then { col: -2, row: -2 }
              else state.clickedCell
  

      else state
      where
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
              | otherwise = case row Array.!! current_col of
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
    
    getBoardMessage :: Int -> Int -> Board -> String
    getBoardMessage col row board
      | col >= columns = " " <> getBoardMessage 0 (row+1) board
      | row >= rows    = ""
      | otherwise = case accessCell col row board of
        Nothing -> "xx" <> getBoardMessage (col+1) row board
        Just piece -> case piece.kind of
          Pawn     -> "p" <> if piece.player == One then "1" <> getBoardMessage (col+1) row board else "2" <> getBoardMessage (col+1) row board
          Bishop   -> "b" <> if piece.player == One then "1" <> getBoardMessage (col+1) row board else "2" <> getBoardMessage (col+1) row board
          Rook     -> "r" <> if piece.player == One then "1" <> getBoardMessage (col+1) row board else "2" <> getBoardMessage (col+1) row board
          Prince   -> "k" <> if piece.player == One then "1" <> getBoardMessage (col+1) row board else "2" <> getBoardMessage (col+1) row board
          Princess -> "q" <> if piece.player == One then "1" <> getBoardMessage (col+1) row board else "2" <> getBoardMessage (col+1) row board
    
    getCapturedMessage :: List Captured -> String
    getCapturedMessage Nil = "None"
    getCapturedMessage captured_pieces = foldl helper "" captured_pieces
      where
        helper :: String -> Captured -> String
        helper acc captured_piece
          | captured_piece.kind == Pawn     = acc <> "p" <> show captured_piece.count
          | captured_piece.kind == Bishop   = acc <> "b" <> show captured_piece.count
          | captured_piece.kind == Rook     = acc <> "r" <> show captured_piece.count
          | captured_piece.kind == Prince   = acc <> "k" <> show captured_piece.count
          | captured_piece.kind == Princess = acc <> "q" <> show captured_piece.count
          | otherwise                       = acc <> "xx" -- should never reach this branch

    constructBoard :: Int -> Array String -> Board
    constructBoard row board = case board Array.!! row of
      Nothing -> []
      Just current_row -> [constructRow 0 current_row] <> constructBoard (row+1) board
        where
          constructRow :: Int -> String -> Array (Maybe Piece)
          constructRow col row_string
            | col >= columns || row_string == "" = []
            | otherwise = [new_piece] <> constructRow (col + 1) (drop 2 row_string)
              where
                piece = take 1 row_string
                player_num = case take 1 $ drop 1 row_string of
                  "1" -> One
                  _ -> Two    -- Assume valid piece always, check later if invalid

                new_piece = case piece of
                  "p" -> createPawn     col row player_num
                  "b" -> createBishop   col row player_num
                  "r" -> createRook     col row player_num
                  "k" -> createPrince   col row player_num
                  "q" -> createPrincess col row player_num
                  _   -> Nothing

    -- Used to send the current state of the game
    sendStateMessage :: GameState -> Effect GameState
    sendStateMessage state = do
      send $ (show state.currentPlayer) <> " " <> getCapturedMessage state.playerOneCaptures <> " " <> 
        getCapturedMessage state.playerTwoCaptures <> " " <> (trim $ getBoardMessage 0 0 state.board)
      pure state
    
    readCapturedMessage :: String -> PlayerNum -> List Captured
    readCapturedMessage captured_string player_num = if captured_string == "None"
      then Nil
      else helper captured_string
        where
          helper :: String -> List Captured
          helper remaining_captured = if count == 0
            then Nil
            else Cons { kind: kind, count: count, image: image } (helper (drop 2 remaining_captured))
              where
                kind = case take 1 remaining_captured of
                  "p" -> Pawn
                  "b" -> Bishop
                  "r" -> Rook
                  "k" -> Prince
                  "q" -> Princess
                  _   -> Pawn -- should never reach this case
                count = case fromString (take 1 (drop 1 remaining_captured)) of
                  Just num -> num
                  Nothing -> 0 -- should never reach this case
                image = case take 1 remaining_captured of
                  "p" -> "../../img/eevee.png"
                  "b" -> "../../img/pikachu.png"
                  "r" -> "../../img/turtwig.png"
                  "k" -> "../../img/latios.png"
                  "q" -> "../../img/latias.png"
                  _   -> "" -- should never reach this case
    
    readStateMessage :: GameState -> GameState
    readStateMessage state = do
      let
        payload_arr = case state.lastReceivedMessage of
          Nothing -> []
          Just message -> split (Pattern " ") $ message.payload

        current_player = case state.lastReceivedMessage of
          Nothing -> show state.currentPlayer
          Just message -> take 3 message.payload
        board = Array.drop 3 $ payload_arr
                      
        new_board = if Array.length board == state.rows
        then constructBoard 0 board
        else state.board

        player_one_captures = case payload_arr Array.!! 1 of
          Just captured_message -> if readCapturedMessage captured_message One == Nil
            then state.playerOneCaptures
            else readCapturedMessage captured_message One
          Nothing -> state.playerOneCaptures
        
        player_two_captures = case payload_arr Array.!! 2 of
          Just captured_message -> if readCapturedMessage captured_message Two == Nil
            then state.playerTwoCaptures
            else readCapturedMessage captured_message Two
          Nothing -> state.playerTwoCaptures
      
      state
        { board = new_board
        , currentPlayer = if current_player == "One" then One else if current_player == "Two" then Two else gameState.currentPlayer
        , playerOneCaptures = player_one_captures
        , playerTwoCaptures = player_two_captures
        }
    
    initializeGame :: GameState -> Effect GameState
    initializeGame state = do
      if state.initialized == false
      then send $ "init1 " <> show state.columns <> " " <> show state.rows <> " " <> getBoardMessage 0 0 state.board
      else send $ "init2 " <> show state.columns <> " " <> show state.rows <> " " <> getBoardMessage 0 0 state.board

      let
        player = case state.lastReceivedMessage of
          Nothing -> ""
          Just msg -> if show msg.playerId == "Player1" then "One" else if show msg.playerId == "Player2" then "Two" else ""
        message = case state.lastReceivedMessage of
          Nothing -> []
          Just msg -> if take 4 msg.payload == "init"
            then split (Pattern " ") $ drop 6 msg.payload
            else []
        my_player_num = case state.lastReceivedMessage of
          Nothing -> state.currentPlayer
          Just msg -> if take 1 (drop 4 msg.payload) == "1"
            then One
            else if take 1 (drop 4 msg.payload) == "2"
            then Two
            else state.currentPlayer

      if message /= []
      then if player == "One" && state.initialized == false
        then do
          let
            new_columns = case message Array.!! 0 of
              Nothing -> 0
              Just cols_string -> case fromString cols_string of
                Nothing -> 0
                Just cols -> cols
            new_rows = case message Array.!! 1 of
              Nothing -> 0
              Just rows_string -> case fromString rows_string of
                Nothing -> 0
                Just rows -> rows
            board_array = case Array.dropEnd 1 (Array.drop 2 message) of
              [] -> []
              arr -> arr

            new_board = if Array.length board_array == new_rows
              then constructBoard 0 board_array
              else []
          pure state { columns = new_columns, rows = new_rows, board = new_board, initialized = true, myPlayerNum = my_player_num }

        else if player == "Two"
        then pure state { gameStart = true }
        else pure state
      else pure state

    -- mapper :: List Position -> String
    -- mapper Nil str = str
    -- mapper (Cons h t) str =  mapper t (str <> show h)

  -- if gameState.tickCount `mod` fps == 0 then do
  --   send $ show (concat $ (protectedPieceMovementCells 0 0 gameState.board One) : (protectedPieceMovementCells 0 0 gameState.board Two) : Nil) <> "\n" --<>
  --     --show gameState.currentPlayer <> "\n" <> 
  --     -- showBoard gameState.board --<> "\n" 
  --   else pure unit

  case gameState.gameStart of
    false -> initializeGame gameState  
    true -> if gameState.myPlayerNum /= gameState.currentPlayer
      then pure $ readStateMessage gameState
      else case gameState.winner of 
        Nothing -> if valid_move == true
          then gameState
            # makeMove
            # updateActivePiece
            # updatePossibleMoves
            # updateTickCount
            # updateGameOver
            # sendStateMessage
          else pure $ gameState
            # makeMove
            # updateActivePiece
            # updatePossibleMoves
            # updateTickCount
            # updateGameOver
        Just _ ->
          pure $ gameState
      

onMouseDown :: (String -> Effect Unit) -> { x :: Int, y :: Int } -> GameState -> Effect GameState
onMouseDown send { x, y } gameState = do
  let
    -- Get the column and row of the clicked cell given its coordinates
    -- Formula is coordinate - offset - cell_width to translate the point
    -- where x = 0 and y = 0 is row 0 col 0 (0 indexed board)
    cell_col = floor $ (toNumber x - canvas_offset_x-cell_width) / cell_width
    cell_row = floor $ (toNumber y - canvas_offset_y-cell_height) / cell_height

  if gameState.gameStart == true && gameState.currentPlayer == gameState.myPlayerNum
  then do
    send $ "click " <> show cell_col <> " " <> show cell_row
    pure gameState
  else pure gameState

-- Not sure if we will be using this? Didn't remove it first
-- since I just buit on the demo
onKeyDown :: (String -> Effect Unit) -> String -> GameState -> Effect GameState
onKeyDown _ _ gameState = do
  -- send $ "I pressed " <> key
  pure gameState

-- Unused function
onKeyUp :: (String -> Effect Unit) -> String -> GameState -> Effect GameState
onKeyUp _ _ gameState = pure gameState

-- Used to update clicks depending on received messages
onMessage :: (String -> Effect Unit) -> Message -> GameState -> Effect GameState
onMessage _ message gameState = do
  let
    command = split (Pattern " ") message.payload
    clicked_cell = case command Array.!! 0 of
      Nothing -> { col: -2, row: -2 }
      Just action -> if action == "click"
        then do
          let
            cell_col = case command Array.!! 1 of
              Nothing -> -2
              Just col -> case fromString col of
                Nothing -> -2
                Just num -> num
            cell_row = case command Array.!! 2 of
              Nothing -> -2
              Just col -> case fromString col of
                Nothing -> -2
                Just num -> num
          { col: cell_col, row: cell_row }
        else { col: -2, row: -2 }
  
  log $ "Received Message: " <> show message
  
  case gameState.gameStart of
    false -> do
      if show message.playerId == "Player1"
      then pure $ gameState { lastReceivedMessage = Just message }
      else if show message.playerId == "Player2" && isNothing gameState.lastReceivedMessage /= true
      then  pure $ gameState { lastReceivedMessage = Just message }
      else pure $ gameState
    true -> if gameState.myPlayerNum == gameState.currentPlayer && ( (show message.playerId == "Player1" && gameState.currentPlayer == One) || (show message.playerId == "Player2" && gameState.currentPlayer == Two) )
      then do pure $ gameState { lastReceivedMessage = Just message, clickedCell = clicked_cell }
      else do
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