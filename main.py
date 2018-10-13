from telegram.ext import Updater, Filters, CommandHandler
import requests
import sys

if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")

token = ''
royaleToken = ''


def load_clan_member(clan_tag):
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


def load_clan_war_info(clan_tag):
    clan_war_info = {}
    clan_members = load_clan_member(clan_tag)
    for tag in clan_members.keys():
        clan_war_info[tag] = []

    params = dict(
        authorization=royaleToken
    )

    r = requests.get(url='https://api.clashroyale.com/v1/clans/%23' + clan_tag + '/warlog', params=params)

    all_data = r.json()

    for item in reversed(all_data['items']):
        participants = item['participants']
        for playerTag in clan_members.keys():
            participant = next((x for x in participants if x['tag'] == playerTag), None)
            clan_war_info[playerTag].append(participant)

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
                if participant['battlesPlayed'] < 2:
                    plays += "1" if participant['wins'] > 0 else "0" if participant['battlesPlayed'] > 0 else "_"
                else:
                    plays += "("
                    for war_battle in range(participant['battlesPlayed']):
                        plays += "1" if war_battle < participant['wins'] else "0"
                    plays += ")"
            else:
                plays += "x"

        if battles > 0:
            win_rate = wins / battles
        win_rate = int(100 * win_rate)

        sorted_players.append((clan_members[tag], win_rate, plays, battles))

    sorted_players.sort(key=lambda x: (x[1], x[3]), reverse=True)

    result = []
    for player in sorted_players:
        result.append((player[0] + " " + str(player[1]) + "% " + player[2]))

    return result


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


def clan_war(bot, update, args):
    if len(args) != 1:
        bot.send_message(update.message.chat.id, 'Invalid clan tag')
        return

    tag = args[0]
    tag = tag.replace('#', '').upper()
    
    clan_war_info = load_clan_war_info(tag)
    answer = ""
    for info in clan_war_info:
        answer += info + "\n"

    bot.send_message(update.message.chat.id, '`' + answer + '`', parse_mode="Markdown")


def clan_stat(bot, update, args):
    if len(args) != 1:
        bot.send_message(update.message.chat.id, 'Invalid clan tag')
        return

    tag = args[0]
    tag = tag.replace('#', '').upper()
    answer = get_stat(tag)

    bot.send_message(update.message.chat.id, '`' + answer + '`', parse_mode="Markdown")


def about(bot, update):
    about_text = '''This is free open source telegram bot.
    You can contribute here https://github.com/dfomin/ClashRoyaleBot.
    You can text me in telegram @dfomin'''
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
    dp.add_handler(CommandHandler("clanstat", clan_stat, pass_args=True))

    updater.idle()

    # answer = load_clan_war_info('2UJ2GJ')
    # print(answer)
    # answer = get_stat('2UJ2GJ')
    # print(answer)


if __name__ == "__main__":
    main()
