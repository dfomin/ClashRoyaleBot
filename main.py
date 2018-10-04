from telegram.ext import Updater, Filters, MessageHandler
import requests

token = ''
royaleToken = ''


def echo(bot, update):
    params = dict(
        authorization=royaleToken
    )

    r = requests.get(url='https://api.clashroyale.com/v1/clans/%232UJ2GJ/warlog', params=params)

    update.message.reply_text(r.json())


def main():
    updater = Updater(token)
    updater.start_webhook(listen='127.0.0.1', port=5000, url_path=token)
    updater.bot.set_webhook(url='https://pigowl.com:443/' + token)

    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text, echo))

    updater.idle()


if __name__ == "__main__":
    main()
