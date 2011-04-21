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

        self.transition_matrix = scipy.zeros((num_steps, num_states, num_states), scipy.float64)
        self.__build()
  
    def __build(self):
        """build the markov model"""

        state_measurements = sorted(self.state_measurements,
                                    key = lambda state : state[0])

        state_measurements = pairwise(state_measurements)
        
        for (time1, state1), (time2, state2) in state_measurements:

            # get the array indices
            step_1 = self.get_step_number(time1)
            state_index1 = self.get_state_number(state1)
            
            step_2 = self.get_step_number(time2)
            state_index2 = self.get_state_number(state2)

            # check for a missing sample before keeping track of the data
            if ((step_2-step_1)==1) or ( step_2==0 ):
                self.transition_matrix[step_1, state_index1, state_index2] += 1.0
            else:
                print "missing data!"

        for step_num in range(self.num_steps):
            m = self.transition_matrix[step_num, :, :,]

            for state_num in range(self.num_states):
                mat = self.transition_matrix[step_num, state_num, :,]
                s = sum(mat)*1.0
                if s != 0:
                    self.transition_matrix[step_num, state_num, :,] = mat/s

    def get_prob_vector(self, start_state, start_time, stop_time, stop_state):

        if start_state not in self.state_map:
            raise RuntimeError("unknown start state: %s" % start_state)

        if stop_state not in self.state_map:
            raise RuntimeError("unknown stop state: %s" % stop_state)

        # steps in 'time' increments
        start_step = self.get_step_number(start_time)
        stop_step = self.get_step_number(stop_time)

        # a state is what place the user is occupying at some time
        start_state_index = self.get_state_number(start_state)
        stop_state_index = self.get_state_number(stop_state)

        history_list = []

        wrap = False
        if(start_step>stop_step):
            # this calculation wraps around the week
            # get the max step number
            loop_limit_step = self.get_max_step()
            wrap=True
        else:
            loop_limit_step = stop_step

        prob_vector = self.transition_matrix[start_step, start_state_index,:,]

        # the +1 is because we get the prob vector for the first step above
        for step in range(start_step+1, loop_limit_step):
            mat = self.transition_matrix[step, :,:,]
            prob_vector = scipy.dot(prob_vector, mat)
            history_list.append(prob_vector[stop_state_index])

        if wrap:
            print "wrap"
            for step in range(0, stop_step):
                mat = self.transition_matrix[step, :,:,]
                prob_vector = scipy.dot(prob_vector, mat)
                history_list.append(prob_vector[stop_state_index])

        print "Prob vector: --->", prob_vector
        return (history_list, prob_vector)


    def get_state_number(self, state):
        """Given a state return an index for that state"""
        if state not in self.state_map:
            self.state_map[state] = self.state_count
            self.state_count = self.state_count+1

        return self.state_map[state]

    def get_step_info(self, step_num):
        steps_per_day = int((24.0 * 60.0) / self.minutes_in_step)

        day_num = step_num  / steps_per_day
        
        remaining_steps = step_num % steps_per_day
        hour_num = remaining_steps / 4

        minute_num = (remaining_steps % 4) * 15

        return "day %d, %d:%d" % ( day_num, hour_num, minute_num )
        
        
        

    def get_max_step(self):
        """given the number of minutes in a step
        Figure out the largest step index"""

        
        max_step = (24.0 * 60.0 * 7.0) / self.minutes_in_step

        return int(max_step)
    
    def get_step_number(self, time_date):
        """given a time return an step index for that time"""
        
        # 0 is monday 4 friday, 5 sat, 6 sun 
        day_of_week = time_date.weekday()

        steps_per_day = (24.0 * 60.0 ) / self.minutes_in_step
        
        minutes_past_midnight = time_date.hour*60. + time_date.minute + \
            time_date.second / 60.
        
        step_num = day_of_week * steps_per_day 
        step_num += int(minutes_past_midnight / self.minutes_in_step)
        
        return int(step_num)




