import telebot
from config import token
import requests
from bs4 import BeautifulSoup
from flask import Flask, request
import os
from fake_useragent import UserAgent


ua = UserAgent()


client = telebot.TeleBot(token=token)
server = Flask(__name__)

URL = 'https://api.telegram.org/bot' + token + '/'


def get_html_data(name):
    search_url = 'https://rezka.ag/search/?do=search&subaction=search&q=' + name
    header = {'User-Agent': ua}

    r = requests.get(search_url, headers=header)
    print(r.request.body)
    return r.text


def get_link(html, mname):
    link_list = []
    soup = BeautifulSoup(html, 'lxml')
    ts = soup.find('div', class_='b-content__inline_items').find_all('div', class_='b-content__inline_item')
    for name in ts:
        if name.find('img')['alt'].lower() == mname.lower():
            link_list.append(name.find('a')['href'])
            return link_list
        else:
            link_list.append(name.find('a')['href'])
    return link_list


@client.message_handler(commands=['start'])
def send_welcome(message):
    client.reply_to(message, 'добро пожаловать')


@client.message_handler(content_types=['text'])
def get_text(message):
    client_message = message.text
    link_list = get_link(get_html_data(client_message), client_message)
    if len(link_list) > 5:
        for link in link_list[:5]:
            client.reply_to(message.chat.id, link)
    else:
        for link in link_list:
            client.send_message(message.chat.id, link)


@server.route("/" + token, methods=['POST'])
def getMessage():
    client.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "get message", 200


@server.route("/")
def webhook():
    client.remove_webhook()
    client.set_webhook(url='https://sunrise-bot.herokuapp.com/'+ token)
    return "set token", 200


if __name__ == '__main__':
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
