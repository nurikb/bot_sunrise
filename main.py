import telebot
from config import token
import requests
from bs4 import BeautifulSoup
from flask import Flask, request
import os


client = telebot.TeleBot(token=token)
server = Flask(__name__)

user_agency = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 OPR/78.0.4093.147'

# https://api.telegram.org/bot1550057543:AAGsIiMfET1vqwX74kFdpaIVI79MwMnAF0w/sendmessage?chat_id=472745426&text=hello%20world
URL = 'https://api.telegram.org/bot' + token + '/'


def get_html_data(name):
    search_url = 'https://rezka.ag/search/?do=search&subaction=search&q=' + name
    header = {'User-Agent': user_agency}

    r = requests.get(search_url, headers=header)
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
    client.process_new_messages([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    client.remove_webhook()
    client.set_webhook(url='https://sunrise-bot.herokuapp.com/')
    return "!", 200


if __name__ == '__main__':
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))


