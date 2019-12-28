from telegram.ext import Updater, Filters, CommandHandler
from collections import defaultdict
import requests
from requests_html import HTMLSession
import sys
from datetime import datetime

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

token = ''

about_text = '''This is free open source telegram bot for clash royale statistics.
You can contribute here https://github.com/dfomin/ClashRoyaleBot.
You can text me in telegram @dfomin'''

help_text = '''Bot shows statistics of the last 10 clan wars for all clan members.
It's impossible to get information more than 10 clan wars because supercell stores only 10 last.

/clanwar <clan tag> ('/clanwar 2UJ2GJ') shows clan members:
<player nick> <percentage of wins (final battle) in last 10 clan wars> <result for each clan war battle>
Result is shown as:
x - player didn't participate in the clan war
_ - player participated in collection day but skipped final battle
0 - player lost final battle
1 - player won final battle
(00) or (01) or (11) - player had 2 battles, 2 results for each battle.
This command has a few variations:
/clanwarece - the same as clanwar, but the skip of final battle is considered as defeat.
/clanwarecelastseason - the same as clanwarece, but only clan wars in the current season counts (it could be from 1 to 7).

/skips <clan tag> ('/skips 2UJ2GJ') shows statistics about missed battles in collection day and final battle of the last 10 clan wars.

/cwfilter <clan tag> <win streak> <wins> <skips1> <skips2> <role (optional)> ('/cwfilter 2UJ2GJ 2 5 1 0') filters players with given role (or all if skipped) who has at least <win streak> wins in a row or at least <wins> in last 10 clan wars and not more than <skips1> skips in collection day and not more than <skips2> skips in war day. role can be: member|elder|coLeader|leader.

/lastseen <clan tag> <days count> ('/lastseen 2UJ2GJ 2') shows players who were not online more than <days count> days.

/clanstat <clan tag> ('/clanstat 2UJ2GJ') shows results of the clan for last 10 clan wars (useful to estimate averate skill of the clan):
<result place in clan war> <percentage of wins in the clan war>

/winstreak <clan tag> ('/winstreak 2UJ2GJ') shows clan members sorted by current win streak in the last 10 clan wars.
/maxwinstreak <clan tag> ('/maxwinstreak 2UJ2GJ') shows clan members sorted by max win streak in the last 10 clan wars.

/collectiondayskip <clan tag> ('/collectiondayskip 2UJ2GJ') shows players who participated but didn't play all games in collection day in the last 10 clan wars:
<player nick> <amount of collection day battles>, 0 - didn't participate, 3 - played all battles, 1 or 2 - didn't play all battles.
'''

help_text_ru = '''Бот выводит статистику всех игроков клана по 10 последним клановым войнам.
Получить статистику больше, чем по 10 кв нельзя, так как supercell хранит только 10 последних.

/clanwar <тэг клана> (например, '/clanwar 2UJ2GJ') выводит список игроков в виде:
<ник игрока> <процент побед в 10 последних кв> <результат для каждой кв>
Результат отображается так:
x - игрок не участвовал
_ - игрок сыграл первый день и не провел финальную атаку
0 - игрок проиграл финальный бой
1 - игрок выиграл финальный бой
(00) или (01) или (11) - игрок имел 2 боя, в скобочках написаны результаты этих боёв.
Эта команда имеет несколько разновидностей:
/clanwarece - выводит ту же информацию что и clanwar, но в подсчёте процента побед пропуск войны равносилен поражению в финальной битве.
/clanwarecelastseason - то же самое, что и clanwarece, но учитывает только войны в последнем сезоне (их может быть от 1 до 7).

/skips <тэг клана> (например, '/skips 2UJ2GJ') выводит статистику по пропуску дней сбора и финальных битв за последние 10 кв.

/cwfilter <clan tag> <win streak> <skips1> <skips2> <wins> <role (опционально)> ('/cwfilter 2UJ2GJ 2 5') выводит игроков с данной ролью (или всех, если она не указана), у которых как минимум <win streak> побед подряд или как минимум <wins> побед в последних 10 клановых войнах при этом не более <skips1> и <skips2> пропусков в первый и второй дни войны. role может быть: member|elder|coLeader|leader.

/lastseen <clan tag> <days count> ('/lastseen 2UJ2GJ 2') выводит игроков которые не были онлайн в игре >= полных <days count> дней.

/clanstat <тэг клана> (например, '/clanstat 2UJ2GJ') выводит статистику клана за 10 последних кв (удобно для оценки уровня клана соперника):
<место которое занял клан> <процент побед в финальной битве в этой войне>

/winstreak <тэг клана> (например, '/winstreak 2UJ2GJ') выводит игроков, отсортированных по текущему количеству побед подряд в 10 последних кв.
/maxwinstreak <тэг клана> (например, '/maxwinstreak 2UJ2GJ') выводит игроков, отсортированных по максимальному количеству побед подряд в 10 последних кв.

/collectiondayskip <тэг клана> (например, '/collectiondayskip 2UJ2GJ') выводит игроков которые не доигрывали день сбора в 10 последних кв:
<ник игрока> <количество боев в день сбора>, 0 - пропуск кв, 3 - сыграл все бои, 1 или 2 - не доиграл день сбора.
'''


def escape(s):
    return s.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')


def load_clan_members(clan_tag):
    params = dict(
        authorization=royaleToken
    )

    r = requests.get(url='https://api.clashroyale.com/v1/clans/%23' + clan_tag, params=params)

    result = {}
    clan_info = r.json()
    member_list = clan_info['memberList']
    for member in member_list:
        result[member['tag']] = member['name']

    return result


def load_clan_role(clan_tag):
    params = dict(
        authorization=royaleToken
    )

    r = requests.get(url='https://api.clashroyale.com/v1/clans/%23' + clan_tag, params=params)

    result = {}
    clan_info = r.json()
    member_list = clan_info['memberList']
    for member in member_list:
        result[member['tag']] = member['role']

    return result


def load_clan_war_skips_info(clan_tag):
    clan_war_info = {}
    clan_members = load_clan_members(clan_tag)
    for tag in clan_members.keys():
        clan_war_info[tag] = []

    params = dict(
        authorization=royaleToken
    )

    r = requests.get(url='https://api.clashroyale.com/v1/clans/%23' + clan_tag + '/warlog', params=params)

    all_data = r.json()

    result = ""
    for item in reversed(all_data['items']):
        result += 'day 1: '
        participants = item['participants']
        line = []
        for participant in participants:
            if participant['tag'] in clan_members:
                if participant['collectionDayBattlesPlayed'] == 1 or participant['collectionDayBattlesPlayed'] == 2:
                    line.append(clan_members[participant['tag']] + '(' + str(participant['collectionDayBattlesPlayed']) + '/3)')
        result += ", ".join(line) + '\n'
        result += 'day 2: '
        line = []
        for participant in participants:
            if participant['tag'] in clan_members:
                if participant['battlesPlayed'] == 0:
                    line.append(clan_members[participant['tag']])
        result += ", ".join(line) + '\n'
    return result


def load_player_clan_war_win_rate(tag):
    params = dict(
        authorization=royaleToken
    )

    tag = tag.replace('#', '')
    r = requests.get(url='https://api.clashroyale.com/v1/players/%23' + tag, params=params)

    player_info = r.json()
    wins = player_info['warDayWins']
    cards = player_info['clanCardsCollected']
    return player_info['name'] + ' ' + str(wins) + ' ' + str(round(cards / wins))


def load_clan_war_info_raw(clan_tag, skip_as_lose, last_season):
    clan_war_info = {}
    clan_members = load_clan_members(clan_tag)
    for tag in clan_members.keys():
        clan_war_info[tag] = []

    params = dict(
        authorization=royaleToken
    )

    r = requests.get(url='https://api.clashroyale.com/v1/clans/%23' + clan_tag + '/warlog', params=params)

    all_data = r.json()

    last_season_id = -1
    if last_season and len(all_data['items']) > 0:
        last_season_id = all_data['items'][0]['seasonId']

    for item in reversed(all_data['items']):
        if last_season and item['seasonId'] != last_season_id:
            continue

        participants = item['participants']
        for player_tag in clan_members.keys():
            participant = next((x for x in participants if x['tag'] == player_tag), None)
            clan_war_info[player_tag].append(participant)
    return clan_war_info


def load_clan_war_info(clan_tag, skip_as_lose, last_season):
    clan_members = load_clan_members(clan_tag)
    clan_war_info = load_clan_war_info_raw(clan_tag, skip_as_lose, last_season)
    sorted_players = []
    for tag, participants in clan_war_info.items():
        wins = 0
        battles = 0
        win_rate = 0
        plays = ""

        for participant in participants:
            if participant is not None:
                wins += participant['wins']
                battles += participant['numberOfBattles'] if skip_as_lose else participant['battlesPlayed']

                if participant['numberOfBattles'] < 2:
                    plays += "1" if participant['wins'] > 0 else "0" if participant['battlesPlayed'] > 0 else "_"
                else:
                    plays += "("
                    for war_battle in range(participant['battlesPlayed']):
                        plays += "1" if war_battle < participant['wins'] else "0"
                    for war_battle in range(participant['battlesPlayed'], participant['numberOfBattles']):
                        plays += "_"
                    plays += ")"
            else:
                plays += "x"

                if skip_as_lose:
                    battles += 1

        if battles > 0:
            win_rate = wins / battles
        win_rate = int(100 * win_rate)

        sorted_players.append((clan_members[tag], win_rate, plays, battles))

    sorted_players.sort(key=lambda x: (x[1], x[3]), reverse=True)

    result = []
    for player in sorted_players:
        result.append((player[0] + " " + str(player[1]) + "% " + player[2]))

    return result


def load_card_collection_info_raw(clan_tag):
    card_collection_info = {}
    clan_members = load_clan_members(clan_tag)
    for tag in clan_members.keys():
        card_collection_info[tag] = []

    params = dict(
        authorization=royaleToken
    )

    r = requests.get(url='https://api.clashroyale.com/v1/clans/%23' + clan_tag + '/warlog', params=params)

    all_data = r.json()

    for item in reversed(all_data['items']):
        participants = item['participants']
        for player_tag in clan_members.keys():
            participant = next((x for x in participants if x['tag'] == player_tag), None)
            if participant is not None:
                card_collection_info[player_tag].append(participant['collectionDayBattlesPlayed'])
            else:
                card_collection_info[player_tag].append(0)
    return card_collection_info


def load_card_collection_info(clan_tag):
    clan_members = load_clan_members(clan_tag)
    card_collection_info = load_card_collection_info_raw(clan_tag)

    answer = ""
    for tag, info in card_collection_info.items():
        for battles in info:
            if battles != 3 and battles != 0:
                answer += clan_members[tag] + ' '
                for battlesCount in info:
                    answer += str(battlesCount)
                answer += '\n'
                break

    return answer


def load_clan_war_standing(clan_tag):
    params = dict(
        authorization=royaleToken
    )

    r = requests.get(url='https://api.clashroyale.com/v1/clans/%23' + clan_tag + '/warlog', params=params)

    all_data = r.json()

    result = []
    for item in all_data['items']:
        for index, standing in enumerate(item['standings']):
            clan = standing['clan']
            if '#' + clan_tag == clan['tag']:
                result.append((index + 1, clan['wins'], clan['battlesPlayed'], clan['crowns'], clan['wins'] / clan['battlesPlayed']))
    return result


def load_win_streak_info(clan_tag):
    clan_members = load_clan_members(clan_tag)
    max_win_streak = dict.fromkeys(clan_members, 0)
    current_win_streak = dict.fromkeys(clan_members, 0)

    params = dict(
        authorization=royaleToken
    )

    r = requests.get(url='https://api.clashroyale.com/v1/clans/%23' + clan_tag + '/warlog', params=params)

    all_data = r.json()
    for item in all_data['items']:
        participants = item['participants']
        for participant in participants:
            player_tag = participant['tag']
            if player_tag in clan_members:
                current_win_streak[player_tag] += participant['wins']
                if participant['wins'] < participant['battlesPlayed']:
                    if max_win_streak[player_tag] < current_win_streak[player_tag]:
                        max_win_streak[player_tag] = current_win_streak[player_tag]
                    current_win_streak[player_tag] = participant['wins']

    for player_tag in clan_members:
        if max_win_streak[player_tag] < current_win_streak[player_tag]:
            max_win_streak[player_tag] = current_win_streak[player_tag]

    sorted_players = []
    for player_tag in clan_members:
        sorted_players.append((player_tag, max_win_streak[player_tag]))
    sorted_players.sort(key=lambda x: x[1], reverse=True)

    current_win_streak = sorted_players[0][1]
    answer = str(current_win_streak) + '\n'
    for player in sorted_players:
        if current_win_streak != player[1]:
            current_win_streak = player[1]
            answer += '\n' + str(current_win_streak) + '\n'
        answer += clan_members[player[0]] + '\n'
    return answer


def load_current_win_streak_info(clan_tag):
    clan_members = load_clan_members(clan_tag)
    current_win_streak = dict.fromkeys(clan_members, 0)
    processed_members = []

    params = dict(
        authorization=royaleToken
    )

    r = requests.get(url='https://api.clashroyale.com/v1/clans/%23' + clan_tag + '/warlog', params=params)

    all_data = r.json()
    for item in all_data['items']:
        participants = item['participants']
        for participant in participants:
            player_tag = participant['tag']
            if player_tag in clan_members and player_tag not in processed_members:
                current_win_streak[player_tag] += participant['wins']
                if participant['wins'] < participant['battlesPlayed']:
                    processed_members.append(player_tag)

    sorted_players = []
    for player_tag in clan_members:
        sorted_players.append((player_tag, current_win_streak[player_tag]))
    sorted_players.sort(key=lambda x: x[1], reverse=True)

    win_streak = sorted_players[0][1]
    answer = str(win_streak) + '\n'
    for player in sorted_players:
        if win_streak != player[1]:
            win_streak = player[1]
            answer += '\n' + str(win_streak) + '\n'
        answer += clan_members[player[0]] + '\n'
    return answer


def load_clan_war_filter(clan_tag, win_streak, last_ten, first_day_skips, second_day_skips, role):
    clan_members = load_clan_members(clan_tag)
    clan_roles = load_clan_role(clan_tag)
    max_win_streak = dict.fromkeys(clan_members, 0)
    current_win_streak = dict.fromkeys(clan_members, 0)
    max_first_day_skips = dict.fromkeys(clan_members, 0)
    max_second_day_skips = dict.fromkeys(clan_members, 0)
    last_ten_result = defaultdict(list)

    params = dict(
        authorization=royaleToken
    )

    r = requests.get(url='https://api.clashroyale.com/v1/clans/%23' + clan_tag + '/warlog', params=params)

    all_data = r.json()
    for item in all_data['items']:
        participants = item['participants']
        for participant in participants:
            player_tag = participant['tag']
            if player_tag in clan_members:
                current_win_streak[player_tag] += participant['wins']
                if participant['wins'] < participant['battlesPlayed']:
                    if max_win_streak[player_tag] < current_win_streak[player_tag]:
                        max_win_streak[player_tag] = current_win_streak[player_tag]
                    current_win_streak[player_tag] = participant['wins']

                loses = participant['battlesPlayed'] - participant['wins']
                wins = participant['wins']
                for i in range(loses):
                    last_ten_result[player_tag].append(0)

                for i in range(wins):
                    last_ten_result[player_tag].append(1)

    for player_tag in clan_members:
        if max_win_streak[player_tag] < current_win_streak[player_tag]:
            max_win_streak[player_tag] = current_win_streak[player_tag]

    for item in all_data['items']:
        participants = item['participants']
        for participant in participants:
            player_tag = participant['tag']
            if player_tag in clan_members:
                max_first_day_skips[player_tag] += 3 - participant['collectionDayBattlesPlayed']
                if participant['battlesPlayed'] == 0:
                    max_second_day_skips[player_tag] += 1

    result = ""
    for player_tag in clan_members:
        if len(last_ten_result[player_tag]) > 10:
            player_last_ten = sum(last_ten_result[player_tag][-10:])
        else:
            player_last_ten = sum(last_ten_result[player_tag])
        if (len(role) == 0 or clan_roles[player_tag] == role) and \
                (max_win_streak[player_tag] >= win_streak or player_last_ten >= last_ten) \
                and max_first_day_skips[player_tag] <= first_day_skips \
                and max_second_day_skips[player_tag] <= second_day_skips:
            result += clan_members[player_tag] + " " + str(max_win_streak[player_tag]) + " " + str(
                player_last_ten) + " " + str(max_first_day_skips[player_tag]) + " " + str(
                max_second_day_skips[player_tag]) + " " + clan_roles[player_tag] + "\n"
    return result


def get_stat(tag):
    standings = load_clan_war_standing(tag)
    battles = 0
    wins = 0
    answer = ""
    for standing in standings:
        battles += standing[2]
        wins += standing[1]
        answer += str(standing[0]) + ' ' + str(round(100 * standing[4])) + '%\n'
    answer += str(round(100 * wins / battles)) + '%'
    return answer


def get_tag(args):
    if len(args) != 1:
        return None

    tag = args[0]
    tag = tag.replace('#', '').upper()
    return tag


def clan_last_seen_members(clan_tag, days):
    params = dict(
        authorization=royaleToken
    )

    r = requests.get(url='https://api.clashroyale.com/v1/clans/%23' + clan_tag, params=params)
    print(r)
    result = {}
    clan_info = r.json()

    member_list = clan_info['memberList']
    for member in member_list:
        last_seen_time = member['lastSeen']
        delta_time_last_seen = datetime.utcnow() - datetime.strptime(last_seen_time, "%Y%m%dT%H%M%S.%fZ")
        if delta_time_last_seen.days >= days:
            result[member['name']] = delta_time_last_seen.days

    return result


def clan_war(bot, update, args):
    tag = get_tag(args)
    if tag is None:
        bot.send_message(update.message.chat.id, 'Invalid clan tag')
        return
    
    clan_war_info = load_clan_war_info(tag, False, False)
    answer = ""
    for info in clan_war_info:
        answer += info + "\n"

    bot.send_message(update.message.chat.id, '<pre>' + escape(answer) + '</pre>', parse_mode="HTML")


def clan_war_ece(bot, update, args):
    tag = get_tag(args)
    if tag is None:
        bot.send_message(update.message.chat.id, 'Invalid clan tag')
        return

    clan_war_info = load_clan_war_info(tag, True, False)
    answer = ""
    for info in clan_war_info:
        answer += info + "\n"

    bot.send_message(update.message.chat.id, '<pre>' + escape(answer) + '</pre>', parse_mode="HTML")


def clan_war_ece_last_season(bot, update, args):
    tag = get_tag(args)
    if tag is None:
        bot.send_message(update.message.chat.id, 'Invalid clan tag')
        return

    clan_war_info = load_clan_war_info(tag, True, True)
    answer = ""
    for info in clan_war_info:
        answer += info + "\n"

    bot.send_message(update.message.chat.id, '<pre>' + escape(answer) + '</pre>', parse_mode="HTML")


def clan_skips(bot, update, args):
    tag = get_tag(args)
    if tag is None:
        bot.send_message(update.message.chat.id, 'Invalid clan tag')
        return

    answer = load_clan_war_skips_info(tag)

    bot.send_message(update.message.chat.id, '<pre>' + escape(answer) + '</pre>', parse_mode="HTML")


def cwfilter(bot, update, args):
    if len(args) != 5 and len(args) != 6:
        bot.send_message(update.message.chat.id, 'Invalid arguments')
        return

    tag = args[0]
    tag = tag.replace('#', '').upper()
    win_streak = int(args[1])
    last_ten = int(args[2])
    first_day_skips = int(args[3])
    second_day_skips = int(args[4])
    role = args[5] if len(args) == 6 else ''

    answer = load_clan_war_filter(tag, win_streak, last_ten, first_day_skips, second_day_skips, role)
    if len(answer) == 0:
        answer = "∅"

    bot.send_message(update.message.chat.id, '<pre>' + escape(answer) + '</pre>', parse_mode="HTML")


def last_seen(bot, update, args):
    if len(args) != 2:
        bot.send_message(update.message.chat.id, 'Invalid arguments')
        return

    tag = args[0]
    tag = tag.replace('#', '').upper()
    days = int(args[1])

    answer = ""
    members = clan_last_seen_members(tag, days)
    if len(members) == 0:
        answer = "∅"
    else:
        sorted_members = sorted(members.items(), key=lambda x: -x[1])
        for info in sorted_members:
            answer += info[0] + ": " + str(info[1]) + "\n"

    bot.send_message(update.message.chat.id, '<pre>' + escape(answer) + '</pre>', parse_mode="HTML")


def clan_stat(bot, update, args):
    tag = get_tag(args)
    if tag is None:
        bot.send_message(update.message.chat.id, 'Invalid clan tag')
        return

    answer = get_stat(tag)

    bot.send_message(update.message.chat.id, '<pre>' + escape(answer) + '</pre>', parse_mode="HTML")


def max_win_streak(bot, update, args):
    tag = get_tag(args)
    if tag is None:
        bot.send_message(update.message.chat.id, 'Invalid clan tag')
        return

    answer = load_win_streak_info(tag)

    bot.send_message(update.message.chat.id, '<pre>' + escape(answer) + '</pre>', parse_mode="HTML")


def current_win_streak(bot, update, args):
    tag = get_tag(args)
    if tag is None:
        bot.send_message(update.message.chat.id, 'Invalid clan tag')
        return

    answer = load_current_win_streak_info(tag)

    bot.send_message(update.message.chat.id, '<pre>' + escape(answer) + '</pre>', parse_mode="HTML")


def card_collection(bot, update, args):
    tag = get_tag(args)
    if tag is None:
        bot.send_message(update.message.chat.id, 'Invalid clan tag')
        return

    answer = load_card_collection_info(tag)
    if len(answer) == 0:
        answer = "No one skips collection day."

    bot.send_message(update.message.chat.id, '<pre>' + escape(answer) + '</pre>', parse_mode="HTML")


def player_clan_war_stat(bot, update, args):
    tag = get_tag(args)
    if tag is None:
        bot.send_message(update.message.chat.id, 'Invalid clan tag')
        return

    answer = load_player_clan_war_win_rate(tag)

    bot.send_message(update.message.chat.id, '<pre>' + escape(answer) + '</pre>', parse_mode="HTML")


def load_player_clan_war_history(player_tag, count):
    params = dict(
        authorization=royaleApiToken
    )

    session = HTMLSession()
    r = session.get(url="https://royaleapi.com/inc/player/cw_history?player_tag=" + player_tag, params=params)
    a = r.html.xpath('a')
    results = list(map(lambda x: x.text.split('\n')[0], a))
    results = results if count <= 0 else results[:count]
    results = list(reversed(results))
    log = ""
    for i in range(len(results)):
        wins, battles = results[i].split(' / ')
        if battles == '1':
            log += wins
        else:
            log += "("
            for i in range(int(wins)):
                log += "1"
            for i in range(int(battles) - int(wins)):
                log += "0"
            log += ")"

    return log


def clan_war_history(bot, update, args):
    tag = get_tag(args)
    if tag is None:
        bot.send_message(update.message.chat.id, 'Invalid clan tag')
        return

    answer = load_player_clan_war_history(tag, count)

    bot.send_message(update.message.chat.id, '<pre>' + escape(answer) + '</pre>', parse_mode="HTML")


def about(bot, update):
    bot.send_message(update.message.chat.id, about_text)


def start(bot, update):
    bot.send_message(45227519, str(update.message.chat.id))
    bot.send_message(update.message.chat.id, 'Hello, try /help or /help_ru')


def help(bot, update):
    bot.send_message(update.message.chat.id, help_text)


def help_ru(bot, update):
    bot.send_message(update.message.chat.id, help_text_ru)


# def main():
    # updater = Updater(token)
    # updater.start_webhook(listen='127.0.0.1', port=5000, url_path=token)
    # updater.bot.set_webhook(url='https://pigowl.com:443/' + token)
    #
    # dp = updater.dispatcher
    #
    # dp.add_handler(CommandHandler("start", start))
    # dp.add_handler(CommandHandler("help", help))
    # dp.add_handler(CommandHandler("help_ru", help_ru))
    # dp.add_handler(CommandHandler("about", about))
    # dp.add_handler(CommandHandler("clanwar", clan_war, pass_args=True))
    # dp.add_handler(CommandHandler("clanwarece", clan_war_ece, pass_args=True))
    # dp.add_handler(CommandHandler("clanwarecelastseason", clan_war_ece_last_season, pass_args=True))
    # dp.add_handler(CommandHandler("skips", clan_skips, pass_args=True))
    # dp.add_handler(CommandHandler("cwfilter", cwfilter, pass_args=True))
    # dp.add_handler(CommandHandler("lastseen", last_seen, pass_args=True))
    # dp.add_handler(CommandHandler("clanstat", clan_stat, pass_args=True))
    # dp.add_handler(CommandHandler("maxwinstreak", max_win_streak, pass_args=True))
    # dp.add_handler(CommandHandler("winstreak", current_win_streak, pass_args=True))
    # dp.add_handler(CommandHandler("collectiondayskip", card_collection, pass_args=True))
    # dp.add_handler(CommandHandler("playercwstat", player_clan_war_stat, pass_args=True))
    #
    # updater.idle()

    # answer = load_clan_war_info('2UJ2GJ', False, False)
    # print(answer)
    # answer = get_stat('2UJ2GJ')
    # print(answer)
    # answer = load_player_clan_war_win_rate('8RQVRJUC')
    # print(answer)
    # answer = load_current_win_streak_info('2UJ2GJ')
    # print(answer)
    # answer = load_card_collection_info('2UJ2GJ')
    # print(answer)
    # answer = load_clan_war_info('2UJ2GJ', False, False)
    # print(answer)
    # answer = load_player_clan_war_history('8RQVRJUC', 10)
    # print(answer)
    # answer = load_clan_war_skips_info('2UJ2GJ')
    # print(answer)
    # answer = load_clan_war_filter('2UJ2GJ', 3, 5, 2, 0, 'member')
    # print(answer)
    # answer = clan_last_seen_members('2UJ2GJ', 0)
    # print(answer)


from server_manager import ServerManager
from clan_war_manager import ClanWarManager
from file_clan_war_storage import FileClanWarStorage
from clan import Clan
from pathlib import Path
from selector import Selector

if __name__ == "__main__":
    #main()

    storage = FileClanWarStorage(Path("/Users/dfomin/Downloads/cw/"))
    # clan_wars_info = list(filter(lambda x: x.date > "20191104T130358.000Z", storage.get_clan_wars()))
    clan_wars_info = storage.get_clan_wars()
    clan_wars = {x.date: x for x in clan_wars_info}

    print(len(clan_wars_info))

    server_manager = ServerManager()
    clan = server_manager.get_clan_info("#2UJ2GJ")

    clan.clan_wars = clan_wars

    cw_manager = ClanWarManager(clan)

    # leaders = list(map(lambda x: x.name, filter(lambda x: x.role in ['leader', 'coLeader'], clan.members.values())))
    # print("Соруки и лидер не участвуют в розыгрыше: " + ", ".join(leaders))
    #
    # banned = []
    # for tag, member in clan.members.items():
    #     cw_result = cw_manager.get_member_clan_war_result(tag)
    #     if cw_result.day_1_skips() or cw_result.day_2_skips():
    #         banned.append(cw_result.name)
    # print("Не доигравшие сбор или пропустившие финальную атаку не участвуют в розыгрыше: " + ", ".join(banned))

    # winners = []
    # results = []
    # for tag, member in clan.members.items():
    #     role = member.role
    #     cw_result = cw_manager.get_member_clan_war_result(tag)
    #     # if role not in ["leader", "coLeader"] and not cw_result.day_1_skips() and not cw_result.day_2_skips() and cw_result.name not in winners:
    #     results.append(cw_result)

    # results = sorted(results)
    # for result in results:
    #     print(result)

    for result in cw_manager.get_war_results():
        print(result)

    # selector = Selector(results, 7)
    # winner = selector.select(1, verbose=True)
    # print()
    # print("Победитель: " + ", ".join(winner))
