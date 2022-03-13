from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ConversationHandler, CallbackQueryHandler, Filters
from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler
from telegram.ext.filters import Filters

from credentials import TELEGRAM_TOKEN
from functions import KEYBOARD_COMMANDS, DECISION, start, error, process_image, helper, sticker_decision, add_new_sticker, delete_sticker, get_latest_sticker


def main():
    """
    Main function.
    This function handles the conversation flow by setting
    states on each step of the flow. Each state has its own
    handler for the interaction with the user.
    """

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TELEGRAM_TOKEN)

    # Get the dispatcher to register handlers:
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('test', add_new_sticker))
    dp.add_handler(CommandHandler('delete', delete_sticker))
    dp.add_handler(CommandHandler('getSticker', get_latest_sticker))

    # Log all errors:
    dp.add_error_handler(error)

    # Start StickerBot:
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process
    # receives SIGINT, SIGTERM or SIGABRT:
    updater.idle()


if __name__ == '__main__':
    main()