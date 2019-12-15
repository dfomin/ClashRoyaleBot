import numpy as np
from clan_war_result import ClanWarResult

class Selector:
    def __init__(self, cw_results: list, threshold):
        names = []
        probs = []
        for result in cw_results:
            if result.wins() >= threshold:
                names.append(result.name)

                prob = 2 ** (result.wins() - threshold)
                probs.append(prob)
        probs /= np.sum(probs)
        self.names_probs = sorted(zip(names, probs), key=lambda x: x[1], reverse=True)

    def select(self, count, verbose=False):
        if verbose:
            for name, prob in self.names_probs:
                print(name, str(round(prob * 100, 1)) + "%")

        names = [x[0] for x in self.names_probs]
        probs = [x[1] for x in self.names_probs]
        return np.random.choice(names, size=count, replace=False, p=probs)
