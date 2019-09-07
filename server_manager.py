import requests
from clan import Clan
from private import royaleToken


class ServerManager:
    def get_clan_info(self, tag):
        tag = tag.replace("#", "")

        clan = self.download_clan_info(tag)
        clan_war = self.download_clan_war_info(tag)

        return Clan(clan, clan_war)

    def download_clan_info(self, tag):
        params = dict(
            authorization=royaleToken
        )

        r = requests.get(url="https://api.clashroyale.com/v1/clans/%23" + tag, params=params)
        clan_info = r.json()
        return clan_info

    def download_clan_war_info(self, tag):
        params = dict(
            authorization=royaleToken
        )

        r = requests.get(url="https://api.clashroyale.com/v1/clans/%23" + tag + "/warlog", params=params)
        clan_war_info = r.json()
        return clan_war_info
