module Movements
  ( class Movement
  , getPossibleMoves
  , accessCell
  )
  where

import Prelude

import Data.Maybe (Maybe(..))
import Data.List (List(..), (:), concat)
import Data.Array (index)


import ProjectTypes (Kind(..), Position, Board, PlayerNum(..), Piece)
import Config (rows, columns)


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
  getPossibleMoves Pawn board position player
    | player == One = moveSearcher (position {row = (position.row-1)}) board player 0 (-1)  1
    | otherwise     = moveSearcher (position {row = (position.row+1)}) board player 0   1   1
    
  getPossibleMoves Bishop board position player =
    concat  $ moveSearcher {col: (position.col-1), row: (position.row-1)} board player (-1) (-1)  rows
            : moveSearcher {col: (position.col-1), row: (position.row+1)} board player (-1)   1   rows
            : moveSearcher {col: (position.col+1), row: (position.row-1)} board player   1  (-1)  rows
            : moveSearcher {col: (position.col+1), row: (position.row+1)} board player   1    1   rows
            : Nil

  getPossibleMoves Rook board position player =
    concat  $ moveSearcher {col: (position.col), row: (position.row-1)} board player   0 (-1)  rows
            : moveSearcher {col: (position.col), row: (position.row+1)} board player   0   1   rows
            : moveSearcher {col: (position.col-1), row: (position.row)} board player (-1)  0   rows
            : moveSearcher {col: (position.col+1), row: (position.row)} board player   1   0   rows
            : Nil

  getPossibleMoves Prince board position player =
    concat  $ moveSearcher {col: (position.col), row: (position.row-1)} board player   0 (-1)  1
            : moveSearcher {col: (position.col), row: (position.row+1)} board player   0   1   1
            : moveSearcher {col: (position.col-1), row: (position.row)} board player (-1)  0   1
            : moveSearcher {col: (position.col+1), row: (position.row)} board player   1   0   1
            : Nil

  getPossibleMoves Princess board position player =
    concat  $ moveSearcher {col: (position.col-1), row: (position.row-1)} board player (-1) (-1)  1
            : moveSearcher {col: (position.col-1), row: (position.row+1)} board player (-1)   1   1
            : moveSearcher {col: (position.col+1), row: (position.row-1)} board player   1  (-1)  1
            : moveSearcher {col: (position.col+1), row: (position.row+1)} board player   1    1   1
            : Nil


  --getPossibleMoves Rook board position player = 

-- Access a specific column and row of the board
-- 0 indexed, 1st row 1st col is accessCell 0 0 board
-- Returns a Maybe Piece, with Nothing if cell is not occupied
-- and Just Piece if a piece is present
accessCell :: Int -> Int -> Board -> Maybe Piece
accessCell col row board = case cell of
    Nothing -> Nothing
    Just maybe_piece -> maybe_piece
  where
    cell =
      board
      # (flip index) row
      >>= (flip index) col

-- Abstraction for searching for moves
-- Position: start of tile to search (not current position of piece)
-- colMove: vertical movement 
-- rowMove: horizontal movement
-- limit: number of tiles to search for in specific direction
-- Returns a list of Positions the piece can move to
moveSearcher :: Position -> Board -> PlayerNum -> Int -> Int -> Int -> List Position
moveSearcher {col, row} _ _ _ _ limit | row < 0 || col < 0 || row >= rows || col >= columns || limit <= 0 = Nil
moveSearcher {col, row} board player colMove rowMove limit = 
  case accessCell col row board of
    Nothing -> {col, row} : moveSearcher {col: (col+colMove), row: (row+rowMove)} board player colMove rowMove (limit-1)
    Just piece -> if piece.player /= player then {col, row} : Nil else Nil