import telebot
from telebot import types
import pyodbc

bot = telebot.TeleBot('7243621496:AAHbGXQejejtWj0eweks3H4sGpj2GPjkhMA')
__connect = pyodbc.connect(r'Driver={SQL Server};Server=DESKTOP-8FCVK9K\SQLEXPRESS;Database=bot;Trusted_Connection=yes;')
cursor = __connect.cursor()

# Глобальные переменные для хранения временных данных пользователя
user_data = {}

def create_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Заказать проект')
    btn2 = types.KeyboardButton('Отзывы')
    btn3 = types.KeyboardButton('Связаться с менеджером')
    btn4 = types.KeyboardButton('Реферальная система')
    markup.row(btn1)  
    markup.row(btn2, btn3, btn4)  
    return markup

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_action(message):
    markup = create_markup()
    
    bot.send_message(
        message.chat.id, 
        '<b>🎓 Ready+ — Ваша надёжная поддержка в учебных проектах!</b>\n\nМы с друзьями уже более 5 лет работаем в сфере курсовых проектов, рефератов и других учебных работ. Наша команда решила запустить собственный проект <b>Ready+</b>, чтобы сделать помощь в учебе еще более доступной и удобной.\n\n🔥 <b>Почему именно мы?</b>\n- <b>Опыт:</b> Более 5 лет успешной работы.\n- <b>Экономия:</b> Вы покупаете проект без лишних наценок и переплат за работу менеджеров.\n- <b>Удобство:</b> Все необходимые услуги доступны в нашем Telegram боте.\n\n💼 <b>Гарантии и поддержка:</b>\n- <b>Гарантия 30 дней:</b> Если что-то не понравится, мы готовы внести необходимые корректировки абсолютно бесплатно.\n- <b>На связи 24/7:</b> В отличие от других сайтов, наша команда всегда готова помочь вам в любое время суток.\n\nПрисоединяйтесь к <b>Ready+</b> и решайте учебные задачи легко и быстро! 🚀', 
        parse_mode='HTML', 
        reply_markup=markup 
    )

# Обработчик нажатий на кнопки
@bot.message_handler(func=lambda message: True)
def on_click(message):
    if message.text == 'Заказать проект':
        markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, "Начинаем оформление заказа...", reply_markup=markup)
        
        # Сохраняем пользователя
        save_user(message)
        ask_category(message)
    elif message.text == 'Отзывы':
        bot.send_message(message.chat.id, 'Вы выбрали "Отзывы".')
    elif message.text == 'Связаться с менеджером':
        bot.send_message(message.chat.id, 'Вы выбрали "Связаться с менеджером".')
    elif message.text == 'Реферальная система':
        bot.send_message(message.chat.id, 'Вы выбрали "Реферальная система".')
    else:
        bot.send_message(message.chat.id, 'Пожалуйста, выберите одну из доступных опций.')

def save_user(message):
    user_id = message.from_user.id  
    username = message.from_user.username  
    if username is None:
        username = f'ID{user_id}'  

    # Проверяем, существует ли пользователь в базе данных
    cursor.execute("SELECT UserID FROM Users WHERE Username = ?", username)
    user = cursor.fetchone()

    if user is None:
        cursor.execute("INSERT INTO Users (Username) VALUES (?)", username)
        __connect.commit()
        user_id = cursor.execute("SELECT UserID FROM Users WHERE Username = ?", username).fetchone()[0]
    else:
        user_id = user[0]
    
    user_data[message.chat.id] = {'user_id': user_id}

def ask_category(message):
    # Спрашиваем пользователя категорию
    msg = bot.send_message(message.chat.id, 'Введите категорию проекта:')
    bot.register_next_step_handler(msg, receive_category)

def receive_category(message):
    # Сохраняем введенную категорию
    user_data[message.chat.id]['category'] = message.text
    bot.send_message(message.chat.id, f'Категория "{message.text}" успешно записана.')

    # Теперь спрашиваем название проекта
    ask_title(message)

def ask_title(message):
    # Спрашиваем пользователя название проекта
    msg = bot.send_message(message.chat.id, 'Введите название проекта:')
    bot.register_next_step_handler(msg, receive_title)

def receive_title(message):
    # Сохраняем введенное название
    user_data[message.chat.id]['title'] = message.text
    bot.send_message(message.chat.id, f'Название проекта "{message.text}" успешно записано.')

    # Запись данных в базу данных
    save_project_to_db(message)

def save_project_to_db(message):
    user_id = user_data[message.chat.id].get('user_id')
    category = user_data[message.chat.id].get('category')
    title = user_data[message.chat.id].get('title')

    if user_id is None or category is None or title is None:
        bot.send_message(message.chat.id, 'Ошибка: недостающие данные для сохранения проекта.')
        return
    
    # Найти или создать категорию в базе данных
    cursor.execute("SELECT CategoryID FROM Categories WHERE CategoryName = ?", category)
    category_id = cursor.fetchone()
    
    if category_id is None:
        cursor.execute("INSERT INTO Categories (CategoryName) VALUES (?)", category)
        __connect.commit()
        category_id = cursor.execute("SELECT CategoryID FROM Categories WHERE CategoryName = ?", category).fetchone()[0]
    else:
        category_id = category_id[0]
    
    # Добавить проект в базу данных
    cursor.execute("INSERT INTO Projects (Title, CategoryID, UserID) VALUES (?, ?, ?)", title, category_id, user_id)
    __connect.commit()

    bot.send_message(message.chat.id, f'Проект "{title}" успешно сохранен в базе данных.', reply_markup=create_markup())

bot.polling(non_stop=True)
