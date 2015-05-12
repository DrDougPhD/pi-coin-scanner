class TrinaryState:
  def __init__(self, init_state=0):
    self.state = init_state

  def transition_to_next_state(self):
    self.state = (self.state+1) % 3

  def is_initial_state(self):
    return (self.state == 0)

  def is_middle_state(self):
    return (self.state == 1)

  def is_ending_state(self):
    return (self.state == 2)

