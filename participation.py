from presenter import Presenter


class Participation:
    def __init__(self, json):
        self.tag = json["tag"]
        self.name = json["name"]
        self.day_1_battles_played = json["collectionDayBattlesPlayed"]
        self.day_1_battles = 3
        self.cards = json["cardsEarned"]
        self.day_2_battles_played = json["battlesPlayed"]
        self.day_2_battles = json["numberOfBattles"]
        self.wins = json["wins"]

    def __str__(self):
        result = ""
        need_parentheses = self.day_2_battles > 1

        if need_parentheses:
            result += "("

        for i in range(self.wins):
            result += Presenter.win()

        for i in range(self.day_2_battles_played - self.wins):
            result += Presenter.lose()

        for i in range(self.day_2_battles - self.day_2_battles_played):
            result += Presenter.skip()

        if need_parentheses:
            result += ")"

        return result
