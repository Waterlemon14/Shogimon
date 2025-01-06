module ProjectTypes
  ( Board
  , Captured
  , GameState
  , Kind(..)
  , Piece
  , PlayerNum(..)
  , Position
  , Winner(..)
  )
  where

import Prelude

import Data.List (List)
import Data.Maybe (Maybe)

import CS150241Project.Networking (Message)


-- New type for the kind of piece, will be stored in a Piece record
-- To add a kind, add to the tagged union and Show instance
data Kind
  = Eevee
  | Pikachu
  | Turtwig
  | Latios
  | Latias

instance Show Kind where
  show Eevee    = "Eevee"      -- p
  show Pikachu  = "Pikachu"    -- b
  show Turtwig  = "Turtwig"      -- r
  show Latios   = "Latios"    -- k
  show Latias   = "Latias"  -- q

derive instance Eq Kind

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
  , position :: Position    -- Current position of the piece, {-1,-1} refers to a captured piece
  , player :: PlayerNum     -- Which player the piece belongs to
  , isProtected :: Boolean    -- If the piece is to be protected
  }


-- Used to represent captured pieces. Instead of placing each capture piece
-- individually, counters are used to keep track of the number of captured pieces
type Captured =
  { kind :: Kind      -- Kind of the piece
  , count :: Int      -- How many of that kind of piece is captured
  }


-- Used to more accurately represent gameover state
data Winner = Player1 | Player2 | Draw

instance Show Winner where
  show Player1 = "Player 1"
  show Player2 = "Player 2"
  show Draw = "Draw"

derive instance Eq Winner

-- Used to represent the current game state, keeps all relevant information
-- to the game state.
type GameState =
  { tickCount :: Int
  , lastReceivedMessage :: Maybe Message
  , board :: Board                       -- Represents the current board
  , currentPlayer :: PlayerNum           -- Represents whose turn it is
  , clickedCell :: Position              -- Position of the last clicked cell
  , possibleMoves :: List Position       -- List of possible moves (position) that the active piece can take
  , activePiece :: Maybe Piece           -- Currently clicked piece to be moved
  , playerOneCaptures :: List Captured   -- List of pieces captured by player one
  , playerTwoCaptures :: List Captured   -- List of pieces captured by player two
  , winner :: Maybe Winner               -- Stores the winner of the current game
  , moveCount :: Int                     -- Available number of moves remaining in the turn
  , columns :: Int                       -- Number of columns of the board
  , rows :: Int                          -- Number of rows of the board
  , gameStart :: Boolean                 -- Used to check if both players have connected
  , initialized :: Boolean               -- Used to check if board has been initialized based on player 1
  , myPlayerNum :: PlayerNum             -- Represents your player number
  }
