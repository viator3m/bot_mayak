import os
import time

import pandas as pd
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update, File
from telegram.ext import (CallbackContext, CallbackQueryHandler,
                          CommandHandler, Updater, MessageHandler, Filters)

from db_command import db_init, insert


con, cur = db_init()


def start(update: Update, context: CallbackContext) -> None:
    chat = update.effective_chat
    name = update.effective_chat.first_name

    context.bot.send_message(
        chat_id=chat.id,
        text=f'Привет, {name}! Пожалуйста, загрузите excel-файл с данными.',
    )


def load_file(update: Update, context: CallbackContext) -> None:
    file_name, ext = update.effective_message.document.file_name.split('.')
    chat_id = update.effective_chat.id
    if ext in ['xlsx', 'xls']:
        file_id = update.effective_message.document.file_id
        file_path = gen_filename(ext)
        context.bot.getFile(file_id).download(file_path)
        data = [[chat_id] + row for row in read_file(file_path)]

        text = 'Прочитан файл:'
        for row in data:
            _, name, url, xpath = row
            text += f"""
            name: {name}
            url: {url}
            xpath: {xpath}
            """
        insert(con, cur, data)
    else:
        text = 'Неверный формат файла'

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
    )


def gen_filename(ext: str) -> str:
    base_dir = f'{os.path.dirname(os.path.abspath(__file__))}/files/'
    pattern = base_dir + 'file_{}.{}'
    stamp = str(int(time.time() * 1000))
    return pattern.format(stamp, ext)


def read_file(file: str) -> list:
    file = pd.ExcelFile(file)
    data = file.parse(file.sheet_names[0])
    data = data.to_numpy().tolist()

    return data


def main():
    updater = Updater(token=token)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(MessageHandler(Filters.document, load_file))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
