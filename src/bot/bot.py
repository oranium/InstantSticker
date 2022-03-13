#!/usr/bin/python3
from telegram.ext import ConversationHandler
from telegram.ext import Updater, CommandHandler, MessageHandler, RegexHandler
from telegram.ext.filters import Filters
from db.db import log_chat_into_database
from credentials import CREDENTIALS
from functions import KEYBOARD_COMMANDS, DECISION, DELETE, start, error, process_image, helper, sticker_decision, \
    user_info, del_sticker_from_set, exit_conversation, delete_info, get_user_info, send_stats


def initialize_bot():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater(CREDENTIALS["TOKEN"])

    # Get the dispatcher to register handlers:
    dp = updater.dispatcher

    # Add conversation handler with predefined states:
    conv_handler_get_sticker = ConversationHandler(
        entry_points=[MessageHandler(Filters.photo, process_image)],
        states={
            DECISION: [RegexHandler('^({}|{})$'.format(
                KEYBOARD_COMMANDS['KEEP'], KEYBOARD_COMMANDS['DEL']), sticker_decision)]
        },
        fallbacks=[]
    )

    conv_handler_del_sticker = ConversationHandler(
        entry_points=[CommandHandler("deletesticker", delete_info)],
        states={
            DELETE: [MessageHandler(Filters.sticker, del_sticker_from_set)]
        },
        fallbacks=[CommandHandler("exit", exit_conversation)]
    )

    dp.add_handler(handler=MessageHandler(Filters.all, log_chat_into_database), group=1)
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('help', helper))
    dp.add_handler(CommandHandler('userinfo', get_user_info))
    dp.add_handler(CommandHandler('stats', send_stats))
    dp.add_handler(MessageHandler(Filters.document, user_info))
    dp.add_handler(conv_handler_get_sticker)
    dp.add_handler(conv_handler_del_sticker)

    # Log all errors:
    dp.add_error_handler(error)

    # Start StickerBot:
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process
    # receives SIGINT, SIGTERM or SIGABRT:
    updater.idle()
