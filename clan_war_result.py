from presenter import Presenter


class ClanWarResult:
    def __init__(self, tag: str, name: str, participations: list):
        self.tag = tag
        self.name = name
        self.participations = participations

    def __str__(self):
        result = self.name + " "
        result += str(round(self.win_rate() * 100)) + "% "
        for participation in self.participations:
            if participation is not None:
                result += str(participation)
            else:
                result += Presenter.absense()
        return result

    def __lt__(self, other):
        if self.win_rate() > other.win_rate():
            return True
        elif self.win_rate() < other.win_rate():
            return False
        elif self.battles() > other.battles():
            return True
        elif self.battles() < other.battles():
            return False
        else:
            return False

    def win_rate(self, strict=False):
        wins = 0
        battles = 0
        for participation in self.participations:
            if participation is not None:
                wins += participation.wins
                battles += participation.day_2_battles
            elif strict:
                battles += 1
        if battles > 0:
            return wins / battles
        else:
            return 0

    def wins(self):
        wins = 0
        for participation in self.participations:
            if participation is not None:
                wins += participation.wins
        return wins

    def battles(self):
        battles = 0
        for participation in self.participations:
            if participation is not None:
                battles += participation.day_2_battles
        return battles

    def day_1_skips(self):
        for participation in self.participations:
            if participation and (participation.day_1_battles == 1 or participation.day_1_battles == 2):
                return True
        return False

    def day_2_skips(self):
        for participation in self.participations:
            if participation and (participation.day_2_battles_played < participation.day_2_battles):
                return True
        return False
