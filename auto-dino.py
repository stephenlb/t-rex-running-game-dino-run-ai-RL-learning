## TODO Receive game state data
## TODO Transmit Player Moves
## TODO 
## TODO 
## TODO 
import pubnub
import torch

GAME_CHANNEL='t-rex-dino-game-state'
game_state_channel = 't-rex-dino-game-state'
game_move_channel = 't-rex-dino-game-movement'

## Subscription Inbox
inbox = Queue()
subscription = threading.Thread(target=subscribe, args=(game_state_channel, inbox,))
subscription.start()

## Publish Game Movement
outbox = Queue()
publishing = threading.Thread(target=publisher, args=(inbox, outbox,))
publishing.start()

## Join threads
subscription.join()
publishing.join()
