import re
from telegram import Update
from telegram.ext import (CommandHandler, MessageHandler,
                          CallbackContext, ApplicationBuilder, filters, ConversationHandler, CallbackQueryHandler)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import logging, os
from ChatGPTHKBU import ChatGPTHKBU
from dotenv import load_dotenv
import sys
from mysqlconn import Database

load_dotenv()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
db_pool = Database()

START, WAIT_INPUT, WAIT_CHAT, WAIT_COMT = range(4)

async def equiped_chatgpt(update, context, is_free_chat=True):
    await db_pool.check_if_user_exists(update.message)
    global chatgpt
    if is_free_chat or prompt_filter(update.message.text):
        reply_message = chatgpt.submit(update.message.text)
        logging.info("Update: " + str(update))
        logging.info("context: " + str(context))
        await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Opps, No data found for the message.\nPlease ask Movie or TV related questions.")
    return WAIT_CHAT


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
    app.add_handler(CommandHandler('search', search))
    app.add_handler(CommandHandler('searchID', searchID))
    app.add_handler(CommandHandler('search_review', search_review))
    app.add_handler(CallbackQueryHandler(multiple_button, pattern=r's_(\d{1,2})'))
    app.add_handler(CommandHandler('rec', recommendHandler))
    app.add_handler(CallbackQueryHandler(rec_button_click, pattern='rec_\d'))
    comm_button_handler = CallbackQueryHandler(comt_button_click, pattern='.+?>com_\d+')
    # app.add_handler(comm_button_handler)

    global chatgpt
    chatgpt = ChatGPTHKBU()
    chatgpt_handler = MessageHandler(filters.TEXT & (~filters.COMMAND),
                                     equiped_chatgpt)
    conv_handler_find = ConversationHandler(
        entry_points=[CommandHandler('find', findMovieByPrompt), CommandHandler('chat', enterChat), comm_button_handler],
        states={
            WAIT_INPUT: [MessageHandler(filters.TEXT & (~filters.COMMAND), handle_find_input)],
            WAIT_CHAT: [chatgpt_handler],
            WAIT_COMT: [MessageHandler(filters.TEXT & (~filters.COMMAND), handle_comt_input)]
        },
        fallbacks=[CommandHandler('exit', exit_conversation)]
    )
    app.add_handler(conv_handler_find)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), default_message))
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
        result = await db_pool.execute_query("SELECT * FROM media_content order by rating desc limit 5")
        if result:
            reply_message = convert_to_human_readable(result)
        else:
            reply_message = 'no record found'
        logging.info("Update: " + str(update))
        logging.info("context: " + str(context))
        await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
    except (IndexError, ValueError):
        await update.message.reply_text('Usage: /top')


async def searchID(update: Update, context: CallbackContext) -> None:
    media_id = ' '.join(context.args)

    # Query the database for the movie information based on the movie name
    query = f"SELECT * FROM media_content WHERE id = '{media_id}'"
    result = await db_pool.execute_query(query)
    reply_message = convert_to_human_readable(result)
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


async def search(update: Update, context: CallbackContext) -> None:
    await db_pool.check_if_user_exists(update.message)
    media_name = ' '.join(context.args)

    # Query the database for the movie information based on the movie name
    query = f"SELECT * FROM media_content WHERE title LIKE '%{media_name}%'"
    result = await db_pool.execute_query(query)

    if media_name and len(result) == 1:
        title = result[0][1]
        title_id = result[0][0]
        comt_keyboard = [
            [InlineKeyboardButton("View Comments", callback_data=f'{title}>com_0/{title_id}')],
            [InlineKeyboardButton("Add Comment", callback_data=f'{title}>com_1/{title_id}')]
        ]
        if True:
            comt_keyboard.append(
                [InlineKeyboardButton("Delete my Comment", callback_data=f'{title}>com_2/{title_id}')])
        reply_message = convert_to_human_readable(result)
        reply_markup=InlineKeyboardMarkup(comt_keyboard)
    elif media_name and len(result) == 0:
        reply_message = 'Movie not found'
        reply_markup=None
    elif media_name and len(result) > 1:
        message=""
        buttons = []
        for item in result:
            message += f"id: {item[0]}, Title: {item[1]}, Year: {item[2]}, Rating: {item[6]}\n\n"
            buttons.append([InlineKeyboardButton((item[0]), callback_data=str(f's_{item[0]}'))])
        reply_markup = InlineKeyboardMarkup(buttons)
        reply_message = f"Multiple movies found. Please choose one:\n {message}\n choose:"
    else:
        reply_message = 'Please provide a movie name to search.'
        reply_markup = None


    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    await update.message.reply_text(reply_message, reply_markup=reply_markup)

async def search_review(update: Update, context: CallbackContext) -> None:
    mediaid = ' '.join(context.args)

    query = f"SELECT * FROM reviews WHERE media_id LIKE '%{mediaid}%'"
    result = await db_pool.execute_query(query)
    if mediaid and len(result) == 1:
        reply_message = convert_to_human_readable(result)
    elif mediaid and len(result) == 0:
        reply_message = 'Movie not found'
    elif mediaid and len(result) > 1:
        multiple = f"SELECT id,media_id,user_id,comments,rating FROM reviews WHERE media_id LIKE '%{mediaid}%'"
        multiple_result = await db_pool.execute_query(multiple)
        message=""
        for item in multiple_result:
            if sys.getsizeof(item[3].encode('utf-8')) > 2048:
               message += f"id: {item[0]}, Media_id: {item[1]}, User_id: {item[2]}, Comments: {item[3][50]+'...'}, Rating: {item[4]}\n\n"
            else:
               message += f"id: {item[0]}, Media_id: {item[1]}, User_id: {item[2]}, Comments: {item[3]}, Rating: {item[4]}\n\n"
    reply_message = f"Comments found:\n {message}\n"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

async def multiple_button(update, context):
    query = update.callback_query
    selected_data = query.data.split('_')[1]
    info = f"SELECT * FROM media_content WHERE id = '{int(selected_data)}'"
    result = await db_pool.execute_query(info)
    reply_message = convert_to_human_readable(result)
    title = ''
    match =  re.search(r'Title:\s*([^\n]*)', reply_message)
    if match:
        title = match.group(1)
    # await query.answer()
    comt_keyboard = [
        [InlineKeyboardButton("View Comments", callback_data=f'{title}>com_0/{selected_data}')],
        [InlineKeyboardButton("Add Comment", callback_data=f'{title}>com_1/{selected_data}')]
    ]
    if await db_pool.check_if_user_reviews(update.callback_query,int(selected_data)):
        comt_keyboard.append([InlineKeyboardButton("Delete my Comment", callback_data=f'{title}>com_2/{selected_data}')])
    await query.edit_message_text(text=f"Movie of your choice:\n{reply_message}",reply_markup=InlineKeyboardMarkup(comt_keyboard))

async def comt_button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    option = query.data.split('>')[1].split('/')[0]
    title =  query.data.split('>')[0]
    title_id = query.data.split('/')[1]
    # Edit the existing message to update the reply based on the button clicked
    reply_message = ''
    if option == 'com_0':
        reply_message = f'View Comments for {title}:\n'

    elif option == 'com_1':
        reply_message = f'Add your Comment for {title}:\n'
        await query.answer()
        await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
        return WAIT_COMT

    elif option == 'com_2':
        reply_message = f'Delete your Comment for {title}:\n'

    await query.answer()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)

def convert_to_human_readable(data):
    result = ""
    for item in data:
        result += f"Title: {item[1]}\n"
        result += f"Year: {item[2]}\n"
        result += f"Category ID: {'Movie' if item[3] == 1 else 'TV Series'}\n"
        result += f"Genre: {item[4]}\n"
        result += f"Description: {item[5]}\n"
        result += f"Rating: {item[6]}\n"
        result += f"poster: {item[7]}\n\n"
    return result

async def start(update: Update, context: CallbackContext):
    await db_pool.check_if_user_exists(update.message)
    reply_text = "Greeting! I'm a Movie & TV info chatbot 🤖\n\n"
    await update.message.reply_text(reply_text)


async def findMovieByPrompt(update: Update, context: CallbackContext):
    await db_pool.check_if_user_exists(update.message)
    await update.message.reply_text(
        'you can use /exit to exit.\nHello! Please enter the info for the Movie or TV shows you want to find:')
    return WAIT_INPUT


async def enterChat(update: Update, context: CallbackContext):
    await db_pool.check_if_user_exists(update.message)
    await update.message.reply_text('you can use /exit to exit.\nHello, ChatGPT here.\nfeel free to chat with me:')
    return WAIT_CHAT


rec_keyboard = [
    [InlineKeyboardButton("All", callback_data='rec_0')],
    [InlineKeyboardButton("Sci-fi", callback_data='rec_1')],
    [InlineKeyboardButton("Action", callback_data='rec_2')],
    [InlineKeyboardButton("Horror", callback_data='rec_3')]
]


async def recommendHandler(update: Update, context: CallbackContext):
    await db_pool.check_if_user_exists(update.message)
    message_text = "Hello! Please choose one of the following options:"
    await update.message.reply_text(message_text, reply_markup=InlineKeyboardMarkup(rec_keyboard))


async def rec_button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    option = query.data
    prompt = ("Please provide straightforward responses without using apologies. Be concise. "
              "Recommend me 5 movies or tv_series in the format of \"Title:name\nYear:year\nCategory:(Movie or TV Series)\nGenre:genre\nDescription:description\nRating:IMDB rating\"")
    # Edit the existing message to update the reply based on the button clicked
    if option == 'rec_1':
        prompt = prompt + "genre Sci-fi"
    elif option == 'rec_2':
        prompt = prompt + "genre Action"
    elif option == 'rec_3':
        prompt = prompt + "genre Horror"

    reply_text = chatgpt.submit(prompt)
    await query.edit_message_text(text=reply_text, reply_markup=InlineKeyboardMarkup(rec_keyboard))


async def handle_find_input(update: Update, context: CallbackContext):
    global chatgpt
    message = update.message.text
    message = ("Please provide straightforward responses without using apologies. Be concise. "
               "I want to find movie or tv_series in the format of \"Title:name\nYear:year\nCategory:(Movie or TV Series)\nGenre:genre\nDescription:description\nRating:IMDB rating\""
               "by information below") + message
    reply_message = chatgpt.submit(message)
    reply_message = reply_message + "\nenter /exit to exit."
    await update.message.reply_text(f'{reply_message}')
    return WAIT_INPUT

async def handle_comt_input(update: Update, context: CallbackContext):
    message = update.message.text
    await update.message.reply_text('comment success!')
    return ConversationHandler.END


async def default_message(update: Update, context: CallbackContext):
    await update.message.reply_text("Sorry, I don't understand that.\nPlease use /start to view commands.")


async def exit_conversation(update: Update, context: CallbackContext):
    await update.message.reply_text('Exited.\nPlease use /start to view commands.')
    return ConversationHandler.END


if __name__ == '__main__':
    main()
