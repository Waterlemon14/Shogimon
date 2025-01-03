module Movements
  ( accessCell
  , class Movement
  , getPossibleMoves
  , protectedPieceMovementCells
  )
  where

import Prelude

import Data.Maybe (Maybe(..))
import Data.List (List(..), (:), concat, filter)
import Data.Array (index)
import Data.Foldable (notElem)


import ProjectTypes (Kind(..), Position, Board, PlayerNum(..), Piece)
import Config (rows, columns)


-- Typeclass to get the possible moves of a piece kind
-- Whenever adding a piece kind, add to the instantiation below
class Movement a where
  -- getPossibleMoves should return a list of all possible moves that can be taken
  -- by the piece in its current position given the Board, Position, PlayerNum, and if it isProtected.

  -- Given its position, check the board if the move is valid. When checking its
  -- moves against another piece, check the PlayerNum of that piece vs. the given
  -- PlayerNum to determine whether it is a valid move to capture it or not.
  getPossibleMoves :: a -> Board -> Position -> PlayerNum -> Boolean -> Boolean -> List Position

-- Define getPossibleMoves of the new kind added here
-- Inputs: Kind, Board, Piece Position, Owner of Piece, isPieceProtected, isPieceCaptured
instance Movement Kind where
  getPossibleMoves _ board _ _ _ true = getFreeCells board 0 0

  getPossibleMoves Pawn board position player isProtected _
    | player == One = moveSearcher (position {row = (position.row-1)}) board player 0 (-1) 1 isProtected
    | otherwise     = moveSearcher (position {row = (position.row+1)}) board player 0   1  1 isProtected
    
  getPossibleMoves Bishop board position player isProtected _ =
    concat  $ moveSearcher {col: (position.col-1), row: (position.row-1)} board player (-1) (-1) rows isProtected
            : moveSearcher {col: (position.col-1), row: (position.row+1)} board player (-1)   1  rows isProtected
            : moveSearcher {col: (position.col+1), row: (position.row-1)} board player   1  (-1) rows isProtected
            : moveSearcher {col: (position.col+1), row: (position.row+1)} board player   1    1  rows isProtected
            : Nil

  getPossibleMoves Rook board position player isProtected _ =
    concat  $ moveSearcher {col: (position.col), row: (position.row-1)} board player   0 (-1) rows isProtected
            : moveSearcher {col: (position.col), row: (position.row+1)} board player   0   1  rows isProtected
            : moveSearcher {col: (position.col-1), row: (position.row)} board player (-1)  0  rows isProtected
            : moveSearcher {col: (position.col+1), row: (position.row)} board player   1   0  rows isProtected
            : Nil

  getPossibleMoves Prince board position player isProtected _ =
    concat  $ moveSearcher {col: (position.col), row: (position.row-1)} board player   0 (-1) 1 isProtected
            : moveSearcher {col: (position.col), row: (position.row+1)} board player   0   1  1 isProtected
            : moveSearcher {col: (position.col-1), row: (position.row)} board player (-1)  0  1 isProtected
            : moveSearcher {col: (position.col+1), row: (position.row)} board player   1   0  1 isProtected
            : Nil

  getPossibleMoves Princess board position player isProtected _ =
    concat  $ moveSearcher {col: (position.col-1), row: (position.row-1)} board player (-1) (-1) 1 isProtected
            : moveSearcher {col: (position.col-1), row: (position.row+1)} board player (-1)   1  1 isProtected
            : moveSearcher {col: (position.col+1), row: (position.row-1)} board player   1  (-1) 1 isProtected
            : moveSearcher {col: (position.col+1), row: (position.row+1)} board player   1    1  1 isProtected
            : Nil


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
moveSearcher :: Position -> Board -> PlayerNum -> Int -> Int -> Int -> Boolean -> List Position
moveSearcher {col, row} _ _ _ _ limit _ | row < 0 || col < 0 || row >= rows || col >= columns || limit <= 0 = Nil
moveSearcher {col, row} board player colMove rowMove limit isProtected = 
  case accessCell col row board of
    Nothing -> {col, row} : moveSearcher {col: (col+colMove), row: (row+rowMove)} board player colMove rowMove (limit-1) isProtected
    
    Just piece -> case isProtected of 

      true -> Nil
      false -> case piece.player /= player of

        true -> if piece.isProtected then Nil else {col, row} : Nil     -- meaning piece in cell cannot be eaten
        false -> Nil

getFreeCells :: Board -> Int -> Int -> List Position
getFreeCells board col row 
  | row >= rows = Nil  -- Base case
  | col >= columns = getFreeCells board 0 (row+1) -- Once whole row searched, search next row
  | otherwise = case accessCell col row board of
    Nothing     -> if notElem {col: col, row: row} invalidCells
      then {col, row} : getFreeCells board (col+1) row
      else getFreeCells board (col+1) row
    Just _  -> getFreeCells board (col+1) row

    where 
      invalidCells = concat $ (protectedPieceMovementCells 0 0 board One) : (protectedPieceMovementCells 0 0 board Two) : Nil

-- Revert change
-- removeMovesWithConflict :: Int -> Int -> Board -> PlayerNum -> List Position -> List Position
-- removeMovesWithConflict col row board player current_moves
--   | row >= rows = current_moves  -- Base case
--   | col >= columns = removeMovesWithConflict 0 (row+1) board player current_moves-- Once whole row searched, search next row
--   | otherwise = case accessCell col row board of
--     Nothing -> removeMovesWithConflict (col+1) row board player current_moves
--     Just current_piece -> if current_piece.player == player
--       then removeMovesWithConflict (col+1) row board player current_moves
--       else removeMovesWithConflict (col+1) row board player updated_moves
--         where
--           checker = (flip notElem) (getPossibleMoves current_piece.kind board current_piece.position current_piece.player current_piece.isProtected (current_piece.position.col == (-1) && current_piece.position.row == (-1)))
--           updated_moves = filter checker current_moves

protectedPieceMovementCells :: Int -> Int -> Board -> PlayerNum -> List Position
protectedPieceMovementCells c r board player
        | r >= rows = Nil                                                 -- Base case
        | c >= columns = protectedPieceMovementCells 0 (r+1) board player -- Once whole row searched, search next row
        | otherwise = case accessCell c r board of 
          Nothing -> protectedPieceMovementCells (c+1) r board player
          Just piece -> if piece.isProtected && piece.player == player
            then concat $ getPossibleMoves piece.kind board piece.position piece.player piece.isProtected false
                        : protectedPieceMovementCells (c+1) r board player 
                        : Nil
            else protectedPieceMovementCells (c+1) r board player

