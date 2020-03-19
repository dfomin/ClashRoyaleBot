import requests
from clan import Clan
from private import royaleToken


class ServerManager:
    @staticmethod
    def get_clan_info(self, tag: str) -> Clan:
        tag = tag.replace("#", "")

        clan = ServerManager.download_clan_info(tag)
        clan_war = ServerManager.download_clan_war_info(tag)

        return Clan(clan, clan_war)

    @staticmethod
    def download_clan_info(tag: str):
        params = dict(
            authorization=royaleToken
        )

        r = requests.get(url="https://api.clashroyale.com/v1/clans/%23" + tag, params=params)
        clan_info = r.json()
        return clan_info

    @staticmethod
    def download_clan_war_info(tag: str):
        params = dict(
            authorization=royaleToken
        )

        r = requests.get(url="https://api.clashroyale.com/v1/clans/%23" + tag + "/warlog", params=params)
        clan_war_info = r.json()
        return clan_war_info
