from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler
import logging
from const import DEFAULT_PACKAGE_TITLE, DEFAULT_STICKERSET_NAME, EMOTIONS, ADMINS

from telegram.error import TelegramError, BadRequest

from azure_com import get_sticker_from_photo

from db import log_sticker_into_database

from get_stats import get_stats


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

logger = logging.getLogger(__name__)

# states for conversations
DECISION, DELETE = range(2)

KEYBOARD_COMMANDS = {
    "KEEP": "Keep it!",
    "DEL": "Delete it!"
}

############################Keyboard#######################################


def send_keyboard(update):
    # Create buttons to slect language:
    keyboard = [[KEYBOARD_COMMANDS['KEEP'], KEYBOARD_COMMANDS['DEL']]]

    # Create initial message:
    message = "*How do you like it?*"
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    update.message.reply_text(
        message, parse_mode="MARKDOWN", reply_markup=reply_markup)


def remove_keyboard(msg, update):
    update.message.reply_text(msg,
                              reply_markup=ReplyKeyboardRemove())

###########################################################################


############################Sticker#######################################
def get_default_sticker_set_name(user_id, botname):
    return DEFAULT_STICKERSET_NAME.format(
        user_id, botname).lower()


def get_latest_sticker(bot, update):
    user_id = update.message.from_user.id
    sticker_set_name = get_default_sticker_set_name(user_id, bot.username)
    sticker_set = bot.get_sticker_set(name=sticker_set_name)
    if (len(sticker_set.stickers) > 0):
        return sticker_set.stickers[-1]
    logger.info("Sticker set is empty!")
    return ""


def delete_sticker(bot, sticker_id):
    if sticker_id:
        try:
            bot.delete_sticker_from_set(sticker_id)
            return True
        except Exception as err:
            logger.error(err)
            return False

def get_sticker_set_title(first_name):
    if (first_name[-1] == 's') or (first_name[-1] == 'z'):
        return "{}' sticker pack".format(first_name)
    else:
        return "{}'s sticker pack".format(first_name)

def add_new_sticker(bot, update, sticker_data):
    user = update.message.from_user
    user_id = user.id
    first_name = user.first_name
    # file_id = update.message.photo[-1].file_id
    png_sticker = open(sticker_data['path'], 'rb')
    sticker_set_name = get_default_sticker_set_name(user_id, bot.username)

    emojis = EMOTIONS[sticker_data["emotion"]]

    # first try to create a new sticker pack with default name
    try:
        logger.info(sticker_set_name)
        bot.add_sticker_to_set(
            user_id=user_id, name=sticker_set_name, png_sticker=png_sticker, emojis=emojis)
        logger.info("{} added new sticker to {}".format(
            user.first_name, sticker_set_name))
    except TelegramError as err:
        # if sticker set does not exist create one
        logger.error(err)
        png_sticker = open(sticker_data['path'], 'rb')
        if (str(err) == "Stickerset_invalid"):
            try:
                title = get_sticker_set_title(first_name)
                bot.create_new_sticker_set(
                    user_id=user_id, name=sticker_set_name, title=title, png_sticker=png_sticker, emojis=emojis)
                logger.info(
                    'Sucessfully created sticker set {}'.format(sticker_set_name))
            except TelegramError as err:
                logger.error(err)


def send_new_sticker(bot, update):
    # send new sticker to user
    chat_id = update.message.chat.id
    sticker = get_latest_sticker(bot, update)
    logger.info(sticker)
    bot.send_message(
        chat_id=chat_id, text="*Here is your new Sticker:*", parse_mode="MARKDOWN")
    bot.send_sticker(chat_id=chat_id, sticker=sticker)


def send_emotion(bot, update, emotion):
    if (emotion != EMOTIONS['not_detected']):
        chat_id = update.message.chat.id
        bot.send_message(
            chat_id=chat_id, text="{} describes your emotion the most!".format(emotion))


def send_error(bot, update, err):
    chat_id = update.message.chat.id
    user_name = update.message.from_user.first_name
    bot.send_message(
        chat_id=chat_id, text="I\'m sry {}! {}".format(user_name, str(err)))

#####################################################################################


#####################small on command functions#############################
def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def start(bot, update):
    """
    Help function.
    This displays a set of commands available for the bot.
    """
    user = update.message.from_user
    username = user.first_name
    logger.info("User {} started the bot.".format(user.first_name))
    update.message.reply_text(
        "Welcome {}\nJust send me your latest selfie as a photo and I will turn it into a fancy sticker!".format(username))


def helper(bot, update):
    """
    Help function.
    This displays a set of commands available for the bot.
    """
    user = update.message.from_user
    logger.info("User {} asked for help.".format(user.first_name))
    update.message.reply_text(
        "Just send me your latest selfie as a photo and I will turn it into a fancy sticker!\n<a href=\"https://www.youtube.com/watch?v=yz5Jaj9_Sog\">How to use FaceToSticker.</a>", parse_mode="HTML")


def user_info(bot, update):
    user = update.message.from_user
    logger.info("User {} uploaded wrong format.".format(user.first_name))
    update.message.reply_text(
        'Please only send me photos.\nNote: If telegram asks you how to send your selfie klick on "as photo"')


def delete_info(bot, update):
    first_name = update.message.from_user.first_name
    update.message.reply_text(
        'Ok just send me a sticker from your pack "{}" I created and I will remove it.'.format(get_sticker_set_title(first_name)))
    return DELETE


def exit_conversation(bot, update):
    update.message.reply_text(
        "Completed :) From now on you can send me selfies again.")
    return ConversationHandler.END


def del_sticker_from_set(bot, update):
    sticker = update.message.sticker
    sticker_id = sticker.file_id
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    if sticker_id:
        try:
            if(sticker.set_name is not DEFAULT_STICKERSET_NAME.format(user_id)):
                logger.info(sticker.set_name)
                logger.info(get_sticker_set_title(update.message.from_user.first_name))
                raise Exception("Stickerset_not_owned")
            #bot.delete_sticker_from_set(sticker_id)
            bot.send_message(
                chat_id=chat_id, text='Sticker has been deleted!\nPlease send me another sticker to delete or exit with \exit')
        except Exception as err:
            error_str = str(err)
            if error_str is "Stickerset_not_modified":
                bot.send_message(chat_id=chat_id, text="You already deleted this sticker.\nPlease note that it takes some time for Telegram to delete the sticker.\nOften restarting the app helps.")
            elif error_str is "Stickerset_invalid":
                bot.send_message(chat_id=chat_id, text="I'm only able to delete stickers from sets you created with my help!")
            elif error_str is "Stickerset_not_owned":
                bot.send_message(chat_id=chat_id, text="You are not allowed to delete stickers that you didn't create!")
            else:
                bot.send_message(chat_id=chat_id, text="An unknown error occured. Please try again.")
    else:
        bot.send_message(chat_id=chat_id, text="Please only send me stickers or type /exit to stop deleting sticker.")

    return DELETE

def send_stats(bot, update): 
    if (update.message.chat.id in ADMINS):
        stats = get_stats()
        msg = 'INSTANT STICKER STATS {}\n'.format(u'\U0001f4ca')
        for s in stats:
            msg += '{}: {}\n'.format(s[0],s[1])
        update.message.reply_text(msg)

def get_user_info(bot, update):
    if (update.message.chat.id in ADMINS):
        user = update.message.from_user
        first_name = user.first_name
        chat_id = update.message.chat.id
        user_id = user.id
        user_info = "Name: {}\nUserid: {}\nChatid: {}".format(first_name, user_id, chat_id)
        update.message.reply_text(user_info)

#####################################################################################


def process_image(bot, update):
    user = update.message.from_user

    update.message.reply_text("Ok {}, just give me a second to create the sticker.".format(user.first_name))

    # get latest photo
    file_id = update.message.photo[-1].file_id
    # get url where photo can be downloaded from telegram server
    image_url = bot.getFile(file_id).file_path

    # prozess photo via azure and tensorflow
    try:
        sticker_data = get_sticker_from_photo(image_url)
    except Exception as err:
        send_error(bot, update, err)
        return ConversationHandler.END

    # holds emotion, image path
    logger.info(sticker_data)

    # add the new sticker to the database
    add_new_sticker(bot, update, sticker_data)

    # send a preview for new sticker to user
    send_new_sticker(bot, update)
    send_emotion(bot, update, EMOTIONS[sticker_data["emotion"]])

    # ask for desicion to keep or delete the sticker
    send_keyboard(update)

    return DECISION


def sticker_decision(bot, update):
    user = update.message.from_user
    message_text = update.message.text
    logger.info("User {} made the decision to {}".format(
        user.first_name, message_text))
    msg = ""

    sticker_id = get_latest_sticker(bot, update).file_id
    keep = update.message.text == KEYBOARD_COMMANDS["KEEP"]
    if keep:
        msg = "Great! Have fun with your new Sticker." + u'\u2665\ufe0f'
    else:
        if(delete_sticker(bot, sticker_id)):
            logger.info(
                "{} successfully deleted a sticker.".format(user.first_name))
            msg = "Ok I removed the sticker {} \nHopefully it's getting better next time!".format(
                u'\U0001f630')
        else:
            msg = "Sorry an error occured and I couln't delete the sticker."

    remove_keyboard(msg, update)
    log_sticker_into_database(sticker_id, update.message.chat.id, keep)

    return ConversationHandler.END

#########################EOF########################################################
