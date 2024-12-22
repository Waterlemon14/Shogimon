module CS150241Project.Networking
  ( PlayerId(..)
  , toMessage
  , connect
  , Message
  , NetworkingState
  ) where

import Prelude

import Control.Monad.Except (runExceptT)
import Data.Array (length, slice, (!!))
import Data.Either (Either(..))
import Data.Foldable (for_)
import Data.Generic.Rep (class Generic)
import Data.Identity (Identity(..))
import Data.Int (fromString)
import Data.Maybe (Maybe(..))
import Data.Show.Generic (genericShow)
import Data.String (Pattern(..), joinWith, split)
import Effect (Effect)
import Effect.Console (log)
import Foreign (readString)
import Web.Event.EventTarget (addEventListener, eventListener)
import Web.Socket.Event.EventTypes (onMessage)
import Web.Socket.Event.MessageEvent (fromEvent, data_)
import Web.Socket.WebSocket (WebSocket, create, sendString, toEventTarget)
import Effect.AVar as AVar

data PlayerId
  = Player1
  | Player2

derive instance Generic PlayerId _

instance Show PlayerId where
  show = genericShow

type Message = { playerId :: PlayerId, payload :: String }

toPlayerId :: Int -> Maybe PlayerId
toPlayerId n
  | n == 1 = Just Player1
  | n == 2 = Just Player2
  | otherwise = Nothing

toMessage :: String -> Maybe Message
toMessage s = do
  let tokens = split (Pattern " ") s
  playerId <- (tokens !! 0 >>= fromString >>= toPlayerId)
  let payload = slice 1 (length tokens) tokens # joinWith " "

  Just { playerId, payload }

sendMessage :: WebSocket -> Message -> Effect Unit
sendMessage ws message = sendString ws message.payload

type NetworkingState =
  { avPlayerId :: AVar.AVar PlayerId
  , send :: (String -> Effect Unit)
  , processSendQueue :: Effect Unit
  , recv :: Effect (Array (Maybe Message))
  }

connect :: String -> Int -> Effect NetworkingState
connect ipAddr port = do
  let addr = "ws://" <> ipAddr <> ":" <> show port
  ws <- create addr []

  avPlayerId <- AVar.empty
  avSendQueue <- AVar.new []
  avRecvQueue <- AVar.new []

  let
    send :: String -> Effect Unit
    send payload = do
      maybePlayerId <- AVar.tryRead avPlayerId
      case maybePlayerId of
        Nothing -> do
          log $ "Added to send queue: " <> payload

          let
            doWhenFilled (Left _) = pure unit
            doWhenFilled (Right sendQueue) = do
              void $ AVar.put (sendQueue <> [ payload ]) avSendQueue (\_ -> pure unit)
              pure unit

          void $ AVar.take avSendQueue doWhenFilled
          pure unit

        Just playerId -> do
          let messageToSend = { playerId, payload }
          sendMessage ws messageToSend

    processSendQueue :: Effect Unit
    processSendQueue = do
      let
        doWhenSendQueueFilled (Left _) = pure unit
        doWhenSendQueueFilled (Right sendQueue) = for_ sendQueue send

      void $ AVar.take avSendQueue doWhenSendQueueFilled
      pure unit

    recv :: Effect (Array (Maybe Message))
    recv = do
      maybeRecvQueue <- AVar.tryTake avRecvQueue
      case maybeRecvQueue of
        Nothing -> pure []
        Just recvQueue -> do
          void $ AVar.tryPut [] avRecvQueue
          pure recvQueue

    addToRecvQueue :: Message -> Effect Unit
    addToRecvQueue message = do
      let
        doWhenFilled (Left _) = pure unit
        doWhenFilled (Right recvQueue) = do
          void $ AVar.put (recvQueue <> [ Just message ]) avRecvQueue (\_ -> pure unit)
          pure unit

      void $ AVar.take avRecvQueue doWhenFilled
      pure unit

    state = { avPlayerId, send, processSendQueue, recv }

  messageListener <- eventListener \ev -> do
    case fromEvent ev of
      Nothing -> log "Failed to convert Event to MessageEvent"
      Just messageEvent -> do
        case runExceptT $ readString $ data_ messageEvent of
          Identity e ->
            case e of
              Left _ -> log "Failed to read Foreign as String"
              Right s -> do
                case toMessage s of
                  Nothing -> log $ "Failed to make message from " <> s
                  Just message -> do
                    maybePlayerId <- AVar.tryRead state.avPlayerId

                    case maybePlayerId of
                      Nothing -> do
                        void $ AVar.put message.playerId state.avPlayerId (\_ -> pure unit)
                        state.processSendQueue

                      Just _ -> do
                        addToRecvQueue message
                        state.processSendQueue

  addEventListener onMessage messageListener false (toEventTarget ws)

  pure state
