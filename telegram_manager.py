from telegram.ext import Updater, CommandHandler
import logging
from private import token


class TelegramManager:
    def __init__(self):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

        self.updater = Updater(token=token)
        self.updater.start_webhook(listen='127.0.0.1', port=5000, url_path=token)
        self.updater.bot.set_webhook(url='https://pigowl.com:443/' + token)
        self.dispatcher = self.updater.dispatcher

        self.dispatcher.add_handler(CommandHandler("start", self.start))

        self.updater.idle()

    @staticmethod
    def start(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")
