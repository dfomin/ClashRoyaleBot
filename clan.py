from clan_war import ClanWar
from member import Member


class Clan:
    def __init__(self, clan_info, clan_war_info):
        if clan_info:
            self.tag = clan_info["tag"]
            self.name = clan_info["name"]
            self.members = {}
            for member_json in clan_info["memberList"]:
                member = Member(member_json)
                self.members[member.tag] = member

        if clan_war_info:
            self.clan_wars = {}
            for item in clan_war_info["items"]:
                clan_war = ClanWar(item)
                self.clan_wars[clan_war.date] = clan_war
