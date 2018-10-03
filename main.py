from telegram.ext import Updater, Filters, MessageHandler

token = ''


def echo(bot, update):
    update.message.reply_text(update.message.text)


def main():
    updater = Updater(token)
    updater.start_webhook(listen='127.0.0.1', port=5000, url_path=token)
    updater.bot.set_webhook(url='https://pigowl.com/' + token, certificate=open('fullchain.pem', 'rb'))

    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text, echo))

    updater.idle()


if __name__ == "__main__":
    main()