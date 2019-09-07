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
