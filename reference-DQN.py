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