from clan_war_result import ClanWarResult
from clan import Clan
from war_result import WarResult


class ClanWarManager:
    def __init__(self, clan: Clan):
        self.clan = clan

    def get_clan_war_result(self) -> list:
        results = []
        members_tags = self.clan.members.keys()
        for tag in members_tags:
            results.append(self.get_member_clan_war_result(tag))
        return list(map(str, sorted(results)))

    def get_clan_war_result_history(self) -> list:
        results = []
        members_tags = set()
        for dict_keys in map(lambda x: x.participations.keys(), self.clan.clan_wars.values()):
            members_tags.update(dict_keys)
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
        name = self.clan.members[tag].name if tag in self.clan.members else tag
        return ClanWarResult(tag, name, result)

    def get_war_results(self):
        results = []
        for clan_war in self.clan.clan_wars.values():
            results.append(WarResult(self.clan.tag, clan_war))
        return results
