module Main
  ( Board
  , GameState
  , Kind(..)
  , Piece
  , PlayerNum(..)
  , Position
  , class Movement
  , columns
  , fps
  , getPossibleMoves
  , height
  , initialState
  , main
  , onKeyDown
  , onKeyUp
  , onMessage
  , onMouseDown
  , onRender
  , onTick
  , rows
  , width
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
import Data.Array (replicate, index, (!!))
import Data.Foldable (elem)
import Effect (Effect)
import Effect.Console (log)
import Graphics.Canvas as Canvas

-- aspect ratio should be cols+2 : rows+2 for square cells
-- Width of canvas
width :: Number
width = 490.0

-- Height of canvas
height :: Number
height = 700.0

-- Represents number of rows in the board
-- Not 0 indexed, row 1 is (Board !! 0)
rows :: Int
rows = 8

-- Represents number of columns in the board
-- Not 0 indexed, col 1 of row 1 is ((Board !! 0) !! 0)
columns :: Int
columns = 5

-- width-(1.0 + toNumber (columns+2))
-- where 1.0 is space between cells that serve as the border
-- and columns+2 for the outer cell border
cell_width :: Number
cell_width = (width-(1.0 + toNumber (columns+2))) / (toNumber (columns+2))

-- same formula as width
cell_height :: Number
cell_height = (height-(1.0+toNumber (rows+2))) / (toNumber (rows+2))

-- offset to get x value of the first column
board_start_x :: Number
board_start_x = cell_width

-- offset to get y value of the first column
board_start_y :: Number
board_start_y = cell_height

-- offset from the left of the screen, might be different on different devices
canvas_offset_x :: Number
canvas_offset_x = 8.0

-- offset from the top of the screen, might be different on different devices
canvas_offset_y :: Number
canvas_offset_y = 8.0

fps :: Int
fps = 60

-- New type for the kind of piece, will be stored in a Piece record
-- To add a kind, add to the tagged union and Show instance
data Kind
  = Pawn
  | Bishop

instance Show Kind where
  show Pawn   = "Pawn"
  show Bishop = "Bishop"

derive instance Eq Kind

-- Typeclass to get the possible moves of a piece kind
-- Whenever adding a piece kind, add to the instantiation below
class Movement a where
  -- getPossibleMoves should return a list of all possible moves that can be taken
  -- by the piece in its current position given the Board, Position, and PlayerNum.
  -- Given its position, check the board if the move is valid. When checking its
  -- moves against another piece, check the PlayerNum of that piece vs. the given
  -- PlayerNum to determine whether it is a valid move to capture it or not.
  getPossibleMoves :: a -> Board -> Position -> PlayerNum -> List Position

-- Define getPossibleMoves of the new kind added here
instance Movement Kind where
  getPossibleMoves Pawn _ position player
    | player == One = if position.row == 0 then Nil else {col: position.col, row: position.row - 1} : Nil
    | otherwise     = if position.row == rows-1 then Nil else {col: position.col,row: position.row + 1} : Nil
    
  getPossibleMoves Bishop board position player = bishopHelper
    where
      bishopHelper :: List Position
      bishopHelper = concat $ getUpperLeftMoves {col: position.col-1, row: position.row-1}
        : getLowerLeftMoves {col: position.col-1, row: position.row+1}
        : getUpperRightMoves {col: position.col+1, row: position.row-1}
        : getLowerRightMoves {col: position.col+1, row: position.row+1}
        : Nil
        where
          getUpperLeftMoves :: Position -> List Position
          getUpperLeftMoves current_position
            | current_position.row < 0 || current_position.col < 0 = Nil
            | otherwise = case accessBoard current_position.col current_position.row board of
              Nothing -> current_position : getUpperLeftMoves {col: current_position.col-1, row: current_position.row-1}
              Just piece -> if piece.player /= player then current_position : Nil else Nil
          getLowerLeftMoves :: Position -> List Position
          getLowerLeftMoves current_position
            | current_position.row >= rows || current_position.col < 0 = Nil
            | otherwise = case accessBoard current_position.col current_position.row board of
              Nothing -> current_position : getLowerLeftMoves {col: current_position.col-1, row: current_position.row+1}
              Just piece -> if piece.player /= player then current_position : Nil else Nil
          getUpperRightMoves :: Position -> List Position
          getUpperRightMoves current_position
            | current_position.row < 0 || current_position.col >= columns = Nil
            | otherwise = case accessBoard current_position.col current_position.row board of
              Nothing -> current_position : getUpperRightMoves {col: current_position.col+1, row: current_position.row-1}
              Just piece -> if piece.player /= player then current_position : Nil else Nil
          getLowerRightMoves :: Position -> List Position
          getLowerRightMoves current_position
            | current_position.row >= rows || current_position.col >= columns = Nil
            | otherwise = case accessBoard current_position.col current_position.row board of
              Nothing -> current_position : getLowerRightMoves {col: current_position.col+1, row: current_position.row+1}
              Just piece -> if piece.player /= player then current_position : Nil else Nil

-- Used to represent the position of a piece on the board
type Position =
  { col :: Int
  , row :: Int
  }

-- Used to represent the board as a 2D array.
-- Board is 0 indexed (last row is rows-1)
type Board = Array (Array (Maybe Piece))

-- Used to more accurately represent Players
data PlayerNum = One | Two

instance Show PlayerNum where
  show One = "One"
  show Two = "Two"

derive instance Eq PlayerNum

-- Used to represent a piece and store relevant information to the piece
type Piece =
  { kind :: Kind            -- Kind of the piece
  , position :: Position    -- Current position of the piece
  , image :: String         -- Filename of the image used to draw the piece
  , player :: PlayerNum     -- Which player the piece belongs to
  }

-- Used to represent captured pieces. Instead of placing each capture piece
-- individually, counters are used to keep track of the number of captured pieces
type Captured =
  { kind :: Kind      -- Kind of the piece
  , count :: Int      -- How many of that kind of piece is captured
  , image :: String   -- Filename of the image used to draw the piece
  }

-- Used to represent the current game state, keeps all relevant information
-- to the game state.
type GameState =
  { tickCount :: Int
  , lastReceivedMessage :: Maybe Message
  , board :: Board
  , currentPlayer :: PlayerNum        -- Represents whose turn it is
  , clickedCell :: Position           -- Position of the last clicked cell
  , possibleMoves :: List Position    -- List of possible moves (position) that the active piece can take
  , activePiece :: Maybe Piece        -- Currently clicked piece to be moved
  , playerOneCaptures :: List Piece   -- List of pieces captured by player one
  , playerTwoCaptures :: List Piece   -- List of pieces captured by player two
  }

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
    getBackRow row player_num = [Nothing, Just {kind: Bishop, position: {col:1,row:row}, image: "pikachu.png", player: player_num}, Nothing,
                                  Just {kind: Bishop, position: {col:3,row:row}, image: "pikachu.png", player: player_num}, Nothing]
    getPawnRow :: Int -> PlayerNum -> Int -> Array (Maybe Piece)
    getPawnRow row player_num col | col == columns = []
                                  | otherwise = [Just {kind: Pawn, position: {col:col,row:row}, image: "eevee.png", player: player_num}] <> getPawnRow row player_num (col+1)

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

-- Access a specific column and row of the board
-- 0 indexed, 1st row 1st col is accessBoard 0 0 board
-- Returns a Maybe Piece, with Nothing if cell is not occupied
-- and Just Piece if a piece is present
accessBoard :: Int -> Int -> Board -> Maybe Piece
accessBoard col row board = case cell of
    Nothing -> Nothing
    Just maybe_piece -> maybe_piece
  where
    cell =
      board
      # (flip index) row
      >>= (flip index) col

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
onTick _ gameState = do
  let
    clicked_col = gameState.clickedCell.col
    clicked_row = gameState.clickedCell.row

    clicked_piece = accessBoard clicked_col clicked_row gameState.board

    updateActivePiece :: Maybe Piece -> GameState -> GameState
    updateActivePiece maybe_piece state = case maybe_piece of
      Nothing -> state { activePiece = Nothing }
      Just piece -> if piece.player == state.currentPlayer then state { activePiece = Just piece } else state { activePiece = Nothing }
    
    updateTickCount :: GameState -> GameState
    updateTickCount state = state { tickCount = gameState.tickCount + 1 }

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
          then case accessBoard state.clickedCell.col state.clickedCell.row state.board of
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
    
  pure $ gameState
    # makeMove
    # updateActivePiece clicked_piece
    # updatePossibleMoves clicked_piece
    # updateTickCount

onMouseDown :: (String -> Effect Unit) -> { x :: Int, y :: Int } -> GameState -> Effect GameState
onMouseDown send { x, y } gameState = do
  let
    -- Get the column and row of the clicked cell given its coordinates
    -- Formula is coordinate - offset - cell_width to translate the point
    -- where x = 0 and y = 0 is row 0 col 0 (0 indexed board)
    cell_col = floor $ (toNumber x - canvas_offset_x-cell_width) / cell_width
    cell_row = floor $ (toNumber y - canvas_offset_y-cell_height) / cell_height

  send $ show cell_col <> "," <> show cell_row
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
          case accessBoard col row gameState.board of
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
    , imagePaths: [ "eevee.png", "pikachu.png" ]
    }