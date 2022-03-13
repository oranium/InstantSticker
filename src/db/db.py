import sqlite3
import time


def log_chat_into_database(bot, update):
    chat_id = update.message.chat.id
    ts = time.time()
    conn = sqlite3.connect('log.db')
    cursor = conn.execute(
        'SELECT lastusage FROM chats WHERE chatid = ?', (chat_id,))
    data = cursor.fetchone()
    if data is None:
        print("The bot now is used in a new chat! (chatid = {})".format(chat_id))
        conn.execute(
            'INSERT INTO chats (chatid, lastusage) VALUES (?, ?)', (chat_id, ts))
        conn.commit()
    else:
        conn.execute(
            'UPDATE chats set lastusage = ? where chatid = ?', (ts, chat_id))
        conn.commit()
    conn.close()
    count_interactions()


def log_sticker_into_database(file_id, chat_id, kept):
    conn = sqlite3.connect('log.db')
    ts = time.time()
    conn.execute(
        'INSERT INTO stickers (chatid, fileid, kept, time) VALUES (?, ?, ?, ?)', (file_id, chat_id, kept, ts))
    conn.commit()


def count_interactions():
    try:
        counter = 0
        with open('interactions.txt', 'r') as f:
            counter = int(f.readline().strip())
            counter += 1
        with open('interactions.txt', 'w') as f:
            f.write(str(counter))
    except Exception as err:
        print("Error while writing to file: {}".format(err))
