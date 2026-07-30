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

## Watch the human play and learn from their moves
def environment(inbox, outbox):
    future = extract_features(inbox.get())
    while True:
        current = future
        future = extract_features(inbox.get())

        ## Calculate Reward
        crashed = bool(future[0][5])
        if crashed: reward = -10.0
        else:       reward = 0.3

        ## Action the human took
        jump = int(current[0][6])

        loss = model.learn(
            current,
            torch.Tensor([[reward]]),
            torch.IntTensor([[jump]]), ## [jump]
            future,
            torch.Tensor([[1.0 if crashed else 0.0]]),
        )
        print(f'human={jump} model={model.act(current, explore=0)} reward={reward:.1f} loss={loss:.4f}')

inbox = Queue()
outbox = Queue()

threads = [
    threading.Thread(target=pubnub.subscribe, args=(GAME_STATE_CHANNEL, inbox,), daemon=True),
    threading.Thread(target=environment, args=(inbox, outbox,), daemon=True),
]

for thread in threads: thread.start()

try:
    for thread in threads: thread.join()
except KeyboardInterrupt:
    print('\nstopping')


