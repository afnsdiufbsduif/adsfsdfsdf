import telebot
from telebot import types
import pyodbc

bot = telebot.TeleBot('7027008709:AAE9Ro8gC9iiuX8ALu9CLfTvp6EOpMYriOM')
__connect = pyodbc.connect(r'Driver={SQL Server};Server=DESKTOP-8FCVK9K\SQLEXPRESS;Database=bot;Trusted_Connection=yes;')
cursor = __connect.cursor()

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_action(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Все заказы')
    markup.add(btn1)
    
    bot.send_message(
        message.chat.id, 
        'Бот запущен. Вы можете просматривать новые заказы и все заказы.', 
        reply_markup=markup
    )


# Просмотр всех заказов
@bot.message_handler(func=lambda message: message.text == 'Все заказы')
def view_all_orders(message):
    cursor.execute("""
        SELECT p.ProjectID, p.Title, c.CategoryName, u.Username 
        FROM Projects p
        JOIN Categories c ON p.CategoryID = c.CategoryID
        JOIN Users u ON p.UserID = u.UserID
    """)
    orders = cursor.fetchall()
    
    if orders:
        response = "Все заказы:\n\n"
        for order in orders:
            response += f"ID: {order[0]}\nНазвание: {order[1]}\nКатегория: {order[2]}\nПользователь: @{order[3]}\n\n"
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, 'Нет доступных заказов.')



bot.polling(non_stop=True)
