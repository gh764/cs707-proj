import itertools
import scipy

def pairwise(iterable):
    """take the iterable, make a copy, advance by one in the second and return pairs"""
    iter1, iter2 = itertools.tee(iterable)
    next(iter2, None)
    return itertools.izip(iter1, iter2)



class Markov:
    """This is a general purpose markov generator for time series data
    """
    
    def __init__(self, num_steps, num_states, minutes_in_step, 
                 state_measurements):
        """num_steps -> number of steps in the chain
        num_states -> number of states ( ie number of regions of interest )
        minutes_in_step -> number of minutes between transitions
        state_measurements -> a tuple of (time, occupied region )
        """
        self.minutes_in_step = minutes_in_step
        self.state_measurements = state_measurements
        self.num_states = num_states
        self.num_steps = num_steps
        self.state_map = {}
        self.state_count = 0
        self.transition_matrix = scipy.array((num_steps, num_states, num_states), int)
        self.__build()
  
    def __build(self):
        """build the markov model"""
        state_measurements = sorted(self.state_measurements,
                                    key = lambda state : state[0])
        
        state_measurements = pairwise(state_measurements)
        
        for (time1, state1), (time2, state2) in self.state_measurements:
            
            # get the array indices
            step_1 = self.get_step_number(time1)
            state_index1 = self.get_state_number(state1)
            
            step_2 = self.get_step_number(time2)
            state_index2 = self.get_state_number(state2)


            # check for a missing sample before keeping track of the data
            if ((step_2-step_1)==1) or ( step_2==(self.num_steps-1) and step_1==0):
                self.transition_matrix[step_1, state_index1, state_index2] += 1
                
                   
    def get_state_number(self, state):
        """Given a state return an index for that state"""
        if state not in self.state_map:
            self.state_map[state] = self.state_count
            self.state_count = self.state_count+1

        return self.state_map[state]

    def get_step_number(self, time_date):
        """given a time return an step index for that time"""
        minutes_past_midnight = time_date.hour*60. + time_date.minute + \
            time_date.second / 60.
        
        return int(minutes_past_midnight / self.minutes_in_step)
        




