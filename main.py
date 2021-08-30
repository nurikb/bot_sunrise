import telebot
from config import token
import requests
from bs4 import BeautifulSoup
from flask import Flask, request
from multiprocessing import Process
import re
import os
import json

client = telebot.TeleBot(token=token)
server = Flask(__name__)

URL = 'https://api.telegram.org/bot' + token + '/'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 OPR/78.0.4093.147",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
}


def get_link(html, mname):
    link_list = []
    soup = BeautifulSoup(html, 'lxml')
    ts = soup.find('div', class_='row items').find_all('div', class_='col-xs-2 item')
    for name in ts[:5]:
        link_list.append(name.find('a')['href'])
    return link_list


def get_data(url):
    response = requests.get(url, headers=headers)
    return response.text


def send_link_ts(message):
    client_message = message.text
    client_id = message.chat.id
    ts_search_url = 'https://www.ts.kg/show/search/' + client_message.replace(' ', '%20')
    req_data = get_data(ts_search_url)
    link_list = json.loads(req_data)
    for link in link_list:
        if link['name'].lower().startswith(client_message.lower()):
            client.send_message(client_id, 'https://www.ts.kg' + link['url'])
        elif ' ' in client_message and client_message.lower() in link['name'].lower():
            client.send_message(client_id, 'https://www.ts.kg' + link['url'])


def send_link_kb(message):
    client_message = message.text
    client_id = message.chat.id
    kb_search_url = 'https://kinobase.org/search?query=' + client_message.replace(' ', '+')

    req_data = get_data(kb_search_url)
    kb_link_list = get_link(req_data, client_message)

    for link in kb_link_list:
        client.send_message(client_id, 'https://kinobase.org' + link)


@client.message_handler(commands=['start'])
def send_welcome(message):
    client.reply_to(message, 'добро пожаловать')


@client.message_handler(content_types=['text'])
def get_text(message):
    Process(target=send_link_kb, args=(message,)).start()
    Process(target=send_link_ts, args=(message,)).start()


@server.route("/" + token, methods=['POST'])
def get_message():
    client.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "get message", 200


@server.route("/")
def webhook():
    client.remove_webhook()
    client.set_webhook(url='https://sunrise-bot.herokuapp.com/'+ token)
    return "set token", 200


if __name__ == '__main__':
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
