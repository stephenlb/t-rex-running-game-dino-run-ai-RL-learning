## TODO Receive game state data
## TODO Transmit Player Moves
## TODO 
## TODO 
## TODO 
GAME_CHANNEL='t-rex-dino-game-state'
import pubnub

import numpy as np
import gymnasium as gym

from gymnasium import spaces

from stable_baselines3 import DQN
from stable_baselines3.common.evaluation import evaluate_policy

class Environment(gym.Env):
    def __init__(self):
        super().__init__()
        ## [Jump, Nothing, Duck]
        self.action_space = spaces.Discrete(3)

        ## Input Features time, speed, obsc x1,y1, x2,y2, game-ver, jumping, jumpVel
        self.observation_space = spaces.Box(
            low=-1.0,
            high=2.0,
            shape=(9,),
            dtype=np.float32,
        )

    def step(self, actions):
        pass
        

    def _state(self):
        return np.array([
            
        ])
