import os
import re

import telebot

from stegano import lsb
from stegano import exifHeader


my_token = '1804449587:AAF025uszUcRgp-tPtXWPbdoA48vAlAaZu8'
get_data = []
chat_id = []

bot = telebot.TeleBot(my_token)
print('I am ready')


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, '''
Отправь фото и зашифруй или расшифруй его. С телефона используй "Отправить как файл", а не как обычную фотографию.
На данный момент корректно работает только с форматом JPEG.
    ''')


@bot.message_handler(content_types=['document'])
def get_photo(message):

    chat_id.append(message.chat.id)

    file_id = message.document.file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    filename = message.document.file_name

    '''Sorting dir to name new file'''
    files = os.listdir('photos_input')
    files_int = []

    for file in files:
        files_int.append(int(file[:-4]))

    files_sorted_int = sorted(files_int)
    files_sorted_str = []
    for file in files_sorted_int:
        file = str(file) + '.jpg'
        files_sorted_str.append(file)

    if re.findall('.jpg', filename) == ['.jpg']:
        photo_name = str(int(files_sorted_str[-1][:-4]) + 1) + '.jpg'
    elif re.findall('.JPG', filename) == ['.JPG']:
        photo_name = str(int(files_sorted_str[-1][:-4]) + 1) + '.JPG'
    elif re.findall('.png', filename) == ['.png']:
        photo_name = str(int(files_sorted_str[-1][:-4]) + 1) + '.png'
    elif re.findall('.PNG', filename) == ['.PNG']:
        photo_name = str(int(files_sorted_str[-1][:-4]) + 1) + '.PNG'

    photo_data = [photo_name, file_id]
    get_data.append(photo_data)
    with open(f'photos_input/{photo_name}', 'wb') as new_file:
        new_file.write(downloaded_file)

    markup = telebot.types.InlineKeyboardMarkup()
    btn_encrypt = telebot.types.InlineKeyboardButton('зашифровать', callback_data='encrypt')
    btn_decrypt = telebot.types.InlineKeyboardButton('расшифровать', callback_data='decrypt')
    markup.add(btn_encrypt, btn_decrypt)
    bot.reply_to(message, 'Нажми на кнопку "зашифровать" или "расшифровать"', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def choosing(call):
    if call.data == 'encrypt':
        bot.send_message(chat_id[0], 'Введи текст, используя команду "/secret"'
                                     '\nПример: /secret Я гей и никто не узнает об этом хихихи')
    elif call.data == 'decrypt':
        try:
            photo_name = get_data[-1][0]
            output_secret = exifHeader.reveal(f'photos_input/{photo_name}').decode()
            bot.send_message(chat_id[0], f'Зашифрованный текст:\n{output_secret}')
        except:
            bot.send_message(chat_id[0], 'Не могу найти зашифрованный текст :(')


@bot.message_handler(commands=['secret'])
def encrypt_send(message):
    photo_name = get_data[-1][0]
    if re.findall('.jpg', photo_name) == ['.jpg']:
        photo_name_encrypted = photo_name[:-4] + '_secret.jpg'
    elif re.findall('.JPG', photo_name) == ['.JPG']:
        photo_name_encrypted = photo_name[:-4] + '_secret.JPG'
    elif re.findall('.png', photo_name) == ['.png']:
        photo_name_encrypted = photo_name[:-4] + '_secret.png'
    elif re.findall('.PNG', photo_name) == ['.PNG']:
        photo_name_encrypted = photo_name[:-4] + '_secret.PNG'

    input_secret = exifHeader.hide(f'photos_input/{photo_name}', f'photos_output/{photo_name_encrypted}',
                                   message.text[8:])

    photo_encrypted = open(f'photos_output/{photo_name_encrypted}', 'rb')
    bot.send_document(message.chat.id, photo_encrypted)
    photo_encrypted.close()


@bot.message_handler(commands=['fullguide'])
def fullguide(message):
    bot.send_message(message.chat.id, 'ШАГ №1: Загрузите фотографию без сжатия'
                                      '\nСкриншот 1: Отправка без сжатия на ПК'
                                      '\nСкриншот 2: Отправка без сжатия на IOS')

    photo = open('fullguide/no_compress_PC.png', 'rb')
    bot.send_photo(message.chat.id, photo)
    photo.close()

    photo = open('fullguide/no_compress_IOS.png', 'rb')
    bot.send_photo(message.chat.id, photo)
    photo.close()

    bot.send_message(message.chat.id, 'ШАГ №2: Выберите что хотите сделать,'
                                      ' зашифровать или расшифровать текст в изображение/из изображения')

    photo = open('fullguide/choosing.jpg', 'rb')
    bot.send_photo(message.chat.id, photo)
    photo.close()

    bot.send_message(message.chat.id, 'ШАГ №3: Зашифровываем текст в изображение с помощью команды /secret,'
                                      ' записывая текст после команды')

    photo = open('fullguide/encrypt.jpg', 'rb')
    bot.send_photo(message.chat.id, photo)
    photo.close()

    bot.send_message(message.chat.id, 'ШАГ №:4 Получаем изображение в котором будет зашифрован текст')
    bot.send_message(message.chat.id, 'ШАГ №:5 Сохраняем изображение')
    bot.send_message(message.chat.id, 'ШАГ №:6 Загружаем полученное изображение (НЕ СЖИМАЯ) и выбираем расшифровать ')

    photo = open('fullguide/decrypt.png', 'rb')
    bot.send_photo(message.chat.id, photo)
    photo.close()


if __name__ == '__main__':
    bot.polling()
