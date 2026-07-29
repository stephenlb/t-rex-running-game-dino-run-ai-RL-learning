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

def extract_features(frame: dict) -> torch.Tensor:
    return torch.Tensor([
        frame['speed'],
        frame['obstacles'][0][0], #x1
        frame['obstacles'][0][1], #y1
        frame['obstacles'][1][0], #x2
        frame['obstacles'][1][1], #y2
        frame['crashed'],
        frame['jumping'],
        frame['jump_velocity'],
    ])

model = dqn_algo.Model()
def environment(inbox, outbox):
    future = None
    while True:
        if future == None:
            current = extract_features(inbox.get())
        else:
            current = future
        future  = extract_features(inbox.get())
        print(future)
        out = model(future)
        print(out)

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


