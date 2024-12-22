module CS150241Project.GameEngine
  ( startNetworkGame
  ) where

import Prelude

import CS150241Project.Networking (NetworkingState, Message, connect)
import Data.Array (foldl)
import Data.Foldable (for_)
import Data.Map as Map
import Data.Maybe (Maybe(..))
import Effect (Effect)
import Effect.Console (log)
import Effect.Ref as Ref
import Effect.Timer (setTimeout)
import Graphics.Canvas as Canvas
import Web.DOM.Document (toNonElementParentNode)
import Web.DOM.Element as Element
import Web.DOM.NonElementParentNode (getElementById)
import Web.Event.Event (EventType(..), preventDefault)
import Web.Event.EventTarget (eventListener, addEventListener)
import Web.HTML (window)
import Web.HTML.HTMLDocument as HTMLDocument
import Web.HTML.Window (document, requestAnimationFrame)
import Web.UIEvent.KeyboardEvent as KeyboardEvent
import Web.UIEvent.MouseEvent as MouseEvent

type GameEngineSettings gameState =
  { initialState :: Effect gameState
  , onTick :: (String -> Effect Unit) -> gameState -> Effect gameState
  , onMouseDown :: (String -> Effect Unit) -> { x :: Int, y :: Int } -> gameState -> Effect gameState
  , onKeyDown :: (String -> Effect Unit) -> String -> gameState -> Effect gameState
  , onKeyUp :: (String -> Effect Unit) -> String -> gameState -> Effect gameState
  , onRender :: Map.Map String Canvas.CanvasImageSource -> Canvas.Context2D -> gameState -> Effect Unit
  , onMessage :: (String -> Effect Unit) -> Message -> gameState -> Effect gameState
  , fps :: Int
  , width :: Number
  , height :: Number
  , ipAddress :: String
  , port :: Int
  , imagePaths :: Array String
  }

type GameEngine gameState =
  { initialState :: Effect gameState
  , onTick :: (String -> Effect Unit) -> gameState -> Effect gameState
  , onMouseDown :: (String -> Effect Unit) -> { x :: Int, y :: Int } -> gameState -> Effect gameState
  , onKeyDown :: (String -> Effect Unit) -> String -> gameState -> Effect gameState
  , onRender :: Map.Map String Canvas.CanvasImageSource -> Canvas.Context2D -> gameState -> Effect Unit
  , onMessage :: (String -> Effect Unit) -> Message -> gameState -> Effect gameState
  , fps :: Int
  , ctx :: Canvas.Context2D
  , refState :: Ref.Ref gameState
  , width :: Number
  , height :: Number
  , ipAddress :: String
  , port :: Int
  , networkingState :: NetworkingState
  , refImages :: Ref.Ref (Map.Map String Canvas.CanvasImageSource)
  }

startNetworkGame :: forall gameState. GameEngineSettings gameState -> Effect Unit
startNetworkGame settings = do
  networkingState <- connect settings.ipAddress settings.port
  w <- window
  doc <- document w

  maybeCanvas <- Canvas.getCanvasElementById "cs150-game-canvas"
  maybeElemCanvas <-
    getElementById "cs150-game-canvas"
      $ toNonElementParentNode
      $ HTMLDocument.toDocument doc

  initState <- settings.initialState
  refState <- Ref.new initState

  refImages <- Ref.new Map.empty

  for_ settings.imagePaths
    ( \path ->
        Canvas.tryLoadImage path
          ( \maybeImg ->
              case maybeImg of
                Nothing -> pure unit
                Just img -> do
                  images <- Ref.read refImages
                  Ref.write (Map.insert path img images) refImages
          )
    )

  keyDownHandler <- eventListener
    ( \e -> case KeyboardEvent.fromEvent e of
        Just ev -> do
          preventDefault e
          state <- Ref.read refState
          newState <- settings.onKeyDown networkingState.send (KeyboardEvent.code ev) state
          Ref.write newState refState
        Nothing -> pure unit
    )

  keyUpHandler <- eventListener
    ( \e -> case KeyboardEvent.fromEvent e of
        Just ev -> do
          preventDefault e
          state <- Ref.read refState
          newState <- settings.onKeyUp networkingState.send (KeyboardEvent.code ev) state
          Ref.write newState refState
        Nothing -> pure unit
    )

  mouseDownHandler <- eventListener
    ( \e -> case MouseEvent.fromEvent e of
        Just ev -> do
          preventDefault e
          state <- Ref.read refState
          newState <- settings.onMouseDown networkingState.send
            { x: MouseEvent.clientX ev, y: MouseEvent.clientY ev }
            state
          Ref.write newState refState
        Nothing -> pure unit
    )

  addEventListener (EventType "keydown") keyDownHandler false (HTMLDocument.toEventTarget doc)
  addEventListener (EventType "keyup") keyUpHandler false (HTMLDocument.toEventTarget doc)

  case maybeCanvas, maybeElemCanvas of
    (Just canvas), (Just elemCanvas) -> do
      addEventListener (EventType "mousedown") mouseDownHandler false (Element.toEventTarget elemCanvas)
      Canvas.setCanvasDimensions canvas { width: settings.width, height: settings.height }
      ctx <- Canvas.getContext2D canvas
      let
        engine =
          { initialState: settings.initialState
          , onTick: settings.onTick
          , onMouseDown: settings.onMouseDown
          , onKeyDown: settings.onKeyDown
          , onRender: settings.onRender
          , onMessage: settings.onMessage
          , fps: settings.fps
          , ctx: ctx
          , refState: refState
          , width: settings.width
          , height: settings.height
          , ipAddress: settings.ipAddress
          , port: settings.port
          , networkingState
          , refImages
          }
      gameLoop engine
    _, _ -> log "Canvas not found."

gameLoop :: forall gameState. GameEngine gameState -> Effect Unit
gameLoop engine = do
  w <- window
  void $ setTimeout (1000 / engine.fps) do
    void $ (flip requestAnimationFrame) w do
      state1 <- Ref.read engine.refState
      state2 <- engine.onTick engine.networkingState.send state1
      messages <- engine.networkingState.recv
      state3 <- foldl
        ( \acc maybeMsg ->
            case maybeMsg of
              Nothing -> acc
              Just msg -> do
                state <- acc
                engine.onMessage engine.networkingState.send msg state
        )
        (pure state2)
        messages

      Ref.write state3 engine.refState
      images <- Ref.read engine.refImages
      engine.onRender images engine.ctx state3

      gameLoop engine
