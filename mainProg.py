import telebot
from bs4 import BeautifulSoup
import requests
from firebase import firebase
import json
import urllib.request

TOKEN = "Your own token"

#set up firebase connection
firebase = firebase.FirebaseApplication("Your own app",None)



bot = telebot.TeleBot(TOKEN)
stocks = []

@bot.message_handler(commands=['start','help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Hello and welcome to the Stock Checker Bot! I will get the latest price of the stock in your list and show it to you! If you want to add stocks to your list, go to /add. An example will be \"/add D05.SI\"!")
    checkUser = firebase.get("/Users",str(message.chat.id))
    if checkUser == None:
        print("outcome: No such account.. Creating one now...")
        bot.send_message(message.chat.id,"This is your first time using this bot! Use /add to add stocks! Remember to use the stock codes according to Yahoo Finance! Use /getprice to view the current stock prices!")
        firebase.post("/Users/"+str(message.chat.id),"")
    else:
        stocks = []
        bot.send_message(message.chat.id,"Welcome back! Use /getprice to view the current prices!")



@bot.message_handler(commands=["add"])
def add_stocks(message):
    '''
    user types in the code tgt with add,seperated by space
    '''
    stockToAdd = message.text.strip().split()
    validityCheck = requests.get(f"https://sg.finance.yahoo.com/quote/{stockToAdd[1]}/", allow_redirects=False)
    if validityCheck.status_code == 200:
        stocks.append(stockToAdd[1])
        firebase.post("/Users/"+str(message.chat.id),stockToAdd[1])
        bot.send_message(message.chat.id,f"{stockToAdd[1]} added to list")
        print(stocks)
    else:
        bot.send_message(message.chat.id,"Wrong code entered. Please try again")
    
@bot.message_handler(commands=["getprice"])
def get_price(messageO):
    message = ""
    stocks = []
    bot.send_message(messageO.chat.id,"Getting prices...")
    checkUser = firebase.get("/Users",str(messageO.chat.id))
    for i,j in checkUser.items():
            if j != "":
                stocks.append(j)
    for i in stocks:
        url = f"https://sg.finance.yahoo.com/quote/{i}/"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        price = soup.select("span[data-reactid*='14']")[0].text.strip()
        timing = soup.select("span[data-reactid*='18']")[0].text.strip()
        message += f"Price of {i} \n${price}, {timing} \n"
    bot.send_message(messageO.chat.id,message)

@bot.message_handler(func=lambda m: True)
def echo_all(message):
    bot.send_message(message.chat.id,message.text)


bot.polling()
