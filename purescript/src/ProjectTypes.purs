module ProjectTypes
  ( Kind(..)
  , Position
  , Board
  , PlayerNum(..)
  , Piece
  , Captured
  , GameState
  )
  where

import Prelude

import Data.List (List(..), (:), concat)
import Data.Maybe (Maybe(..))

import CS150241Project.Networking (Message)


-- New type for the kind of piece, will be stored in a Piece record
-- To add a kind, add to the tagged union and Show instance
data Kind
  = Pawn
  | Bishop

instance Show Kind where
  show Pawn   = "Pawn"
  show Bishop = "Bishop"

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
