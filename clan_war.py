from participation import Participation


class ClanWar:
    def __init__(self, json):
        self.season_id = json["seasonId"]
        self.date = json["createdDate"]
        self.participations = {}
        for participant in json["participants"]:
            participation = Participation(participant)
            self.participations[participation.tag] = participation
