from clan_war import ClanWar


class Clan:
    def __init__(self, clan_info, clan_war_info):
        self.clan_wars = {}
        for item in clan_war_info["items"]:
            clan_war = ClanWar(item)
            self.clan_wars[clan_war.date] = clan_war