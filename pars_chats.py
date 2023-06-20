from telethon.errors import ChatAdminRequiredError
from telethon import utils
from datetime import datetime, timedelta, timezone


async def save_message_to_database(chat, message, conn, cursor):
    dialog_name = utils.get_display_name(chat)
    dialog_id = chat.id
    message_id = message.id
    publication_date = message.date.astimezone(timezone(timedelta(hours=3)))
    message_text = message.message
    try:
        dialog_type = message.replies.replies if message.replies else None
    except:
        dialog_type = None
    try:
        message_media = message.media.photo.id if message.media.photo else None
    except AttributeError as e:
        message_media = None
    try:
        sender_id = message.from_id.user_id if message.from_id else None
    except AttributeError as e:
        sender_id = None

    cursor.execute('''INSERT INTO news (dialog_name, dialog_type, dialog_id, message_id, publication_date, message_text, message_media, sender_id)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                      ON CONFLICT(dialog_id, message_id) DO UPDATE SET
                      dialog_name = excluded.dialog_name,
                      dialog_type = excluded.dialog_type,
                      publication_date = excluded.publication_date,
                      message_text = excluded.message_text,
                      message_media = excluded.message_media,
                      sender_id = excluded.sender_id''',
                   (dialog_name, dialog_type, dialog_id, message_id, publication_date, message_text, message_media,
                    sender_id))

    conn.commit()


async def get_history(chat_name, client):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
    tomorrow = today + timedelta(days=-1)
    messages = []
    async for message in client.iter_messages(chat_name, offset_date=today, reverse=True):
        messages.append(message)
    return messages


async def start(client, conn, cursor):
    # Получите список диалогов (каналы, группы и беседы), в которых вы состоите
    chat_dict = {}
    dialogs = await client.get_dialogs()
    iterator = 1
    it_chat = 1
    for x in dialogs:
        try:
            link_chat = "t.me/" + str(x.entity.username)
            print("№: " + str(
                iterator) + "; Название чата:" + x.entity.title + "; Ссылка на чат: " + link_chat + "; ID чата: " + str(
                x.entity.id) + ";")
            chat_dict[str(iterator)] = x.entity.id
            iterator += 1
        except AttributeError:
            continue

    flag = True
    print(
        "Выгрузка информации может занять длительное время, не закрывайте программу до окончания выгрузки")
    while it_chat <= iterator:
        try:
            chat_name = chat_dict[str(it_chat)]
            chat = await client.get_entity(chat_name)
            if flag:
                try:
                    history = await get_history(chat_name, client)
                    print(f"Выгружается чат {chat}")
                    print('Количество сообщений в чате:', len(history))
                    if not len(history):
                        print("В данном чате отсутствуют сообщения")
                        it_chat += 1
                        continue
                    for message in history:
                        await save_message_to_database(chat, message, conn, cursor)
                    print(
                        f"Выгрузка сообщений из чата завершена")
                    print('*' * 100)
                    it_chat += 1
                except ChatAdminRequiredError:
                    print(
                        "Выгрузка информации из данного чата запрещена администратором, выберите другой чат")
                    it_chat += 1
                    continue
            else:
                it_chat += 1
                continue
        except:
            it_chat += 1
            continue
