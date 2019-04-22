import sqlite3


def get_stats():
    stats = []
    conn = sqlite3.connect('log.db')
    cursor = conn.execute(
        'SELECT count(chatid) FROM chats')
    data = cursor.fetchone()
    stats.append(['Chats',data[0]])
    with open('interactions.txt', 'r') as f:
        count = f.readline()
        stats.append(['Interactions',count])
    cursor = conn.execute(
        'SELECT count(id) FROM stickers')
    data = cursor.fetchone()
    num_all_stickers = data[0]
    cursor = conn.execute(
        'SELECT count(id) FROM stickers WHERE kept=?', (True, ))
    data = cursor.fetchone()
    num_kept_stickers = data[0]
    num_del_stickers = num_all_stickers - num_kept_stickers
    stats.append(['Created stickers', num_all_stickers])
    stats.append(['Kept stickers', num_kept_stickers])
    stats.append(['Deleted stickers', num_del_stickers])
    conn.close()
    return stats
