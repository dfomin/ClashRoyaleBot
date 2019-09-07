from clan_war_result import ClanWarResult
from clan import Clan


class ClanWarManager:
    def __init__(self, clan: Clan):
        self.clan = clan

    def get_clan_war_result(self) -> list:
        results = []
        members_tags = self.clan.members.keys()
        for tag in members_tags:
            results.append(self.get_member_clan_war_result(tag))
        return list(map(str, sorted(results)))

    def get_member_clan_war_result(self, tag: str) -> ClanWarResult:
        result = []
        dates = sorted(self.clan.clan_wars.keys())
        for date in dates:
            clan_war = self.clan.clan_wars[date]
            if tag in clan_war.participations:
                result.append(clan_war.participations[tag])
            else:
                result.append(None)
        return ClanWarResult(tag, self.clan.members[tag].name, result)
