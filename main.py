from telegram.ext import Updater, Filters, CommandHandler
import requests
import json

token = ''
royaleToken = ''


def echo(bot, update):
    params = dict(
        authorization=royaleToken
    )

    r = requests.get(url='https://api.clashroyale.com/v1/clans/%232UJ2GJ/warlog', params=params)

    update.message.reply_text(r.json())


def load_clan_member(clan_tag):
    params = dict(
        authorization=royaleToken
    )

    r = requests.get(url='https://api.clashroyale.com/v1/clans/' + clan_tag, params=params)

    result = {}
    clan_info = json.loads(r.json())
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

    all_data = json.loads(r.json())

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
                plays += "1" if participant['wins'] > 0 else "0"
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


def clan_war(bot, updater):
    load_clan_member('%232UJ2GJ')
    clan_war_info = load_clan_war_info()
    for info in clan_war_info:
        print(info)


def main():
    updater = Updater(token)
    updater.start_webhook(listen='127.0.0.1', port=5000, url_path=token)
    updater.bot.set_webhook(url='https://pigowl.com:443/' + token)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("clanwar", clan_war))

    updater.idle()



if __name__ == "__main__":
    main()
