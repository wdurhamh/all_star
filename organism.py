
class Organism:
    
    def __init__(self, lr, moment, struct):
        self.rate = lr
        self.momentum = moment
        self.structure = struct

    def set_score(self, score):
        self.score = score
