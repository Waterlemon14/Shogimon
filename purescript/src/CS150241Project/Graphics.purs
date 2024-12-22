module CS150241Project.Graphics
  ( clearCanvas
  , drawCircle
  , drawCircleOutline
  , drawRect
  , drawRectOutline
  , drawText
  , drawImage
  , drawImageScaled
  ) where

import Prelude

import Data.Maybe (Maybe(..))
import Data.Number as Number
import Effect (Effect)
import Graphics.Canvas as Canvas

clearCanvas
  :: Canvas.Context2D
  -> { width :: Number, height :: Number, color :: String }
  -> Effect Unit
clearCanvas ctx { width, height, color } = do
  Canvas.setFillStyle ctx color
  Canvas.rect ctx { x: 0.0, y: 0.0, width: width, height: height }
  Canvas.fill ctx

fillWith :: Canvas.Context2D -> String -> Effect Unit
fillWith ctx color = do
  Canvas.setFillStyle ctx color
  Canvas.fill ctx

strokeWith :: Canvas.Context2D -> String -> Effect Unit
strokeWith ctx color = do
  Canvas.setFillStyle ctx color
  Canvas.stroke ctx

drawRect
  :: Canvas.Context2D
  -> { x :: Number
     , y :: Number
     , width :: Number
     , height :: Number
     , color :: String
     }
  -> Effect Unit
drawRect ctx { x, y, width, height, color } = do
  Canvas.beginPath ctx
  Canvas.rect ctx { x, y, width, height }
  fillWith ctx color

drawRectOutline
  :: Canvas.Context2D
  -> { x :: Number
     , y :: Number
     , width :: Number
     , height :: Number
     , color :: String
     }
  -> Effect Unit
drawRectOutline ctx { x, y, width, height, color } = do
  Canvas.beginPath ctx
  Canvas.rect ctx { x, y, width, height }
  strokeWith ctx color

startCircle
  :: Canvas.Context2D
  -> { x :: Number
     , y :: Number
     , radius :: Number
     }
  -> Effect Unit
startCircle ctx { x, y, radius } = do
  Canvas.beginPath ctx
  Canvas.arc ctx
    { start: 0.0
    , end: 2.0 * Number.pi
    , radius
    , useCounterClockwise: false
    , x
    , y
    }

drawCircle
  :: Canvas.Context2D
  -> { x :: Number
     , y :: Number
     , radius :: Number
     , color :: String
     }
  -> Effect Unit
drawCircle ctx { x, y, radius, color } = do
  startCircle ctx { x, y, radius }
  fillWith ctx color

drawCircleOutline
  :: Canvas.Context2D
  -> { x :: Number
     , y :: Number
     , radius :: Number
     , color :: String
     }
  -> Effect Unit
drawCircleOutline ctx { x, y, radius, color } = do
  startCircle ctx { x, y, radius }
  strokeWith ctx color

drawText
  :: Canvas.Context2D
  -> { x :: Number
     , y :: Number
     , text :: String
     , font :: String
     , size :: Int
     , color :: String
     }
  -> Effect Unit
drawText ctx { x, y, text, font, size, color } = do
  let style = show size <> "px " <> font
  Canvas.setFont ctx style
  Canvas.setFillStyle ctx color
  metrics <- Canvas.measureText ctx text
  Canvas.fillText ctx text (x - metrics.width / 2.0) y

drawImage
  :: Canvas.Context2D
  -> Canvas.CanvasImageSource
  -> { x :: Number
     , y :: Number
     }
  -> Effect Unit
drawImage ctx img { x, y } = Canvas.drawImage ctx img x y

drawImageScaled
  :: Canvas.Context2D
  -> Canvas.CanvasImageSource
  -> { x :: Number
     , y :: Number
     , width :: Number
     , height :: Number
     }
  -> Effect Unit
drawImageScaled ctx img { x, y, width, height } =
  Canvas.drawImageScale ctx img x y width height
