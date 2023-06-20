import sqlite3
import time
from telethon.sync import TelegramClient
from pars_chats import start
import configparser

config = configparser.ConfigParser()
config.read("config.ini")
TOKEN = config['Telegram']['bot_token']
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']
phone_number = config['Telegram']['phone_number']
client = TelegramClient('session_name', api_id, api_hash)
client.start(phone_number)


async def main():
    me = await client.get_me()
    start_time = time.time()
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    await start(client, conn, cursor)
    cursor.close()
    conn.close()



if __name__ == '__main__':
    client.loop.run_until_complete(main())