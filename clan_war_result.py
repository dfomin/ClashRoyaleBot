from presenter import Presenter


class ClanWarResult:
    def __init__(self, tag: str, name: str, participations: list):
        self.tag = tag
        self.name = name
        self.participations = participations

    def __str__(self):
        result = self.name + " "
        # result += str(round(self.win_rate() * 100)) + "% "
        # result += str(self.wins()) + " "
        result += str(self.win_streak()) + " "
        # result += str(self.battles()) + " "
        # result += str(self.cards_collected()) + " "
        # result += str(round(self.average_cards_collected())) + " "
        for participation in self.participations:
            if participation is not None:
                result += str(participation)
            else:
                result += Presenter.absense()
        return result

    def __lt__(self, other):
        # if self.wars() > other.wars():
        #     return True
        # elif self.wars() < other.wars():
        #     return False
        if self.win_streak() > other.win_streak():
            return True
        elif self.win_streak() < other.win_streak():
            return False
        # if self.wins() > other.wins():
        #     return True
        # elif self.wins() < other.wins():
        #     return False
        # if self.win_rate() > other.win_rate():
        #     return True
        # elif self.win_rate() < other.win_rate():
        #     return False
        # if self.cards_collected() > other.cards_collected():
        #     return True
        # if self.cards_collected() < other.cards_collected():
        #     return False
        # if self.average_cards_collected() > other.average_cards_collected():
        #     return True
        # if self.average_cards_collected() < other.average_cards_collected():
        #     return False
        if self.battles() < other.battles():
            return True
        elif self.battles() > other.battles():
            return False
        else:
            return False

    def win_rate(self, strict=False):
        wins = 0
        battles = 0
        for participation in self.participations:
            if participation is not None:
                wins += participation.wins
                battles += participation.day_2_battles
            elif strict:
                battles += 1
        if battles > 0:
            return wins / battles
        else:
            return 0

    def wins(self):
        wins = 0
        for participation in self.participations:
            if participation is not None:
                wins += participation.wins
        return wins

    def win_streak(self):
        max_win_streak = 0
        current_win_streak = 0
        for participation in self.participations:
            if participation is not None:
                if participation.wins < participation.day_2_battles:
                    current_win_streak += participation.wins
                    if current_win_streak > max_win_streak:
                        max_win_streak = current_win_streak
                    current_win_streak = participation.wins
                else:
                    current_win_streak += participation.wins

        if current_win_streak > max_win_streak:
            max_win_streak = current_win_streak

        return max_win_streak

    def battles(self):
        battles = 0
        for participation in self.participations:
            if participation is not None:
                battles += participation.day_2_battles
        return battles

    def wars(self):
        return len(list(filter(lambda x: x is not None, self.participations)))

    def cards_collected(self):
        cards = 0
        for participation in self.participations:
            if participation is not None:
                cards += participation.cards
        return cards

    def average_cards_collected(self):
        return self.cards_collected() / self.wars() if self.wars() > 0 else 0

    def day_1_skips(self):
        for participation in self.participations:
            if participation and (participation.day_1_battles_played == 1 or participation.day_1_battles_played == 2):
                return True
        return False

    def day_2_skips(self):
        for participation in self.participations:
            if participation and (participation.day_2_battles_played < participation.day_2_battles):
                return True
        return False
