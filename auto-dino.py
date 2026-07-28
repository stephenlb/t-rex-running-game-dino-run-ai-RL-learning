## TODO Receive game state data
## TODO Transmit Player Moves
## TODO 
## TODO 
## TODO 
import pubnub
import torch
import threading
from queue import Queue

import dqn_algo

GAME_STATE_CHANNEL = 't-rex-dino-game-state'
GAME_MOVE_CHANNEL = 't-rex-dino-game-movement'

model = dqn_algo.Model()
def environment(inbox, outbox):
    future = None
    while True:
        current = future or inbox.get()
        future  = inbox.get()
        print(future)

## Subscription Inbox
inbox = Queue()
subscription = threading.Thread(target=pubnub.subscribe, args=(GAME_STATE_CHANNEL, inbox,))
subscription.start()

## Publish Game Movement Predictions
outbox = Queue()
simulation = threading.Thread(target=environment, args=(inbox, outbox,))
simulation.start()

## Join threads
simulation.join()
subscription.join()


