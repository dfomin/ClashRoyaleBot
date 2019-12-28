from clan_war import ClanWar


class WarResult:
    def __init__(self, tag: str, clan_war: ClanWar):
        self.tag = tag
        self.clan_war = clan_war
        for i, standing in enumerate(self.clan_war.standings):
            if self.tag == standing.tag:
                self.standing = standing
                self.place = i + 1
                break
        else:
            raise Exception()

    def __str__(self):
        return f"place: {self.place}, "\
               f"wins: {self.standing.wins}, "\
               f"battles: {self.standing.battles_played}, "\
               f"cards: {self.cards_collected()}"

    def cards_collected(self) -> int:
        cards = 0
        for participation in self.clan_war.participations.values():
            cards += participation.cards
        return cards
