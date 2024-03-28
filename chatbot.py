from telegram import Update
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackContext)
import logging, os
from ChatGPTHKBU import ChatGPTHKBU


def equiped_chatgpt(update, context):
    global chatgpt
    reply_message = chatgpt.submit(update.message.text)
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


def main():
    updater = Updater(token=(os.environ['TELEGRAM_ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello))

    # dispatcher for chatgpt
    global chatgpt
    chatgpt = ChatGPTHKBU()
    chatgpt_handler = MessageHandler(Filters.text & (~Filters.command),
                                     equiped_chatgpt)
    dispatcher.add_handler(chatgpt_handler)
    # To start the bot:
    updater.start_polling()
    updater.idle()


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')


def hello(update: Update, context: CallbackContext) -> None:
    try:
        reply_message = r"Good day, " + context.args[0] + r"!"
        logging.info("Update: " + str(update))
        logging.info("context: " + str(context))
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /hello <keyword>')

