import torch
from torch import nn
from torch import Tensor, IntTensor
import torch.nn.functional as F

NUM_INPUTS = 8 #idk what this should be
NUM_MOVES = 2
DECAY = 0.8 #play with this

class Model(nn.Module):
    def __init__(self,hidden=3):
        super().__init__()
        self.first = nn.Linear(NUM_INPUTS,hidden)
        self.second = nn.Linear(hidden,NUM_MOVES)

    def forward(self, state: Tensor) -> Tensor:
        x = F.relu(self.first(state))
        return self.second(x)

    ## DQN
    def compute_loss(self,current:Tensor,reward:Tensor,action :IntTensor,future:Tensor):
        #start by seeing what the model guesses
        #action = action.reshape(-1, 1)
        out = self.forward(current)
        print('out',out.shape)
        print('action',action.shape)
        guess = (
            self.forward(current)
            .gather(1, action)
        )

        #look one move to the future, see what it thinks then
        with torch.no_grad():
            future_guess = self.forward(future).max(-1, keepdim=True).values

        #we can now do a better job guessing
        better_guess = reward + DECAY * future_guess

        #well we can improve our guess now
        error = guess - better_guess

        #solving for error=0 is called solving the bellman equation
        #it is written diffrently in other places but thats the idea 
        #it happens there is only 1 solution

        loss = error.abs().mean() #just abs for now but can be fancy
        # loss = nn.HuberLoss(error) #this is a fancy mix of l1 and l2     
        return loss
