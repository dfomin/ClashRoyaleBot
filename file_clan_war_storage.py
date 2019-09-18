from pathlib import Path
from clan_war_storage import ClanWarStorage
from clan_war import ClanWar
from clan import Clan
import json


class FileClanWarStorage(ClanWarStorage):
    def __init__(self, dir_path):
        self.clan_wars = set()
        for path in dir_path.iterdir():
            if path.suffix == ".json":
                with path.open() as input_file:
                    clan_war_info = json.load(input_file)
                    clan = Clan(None, clan_war_info)
                    for date, clan_war in clan.clan_wars.items():
                        self.clan_wars.add(clan_war)

    def get_clan_wars(self):
        return self.clan_wars
