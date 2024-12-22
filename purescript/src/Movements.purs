module Movements
  ( class Movement
  , getPossibleMoves
  , accessBoard
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

