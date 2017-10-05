# -*- coding: utf-8 -*-

import os
import re
import telebot
from flask import Flask, request
import google_drive_sheet
import var
import var_price
from telegraph import Telegraph

url_to_webhook = var.url_heroku_app
PORT = int(os.environ.get('PORT', 5000))
server = Flask(__name__)

#Авторизуем Телеграм-бота
token = var.token_telegram_bot
myBot = telebot.TeleBot(token)

#Авторизация Телеграф-аккаунта
telegraph = Telegraph(var.tg_access_token)

#_Раздел-01. Взаимодействие с Телеграф (Инстант Вью)
#Creates a search result InstantView-page for the vendor code. ТФ-страница рез-та поиска 7-знач. артикула.
def tf_vendor_code(result_message):
    text_message = 'Поиск по артикулу: ' + '\n' + str(result_message)
    text_1 = 'Артикул: '
    text_2 = 'Цена: '
    content = [
        {
            'tag': 'h4',
            'children': [result_message[0]]
        },
        {
            'tag': 'h4',
            'children': [{'tag': 'strong', 'children': [text_1]}, result_message[1]]
        },
        {
            'tag': 'h4',
            'children': [{'tag': 'strong', 'children': [text_2]}, result_message[2]]
        },
        {
            'tag': 'hr'
        },
        {
            'tag': 'blockquote',
            'children': ['➡ Заявку также можно отправить по E-MAIL: ', {'tag': 'strong', 'children': [var.contact_mail]}]
        }
    ]

    page_title = var_price.page_title_vendor
    response = telegraph.create_page(
        title=page_title,
        content=content
    )
    page = 'http://telegra.ph/{}'.format(response['path'])
    return page

#Телеграф страница с различными метками (DOM-элементами)
def tf_test_page():
    # text_message = 'Поиск по артикулу: ' + '\n' + str(result_message)

    content = [
        {
            'tag': 'p',
            'children': ['Сейчас я расскажу делать ', {'tag': 'strong', 'children': ['деньги каждый день']}, '. Мы метод ']
        },
        {
            'tag': 'blockquote',
            'children': ['*Cигнал - прогноз роста криптовалюты. 📣']
        },
        {
            'tag': 'br'
        },
        {
            'tag': 'p',
            'children': ['10% антилопа']
        },
        {
            'tag': 'a',
            'attrs': {'href': 'www.yandex.ru'},
            'children': ['maybe url here']
        },
        {
            'tag': 'hr'
        },
        {
            'tag': 'p',
            'children': ['30% антилопа']
        }
    ]

    response = telegraph.create_page(
        title='testing',
        content=content
    )
    page = 'http://telegra.ph/{}'.format(response['path'])
    return page

#Create InsView-page from data list. Телеграф страница из списка ключ-значение: начало-середина-конец. (ps: надо доделать)
def tf_page_ranks(dict_ranks):
    page_title = var_price.page_title_rank
    page_content = []
    content_start = [
        {
            'tag': 'blockquote',
            'children': ['Выберите нужный раздел и ', {'tag': 'strong', 'children': ['кликните']},
                         ', чтобы получить список товаров']
        },
        {
            'tag': 'hr'
        }
    ]
    page_content.extend(content_start)

    content_main = []
    for y in range(len(dict_ranks)):
        score = str(y+1)
        rank_title = dict_ranks[y]['title']
        row = score + '. ' + rank_title
        data = {
            'tag': 'h3',
            'children': [row]
        }
        content_main.append(data)
    page_content.extend(content_main)

    content_end = [
        {
            'tag': 'hr'
        },
        {
            'tag': 'blockquote',
            'children': ['➡ Заявку также можно отправить по E-MAIL: ', {'tag': 'strong', 'children': ['mail@mail.om']}]
        }
    ]
    page_content.extend(content_end)

    response = telegraph.create_page(
        title=page_title,
        content=page_content
    )
    page = 'http://telegra.ph/{}'.format(response['path'])
    return page

#_Раздел-02. Взаимодействие с Телеграм Ботом.
#_Команды Бота должны идти вначале кода.
@myBot.message_handler(commands=['start'])
def send_welcome(message):
    myBot.reply_to(message, 'Добро пожаловать') #TODO: change text

@myBot.message_handler(commands=['help'])
def send_help(message):
    myBot.reply_to(message, 'Раздел Помощи: описание функционала') #TODO: change text

@myBot.message_handler(commands=['price'])
def send_menu_category(message):
    # msg_answer = tf_page_ranks(google_drive_sheet.get_all_ranks())    #Здесь создается с нуля создать, но надо ждать ответ на запрос
    tf_page_path = google_drive_sheet.get_cell_value('D1')  #А так быстрее: ссылки на готовые ТФ-страницы
    # tf_page_path = var_price.page_rank
    msg_answer = tf_page_path
    myBot.reply_to(message, msg_answer)

@myBot.message_handler(commands=['dvigateli'])
def send_menu_category(message):
    tf_page_path = var_price.page_motors
    msg_answer = tf_page_path
    myBot.reply_to(message, msg_answer)

@myBot.message_handler(func=lambda message: True)
def handle_text(message):
    # находим первое совпадение (7-значный Артикул)
    vendor_found = re.search(r'\d{7}', str(message.text))
    if vendor_found:
        myBot.send_message(message.from_user.id, "Найден артикул: " + str(vendor_found.group(0))
                           + '. Идёт поиск в прайсе.')

        #Запускаем поиск в Прайсе по данному Артикулу
        result_found = google_drive_sheet.find_by_sheet(vendor_found.group(0))
        # myBot.send_message(message.from_user.id, 'Результат: ' + str(result_found))
        myBot.send_message(message.from_user.id, tf_vendor_code(result_found))
    else:
        myBot.send_message(message.from_user.id, 'Ваш текст не содержит 7-значный артикул')

# @server.route("/")
# def main():
#     #Стартуем Бот
#     myBot.polling(none_stop=True, interval=0)
#
# if __name__ == '__main__':
#     main()

#Ниже этого коммента для запуска ч/з Heroku
@server.route('/' + token, methods=['POST'])
def get_message():
    myBot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "POST", 200

@server.route("/")
def web_hook():
    myBot.remove_webhook()
    myBot.set_webhook(url=url_to_webhook + token)
    return "CONNECTED", 200

server.run(host="0.0.0.0", port=PORT, debug=True)
