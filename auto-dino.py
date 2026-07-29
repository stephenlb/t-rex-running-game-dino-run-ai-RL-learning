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
    return torch.Tensor([[
        frame['speed'],
        frame['obstacles'][0][0], #x1
        frame['obstacles'][0][1], #y1
        frame['obstacles'][1][0], #x2
        frame['obstacles'][1][1], #y2
        frame['crashed'],
        frame['jumping'],
        frame['jump_velocity'],
    ]])

model = dqn_algo.Model()
def environment(inbox, outbox):
    future = None
    while True:

        ## Calculate Future and Current State Features
        if future == None: current = extract_features(inbox.get())
        else:              current = future
        future = extract_features(inbox.get())
        print(future.shape)
        #print(future)

        ## Calculate Reward
        crashed = future[0][5]
        if crashed: reward = -10.0
        else:       reward = 0.3
        reward = torch.Tensor([[reward]])

        ## Action
        jump = current[0][7]
        action = torch.IntTensor([int(jump)]) ## [jump]
        #out = model(future)
        loss = model.compute_loss(
            current,
            reward,
            action, 
            future,
        )
        ##loss.backward()
        print(loss)

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


