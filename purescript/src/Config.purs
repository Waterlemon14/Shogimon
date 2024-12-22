module Config
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
  )
  where

import Prelude

import Data.Int (toNumber, floor)


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