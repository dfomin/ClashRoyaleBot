from telegram.ext import Updater, Filters, CommandHandler
import requests
import sys

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

token = ''
royaleToken = ''

about_text = '''This is free open source telegram bot for clash royale statistics.
You can contribute here https://github.com/dfomin/ClashRoyaleBot.
You can text me in telegram @dfomin'''


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


def load_clan_war_info(clan_tag, skip_as_lose, last_season):
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

    sorted_players = []
    for tag, participants in clan_war_info.items():
        wins = 0
        battles = 0
        win_rate = 0
        plays = ""

        for participant in participants:
            if participant is not None:
                wins += participant['wins']
                battles += participant['battlesPlayed']

                if participant['battlesPlayed'] == 0 and skip_as_lose:
                    battles += 1

                if participant['battlesPlayed'] < 2:
                    plays += "1" if participant['wins'] > 0 else "0" if participant['battlesPlayed'] > 0 else "_"
                else:
                    plays += "("
                    for war_battle in range(participant['battlesPlayed']):
                        plays += "1" if war_battle < participant['wins'] else "0"
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


def load_card_collection_info(clan_tag):
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


def clan_war(bot, update, args):
    tag = get_tag(args)
    if tag is None:
        bot.send_message(update.message.chat.id, 'Invalid clan tag')
        return
    
    clan_war_info = load_clan_war_info(tag, False, False)
    answer = ""
    for info in clan_war_info:
        answer += info + "\n"

    bot.send_message(update.message.chat.id, '`' + answer + '`', parse_mode="Markdown")


def clan_war_ece(bot, update, args):
    tag = get_tag(args)
    if tag is None:
        bot.send_message(update.message.chat.id, 'Invalid clan tag')
        return

    clan_war_info = load_clan_war_info(tag, True, False)
    answer = ""
    for info in clan_war_info:
        answer += info + "\n"

    bot.send_message(update.message.chat.id, '`' + answer + '`', parse_mode="Markdown")


def clan_war_ece_last_season(bot, update, args):
    tag = get_tag(args)
    if tag is None:
        bot.send_message(update.message.chat.id, 'Invalid clan tag')
        return

    clan_war_info = load_clan_war_info(tag, True, True)
    answer = ""
    for info in clan_war_info:
        answer += info + "\n"

    bot.send_message(update.message.chat.id, '`' + answer + '`', parse_mode="Markdown")


def clan_stat(bot, update, args):
    tag = get_tag(args)
    if tag is None:
        bot.send_message(update.message.chat.id, 'Invalid clan tag')
        return

    answer = get_stat(tag)

    bot.send_message(update.message.chat.id, '`' + answer + '`', parse_mode="Markdown")


def max_win_streak(bot, update, args):
    tag = get_tag(args)
    if tag is None:
        bot.send_message(update.message.chat.id, 'Invalid clan tag')
        return

    answer = load_win_streak_info(tag)

    bot.send_message(update.message.chat.id, '`' + answer + '`', parse_mode="Markdown")


def current_win_streak(bot, update, args):
    tag = get_tag(args)
    if tag is None:
        bot.send_message(update.message.chat.id, 'Invalid clan tag')
        return

    answer = load_current_win_streak_info(tag)

    bot.send_message(update.message.chat.id, '`' + answer + '`', parse_mode="Markdown")


def card_collection(bot, update, args):
    tag = get_tag(args)
    if tag is None:
        bot.send_message(update.message.chat.id, 'Invalid clan tag')
        return

    answer = load_card_collection_info(tag)
    if len(answer) == 0:
        answer = "No one skips collection day."

    bot.send_message(update.message.chat.id, '`' + answer + '`', parse_mode="Markdown")


def player_clan_war_stat(bot, update, args):
    tag = get_tag(args)
    if tag is None:
        bot.send_message(update.message.chat.id, 'Invalid clan tag')
        return

    answer = load_player_clan_war_win_rate(tag)

    bot.send_message(update.message.chat.id, '`' + answer + '`', parse_mode="Markdown")


def about(bot, update):
    bot.send_message(update.message.chat.id, about_text)


def start(bot, update):
    bot.send_message(45227519, str(update.message.chat.id))


def help(bot, update):
    bot.send_message(update.message.chat.id, 'TBD')


def main():
    updater = Updater(token)
    updater.start_webhook(listen='127.0.0.1', port=5000, url_path=token)
    updater.bot.set_webhook(url='https://pigowl.com:443/' + token)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("about", about))
    dp.add_handler(CommandHandler("clanwar", clan_war, pass_args=True))
    dp.add_handler(CommandHandler("clanwarece", clan_war_ece, pass_args=True))
    dp.add_handler(CommandHandler("clanwarecelastseason", clan_war_ece_last_season, pass_args=True))
    dp.add_handler(CommandHandler("clanstat", clan_stat, pass_args=True))
    dp.add_handler(CommandHandler("maxwinstreak", max_win_streak, pass_args=True))
    dp.add_handler(CommandHandler("winstreak", current_win_streak, pass_args=True))
    dp.add_handler(CommandHandler("collectiondayskip", card_collection, pass_args=True))
    dp.add_handler(CommandHandler("playercwstat", player_clan_war_stat, pass_args=True))

    updater.idle()

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
    # answer = load_clan_war_info('2UJ2GJ', True, True)
    # print(answer)


if __name__ == "__main__":
    main()
