from telethon.sync import TelegramClient
import random
import string
import configparser

config = configparser.ConfigParser()
config.read("config.ini")
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

async def download(channel_id, message_id):
    client = TelegramClient('session_name', api_id, api_hash)
    await client.start()

    message = await client.get_messages(channel_id, ids=message_id)
    media = message.photo

    downloaded_files = []

    if media is not None:
        if isinstance(media, list):
            for index, photo in enumerate(media):
                file_name = ''.join(random.choice(string.ascii_letters) for _ in range(12))
                result = await client.download_media(photo, file=file_name)
                downloaded_files.append(file_name)
        else:
            file_name = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
            result = await client.download_media(media, file=file_name)
            downloaded_files.append(file_name)


    await client.disconnect()
    return downloaded_files



