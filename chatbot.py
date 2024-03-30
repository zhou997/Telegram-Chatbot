from telegram import Update
from telegram.ext import (CommandHandler, MessageHandler,
                          CallbackContext, ApplicationBuilder, filters)
import logging, os
from ChatGPTHKBU import ChatGPTHKBU
from dotenv import load_dotenv

from mysqlconn import Database

load_dotenv()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
db_pool = Database()


async def equiped_chatgpt(update, context, is_free_chat=False):
    await db_pool.check_if_user_exists(update.message)
    global chatgpt
    if prompt_filter(update.message.text) or is_free_chat:
        reply_message = chatgpt.submit(update.message.text)
        logging.info("Update: " + str(update))
        logging.info("context: " + str(context))
        await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Opps, No data found for the message.\nPlease ask Movie or TV related questions.")


def prompt_filter(text):
    global chatgpt
    reply = chatgpt.submit(
        f"\"{text}\" is this text related to tv show or movie. you only need to reply yes if it is, reply no if it don't")
    if ("Yes" or "yes") in reply:
        return True
    if ("No" or "no") in reply:
        return False
    else:
        return False


def main():
    app = ApplicationBuilder().token(os.getenv('TELEGRAM_ACCESS_TOKEN')).concurrent_updates(True).build()
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("hello", hello))
    app.add_handler(CommandHandler("top", top))
    app.add_handler(CommandHandler("start", start))

    global chatgpt
    chatgpt = ChatGPTHKBU()
    chatgpt_handler = MessageHandler(filters.TEXT & (~filters.COMMAND),
                                     equiped_chatgpt)
    app.add_handler(chatgpt_handler)
    # To start the bot:
    app.run_polling()


async def help_command(update: Update, context: CallbackContext) -> None:
    await db_pool.check_if_user_exists(update.message)
    """Send a message when the command /help is issued."""
    await update.message.reply_text('Helping you helping you.')


async def hello(update: Update, context: CallbackContext) -> None:
    await db_pool.check_if_user_exists(update.message)
    try:
        reply_message = r"Good day, " + context.args[0] + r"!"
        logging.info("Update: " + str(update))
        logging.info("context: " + str(context))
        await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
    except (IndexError, ValueError):
        await update.message.reply_text('Usage: /hello <keyword>')


async def top(update: Update, context: CallbackContext) -> None:
    await db_pool.check_if_user_exists(update.message)
    try:
        result = await db_pool.execute_query("SELECT * FROM media_content")
        if result:
            reply_message = convert_to_human_readable(result)
        else:
            reply_message = 'no record found'
        logging.info("Update: " + str(update))
        logging.info("context: " + str(context))
        await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
    except (IndexError, ValueError):
        await update.message.reply_text('Usage: /top')


def convert_to_human_readable(data):
    result = ""
    for item in data:
        result += f"Title: {item[1]}\n"
        result += f"Year: {item[2]}\n"
        result += f"Category ID: {'Movie' if item[3] == 0 else 'TV Series'}\n"
        result += f"Genre: {item[4]}\n"
        result += f"Description: {item[5]}\n"
        result += f"Rating: {item[6]}\n\n"
    return result

async def start(update: Update, context: CallbackContext):
    await db_pool.check_if_user_exists(update.message)
    reply_text = "Greeting! I'm a Movie & TV info chatbot 🤖\n\n"
    await update.message.reply_text(reply_text)

if __name__ == '__main__':
    main()
