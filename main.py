from telegram.ext import Updater, Filters, CommandHandler
import requests
import json

token = ''
royaleToken = ''


def load_clan_member(clan_tag):
    params = dict(
        authorization=royaleToken
    )

    r = requests.get(url='https://api.clashroyale.com/v1/clans/' + clan_tag, params=params)

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

    r = requests.get(url='https://api.clashroyale.com/v1/clans/' + clan_tag + '/warlog', params=params)

    all_data = r.json()

    for item in all_data['items']:
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
                plays += "1" if participant['wins'] > 0 else "0" if participant['battlesPlayed'] > 0 else "_"
            else:
                plays += "x"

        if battles > 0:
            win_rate = wins / battles
        win_rate = int(100 * win_rate)

        plays = plays[::-1]

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

    r = requests.get(url='https://api.clashroyale.com/v1/clans/' + clan_tag + '/warlog', params=params)

    all_data = r.json()

    return all_data['standings']


def clan_war(bot, update, args):
    if len(args) != 1:
        bot.send_message(update.message.chat.id, 'Invalid clan tag')
        return

    tag = args[0]
    tag = tag.replace('#', '').upper()
    
    clan_war_info = load_clan_war_info('%23' + tag)
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

    standings = load_clan_war_standing(tag)
    for clan in standings:
        print(clan['clan']['name'])


def main():
    updater = Updater(token)
    updater.start_webhook(listen='127.0.0.1', port=5000, url_path=token)
    updater.bot.set_webhook(url='https://pigowl.com:443/' + token)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("clanwar", clan_war, pass_args=True))
    dp.add_handler(CommandHandler("clanstat", clan_stat, pass_args=True))

    updater.idle()



if __name__ == "__main__":
    main()
