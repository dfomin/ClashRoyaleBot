from participation import Participation


class ClanWar:
    def __init__(self, json):
        self.season_id = json["seasonId"]
        self.date = json["createdDate"]
        self.participations = {}
        for participant in json["participants"]:
            participation = Participation(participant)
            self.participations[participation.tag] = participation

    def __eq__(self, other):
        # TODO: check standing as well, two different clan wars could have the same date but different clans
        return self.date == other.date

    def __hash__(self):
        return hash(self.date)
