import os
import time

import pandas as pd
from telegram import Update
from telegram.ext import (CallbackContext, CommandHandler,
                          Updater, MessageHandler, Filters)

from db_command import db_init, insert_to_db
from logger import logger
from utils import get_average, file_info


con, cur = db_init()


def start(update: Update, context: CallbackContext) -> None:
    """Приветствует нового пользователя"""
    chat = update.effective_chat
    name = update.effective_chat.first_name

    context.bot.send_message(
        chat_id=chat.id,
        text=f'Привет, {name}! Пожалуйста, загрузите excel-файл с данными.',
    )


def load_file(update: Update, context: CallbackContext) -> None:
    """Сохраняет файл в базу данных и отвечает пользователю."""
    file_name, ext = update.effective_message.document.file_name.split('.')
    chat_id = update.effective_chat.id
    data = []
    if ext in ['xlsx', 'xls']:
        file_id = update.effective_message.document.file_id
        file_path = gen_filename(ext)
        context.bot.getFile(file_id).download(file_path)
        data = [[chat_id] + row for row in read_file(file_path)]
        text = f'Прочитан файл: {file_info(data)}'

    else:
        text = 'Неверный формат файла'
        logger.info(f'{text}: .{ext}')

    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        disable_web_page_preview=True
    )
    if data:
        context.bot.send_message(
            chat_id=chat_id,
            text=f'Опрашиваем сайты...',
        )
        insert_to_db(con, cur, data)
        price, amount = get_average(data)
        context.bot.send_message(
            chat_id=chat_id,
            text=f'Узнали цен: {amount}\n'
                 f'Средняя цена товаров в файле: {price}₽',
        )


def gen_filename(ext: str) -> str:
    """Генерирует имя файла для сохранения, в формате 'file_<timestamp>'."""
    base_dir = f'{os.path.dirname(os.path.abspath(__file__))}/files/'
    pattern = base_dir + 'file_{}.{}'
    stamp = str(int(time.time() * 1000))
    return pattern.format(stamp, ext)


def read_file(file: str) -> list:
    """Читает excel-файл и возвращает вложенный список с данными."""
    file = pd.ExcelFile(file)
    data = file.parse(file.sheet_names[0])
    data = data.to_numpy().tolist()

    return data


def bot():
    """Основная функция работы бота."""
    token = os.environ['TOKEN']
    updater = Updater(token=token)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(MessageHandler(Filters.document, load_file))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    bot()
