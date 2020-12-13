import pyowm #API позволяющее получить погоду
import telebot
import random
from telebot import types #для добавления кнопок
from bs4 import BeautifulSoup #позволяет легко парсить сайты
import requests as req #позволяет получить код HTML по ссылке сайта
import re # регулярные выражения
import os
os.system('chcp 65001') #была проблема с кодировкой при парсинге, единственное решение которое помогло энкодить в UTF-8

#30 цитат
quote=[] #список цитат
author=[]#список авторов цитат
def parsing_quotes():
    url='https://resheto.net/raznosti/143-pozitivnye-tsitaty-na-kazhdyj-den'
    response = req.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    quotes = soup.find_all('em')
    authors = soup.find_all('span',class_='bol')

    authors.pop(6) #удаляем лишний эллемент
    for i in range(len(quotes)):
        quote.append(quotes[i].text)
        author.append(authors[i].text)
parsing_quotes()

#114 стихотворений
stixs=[]#список стихотворений
names=[]#cписок авторов и названий стихотворений
def parsing_stixs():
    url = 'https://poemata.ru/rating/russian/'
    response = req.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, "html.parser")
    for link in soup.findAll('a',class_="topbig"):
        link='https://poemata.ru'+link.get('href')
        try:
            res=req.get(link)
            res.encoding='utf=8'
            soup_link=BeautifulSoup(res.text,"html.parser")
            stix=soup_link.find_all('div',class_="preline")
            name = soup_link.find_all('h1')
            names.append(re.sub('</span>',' ----',str(name)[11:-6]))
            stixs.append(re.sub('<p>','',re.sub('</p>','\n',str(stix)[22:-11])))
        except:
            continue
parsing_stixs()

owm =pyowm.OWM('b3377cb02dafa025857e3fdc8b022828') #токен, необходимый для получения погоды

token='1313378892:AAHD3klFSAvNdC9508OWTY6aZzCRq74zNQw' #токен бота
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start','help']) #быстрые команды, будут выполняться при вводе /start или /help
def start(message):
    bot.send_message(message.from_user.id, 'Привет!\nВот что ты можешь получить от меня:'
                                           '\n---Погоду\n---Цитату\n---Стихотворение'
                                           '\nТакже ты можешь добавить города для быстрого получения погоды в них:'
                                           '\n---Напиши /city'
                                           '\nИли удалить уже добавленные:'
                                           '\n---Напиши /delcity'
                                           '\nЕсли захочешь увидеть это сообщение еще раз:'
                                           '\n---Напиши /start или /help'
                                           '\nВведи что-нибудь')

@bot.message_handler(commands=['city']) #будет выполняться при вводе /city
def start(message):
    bot.send_message(message.from_user.id, 'Эта команда позволяет добавить город для дальнейшего быстрого получения погоды в нем\nВведи желаемый город')
    bot.register_next_step_handler(message, get_town)

@bot.message_handler(commands=['delcity']) #будет выполняться при вводе /delcity
def start(message):
    if message.from_user.id in city:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for i in city[message.from_user.id]:
            markup.add(i)
        bot.send_message(message.from_user.id, 'Эта команда позволяет удалить город из быстрого получения погоды'
                                               '\nВыберите город, который хотите удалить',reply_markup=markup)
        bot.register_next_step_handler(message, del_town)
    else:
        bot.send_message(message.from_user.id,'У вас нет добавленных городов')

city={}

def del_town(message):
    id=message.from_user.id
    if len(city[id])==1:
        del city[id]
    else:
        city[id]=[v for v in city[id] if v!=message.text]
    bot.reply_to(message,"Город успешно удален")

def get_town(message):
    id=message.from_user.id
    try:
        wo = owm.weather_at_place(message.text).get_weather()
        if id in city:
            city[id].append(message.text)
        else:
            city[id] = [message.text]
        bot.reply_to(message, 'Город успешно добавлен')
    except:
        bot.reply_to(message,'Такого города не существует')

@bot.message_handler(content_types=['text']) #функция выполняющаяся при каждом вводе текстового сообщения
def content(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    itembtn1 = types.KeyboardButton('Узнать погоду')
    itembtn2 = types.KeyboardButton('Получить цитату')
    itembtn3 = types.KeyboardButton('Хочу стихотворение')
    markup.add(itembtn1,itembtn2,itembtn3) #добавление кнопок
    print(message.from_user)
    bot.send_message(message.from_user.id,'Чем могу помочь?', reply_markup=markup)
    bot.register_next_step_handler(message, get_city)
    bot.register_next_step_handler(message, get_quote)
    bot.register_next_step_handler(message, get_stix)


def get_city(message): # приглашает ввести желаемый город
    if message.text=='Узнать погоду':
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        if message.from_user.id in city:
            print(city[message.from_user.id])
            for i in city[message.from_user.id]:
                markup.add(i)
        bot.send_message(message.from_user.id, "Введи город, для которого хочешь узнать погоду",reply_markup=markup)
        bot.register_next_step_handler(message, get_temperature)

def get_temperature(message): #выводит температуру
    city1=message.text
    try:
        wo = owm.weather_at_place(city1).get_weather()
        temp = wo.get_temperature('celsius')
        temp_now=temp['temp']
        temp_min=temp['temp_min']
        temp_max=temp['temp_max']
        bot.send_message(message.from_user.id,"В городе " +str(city1)+ " сейчас " + str(temp_now) +
                         "°С\nМин: "+str(temp_min)+'°С     '+'Макс: '+str(temp_max)+'°С')
    except:
        bot.send_message(message.from_user.id,"Такого города не существует")

def get_stix(message):  #достает из списка случайное стихотворение
    if message.text=='Хочу стихотворение':
        t = random.randint(0, len(stixs))
        bot.send_message(message.from_user.id, '*' + names[t] + '*\n\n'+stixs[t],
                         parse_mode="Markdown")

def get_quote(message): #достает из списка цитату
    if message.text=='Получить цитату':
        t=random.randint(0, len(quote))
        bot.send_message(message.from_user.id,str(quote[t])+'\n--'+'*'+str(author[t])+'*',parse_mode= "Markdown")


bot.polling(none_stop=True, interval=0) #необходимо для непрерыной работы бота