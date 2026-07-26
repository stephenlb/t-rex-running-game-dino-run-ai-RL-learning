import torch
from torch import nn
from torch import Tensor,IntTensor
import torch.nn.functional as F


NUM_INPUTS = 10 #idk what this should be
NUM_MOVES = 3

DECAY = 0.8 #play with this

class Model(nn.Module):
    def __init__(self,hidden=3):
        super().__init__()
        self.first = nn.linear(NUM_INPUTS,hidden)
        self.second = nn.linear(hidden,NUM_MOVES)

    def forward(self, state: Tensor) -> Tensor:
        x = F.relu(self.first(state))
        return self.second(x)


    def compute_loss(self,current:Tensor,reward:Tensor,action :IntTensor,future:Tensor):
        #start by seeing what the model guesses
        guess = (
            self.forward(current)
            .gather(-1, action.reshape(-1, 1))
            .squeeze(-1)
        )

        #look one move to the future, see what it thinks then
        with torch.no_grad():
            future_guess = self.forward(future).max(-1).values

        #we can now do a better job guessing
        better_guess = reward + DECAY*future_guess

        #well we can improve our guess now
        error = guess - better_guess

        #solving for error=0 is called solving the bellman equation
        #it is written diffrently in other places but thats the idea 
        #it happens there is only 1 solution


        loss = error.abs().mean() #just abs for now but can be fancy
        # loss = nn.HuberLoss(error) #this is a fancy mix of l1 and l2     
        return loss
