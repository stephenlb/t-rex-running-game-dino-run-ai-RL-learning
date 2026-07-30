import random

import torch
from torch import nn
from torch import Tensor, IntTensor
import torch.nn.functional as F

NUM_INPUTS = 8 #idk what this should be
NUM_MOVES = 2
DECAY = 0.8 #play with this
LEARNING_RATE = 1e-3

class Model(nn.Module):
    def __init__(self,hidden=32):
        super().__init__()
        self.first = nn.Linear(NUM_INPUTS,hidden)
        self.second = nn.Linear(hidden,NUM_MOVES)
        self.optimizer = torch.optim.Adam(self.parameters(), lr=LEARNING_RATE)

    def forward(self, state: Tensor) -> Tensor:
        x = F.relu(self.first(state))
        return self.second(x)

    ## Pick a move: mostly the best guess, sometimes random to explore
    def act(self, state: Tensor, explore: float = 0.1) -> int:
        if random.random() < explore:
            return random.randrange(NUM_MOVES)
        with torch.no_grad():
            return int(self.forward(state).argmax(-1).item())

    ## DQN
    def compute_loss(self,current:Tensor,reward:Tensor,action:IntTensor,future:Tensor,done:Tensor=None):
        #start by seeing what the model guesses
        guess = (
            self.forward(current)
            .gather(-1, action.reshape(-1, 1).long())
        )

        #look one move to the future, see what it thinks then
        with torch.no_grad():
            future_guess = self.forward(future).max(-1, keepdim=True).values
            #when the game is over there is no future to look at
            if done is not None:
                future_guess = future_guess * (1.0 - done.reshape(-1, 1).float())

        #we can now do a better job guessing
        better_guess = reward.reshape(-1, 1) + DECAY * future_guess

        #well we can improve our guess now
        error = guess - better_guess

        #solving for error=0 is called solving the bellman equation
        #it is written diffrently in other places but thats the idea 
        #it happens there is only 1 solution

        loss = error.abs().mean() #just abs for now but can be fancy
        # loss = nn.HuberLoss(error) #this is a fancy mix of l1 and l2
        return loss

    def learn(self,current:Tensor,reward:Tensor,action:IntTensor,future:Tensor,done:Tensor=None) -> float:
        loss = self.compute_loss(current, reward, action, future, done)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return float(loss.item())
