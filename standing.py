class Standing:
    def __init__(self, json):
        self.tag = json["tag"]
        self.name = json["name"]
        self.clan_score = json["clanScore"]
        self.participants = json["participants"]
        self.battles_played = json["battlesPlayed"]
        self.wins = json["wins"]
        self.crowns = json["crowns"]
