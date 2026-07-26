## TODO Receive game state data
## TODO Transmit Player Moves
## TODO 
## TODO 
## TODO 
import pubnub
import torch
import threading
from queue import Queue

GAME_STATE_CHANNEL = 't-rex-dino-game-state'
GAME_MOVE_CHANNEL = 't-rex-dino-game-movement'

## Subscription Inbox
inbox = Queue()
subscription = threading.Thread(target=pubnub.subscribe, args=(GAME_STATE_CHANNEL, inbox,))
subscription.start()

## Publish Game Movement
outbox = Queue()
publishing = threading.Thread(target=pubnub.publisher, args=(inbox, outbox,))
publishing.start()

## Join threads
subscription.join()
publishing.join()
