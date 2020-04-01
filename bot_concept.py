import telebot
import os
from telebot import apihelper
import re

#regular for time
reg = re.compile('(:?\d\d:|\d:){0,1}(:?\d\d|\d){0,1}(:?:\d\d.\d|:\d.\d){1}')

#config
directory_save = r'/root/RABOTA/BOT_TG/NEW_COLLECTION/'
csv_data_dump = r'/root/RABOTA/BOT_TG/data_name.csv'
csv_data_training = r'/root/RABOTA/BOT_TG/data_training.csv'

'''
directory_save = r'/root/BOT/PHOTO/'
csv_data_dump = r'/root/BOT/data_name.csv'
csv_data_training = r'/root//BOT/data_training.csv'
'''

#global variable for writing in csv file
last_uuid = ''
last_id = ''
last_metrs = 0
last_time = ''
last_type = ''

#1128659144:AAFmr_DS-p-_iPRUk1Xc7U-Mv7edaWfz07M - Concept_2

apihelper.proxy = {'https': 'socks5://96.96.33.133:1080'}
bot = telebot.TeleBot('1128659144:AAFmr_DS-p-_iPRUk1Xc7U-Mv7edaWfz07M')

keyboard1 = telebot.types.ReplyKeyboardMarkup()
keyboard1.row('just row'), 
keyboard1.row('single distance', 'single time')
keyboard1.row('intervals distance', 'intervals time')

keyboard_start = telebot.types.ReplyKeyboardMarkup()
keyboard_start.row('Да', 'Нет')

keyboard_remove = telebot.types.ReplyKeyboardRemove()


priv_message = '''Привет, {}!!!

Тебя приветствует бот, призванный помочь отслеживать твои физические показатели и улучшать их. Но пока я только учусь, и у тебя есть возможность помочь мне. 

Для этого нужно отправить мне фотографию своих результатов, я задам тебе пару уточняющих вопросов, о том сколько метров ты прошёл и сколько времени это заняло. И уже в скором времени сам смогу отвечать на эти вопросы за тебя, я быстро учусь😉

Чтобы узнать результат тренировки, будь то простой “Just Row”  или “Select Workout”, нажми “Menu -> Memory -> List by Date” и пришли мне фотографию своих результатов. 

Если вдруг забудешь, то просто напиши мне /help или /start'''

help_message_print = '''Отправь мне фотографию своих результатов, я задам тебе пару уточняющих вопросов, о том сколько метров ты прошёл и сколько времени это заняло. И уже в скором времени сам смогу отвечать на эти вопросы за тебя, я быстро учусь😉

Чтобы узнать результат тренировки, будь то простой “Just Row”  или “Select Workout”, нажми “Menu -> Memory -> List by Date” и пришли мне фотографию своих результатов.
'''

types_training = ['single distance', 'single time', 'intervals distance', 'intervals time']

@bot.message_handler(commands=['start'])
def start_message(message):
    if not os.path.exists(csv_data_dump):
        open(csv_data_dump,'a').close()
    if not os.path.exists(csv_data_training):
        open(csv_data_training,'a').close()
    f = open(csv_data_dump, 'r')
    for st in f.readlines():
        idd = st.split(';')[3].strip()
        if idd == str(message.from_user.id):
            bot.send_message(message.chat.id, "Для проведения дальнейшей аналитики, отправляйте фотографии результатов.")
            return
    f.close()
    bot.send_message(message.chat.id, priv_message.format(message.from_user.username))
    bot.send_message(message.chat.id, 'Желаете ли Вы оставить свои данные для проведения дальнешего анализа?', reply_markup=keyboard_start)
#    bot.send_message(message.chat.id, 'Просто отправляйте мне фотографии')#, reply_markup=keyboard1)
#   print(message)

@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, help_message_print)

@bot.message_handler(content_types=['text'])
def registration(message):
    if message.text == 'Да':
        bot.send_message(message.chat.id, "Введите свою фамилию, имя и город(через пробел, на латинице)", reply_markup=keyboard_remove)
    elif message.text == 'Нет':
        bot.send_message(message.chat.id, 'Хорошо, для записи результатов Вашей тренировки отправляйте фотографии', reply_markup=keyboard_remove)
    elif message.text.split().__len__() == 3:
        try:
            with open(csv_data_dump, 'a') as cs:
                ms = message.text.split()
                ms.append(str(message.from_user.id))
                cs.write(';'.join(ms) + '\n')
        except:
            bot.send_message(message.chat.id, 'Введите данные на латинице!')
            return
        bot.send_message(message.chat.id, 'Отлично, отправляйте фотографии результатов для дальнейшего анализа.')
    elif message.text in types_training:
        bot.send_message(message.chat.id, 'Введите пройденное количество метров (total distance) и общее время (total time) через пробел.', reply_markup=keyboard_remove)
        global last_type
        last_type = message.text
    elif message.text.split().__len__() == 2:
        try:
            metrs, time = message.text.split()
            global last_metrs
            global last_time
            global last_id
            global last_uuid
            int(metrs)
            last_time = time
            last_metrs = metrs
            with open(csv_data_training, 'a') as f:
                a = []
                a.append(last_id)
                a.append(last_uuid)
                a.append(last_type)
                a.append(str(last_metrs))
                a.append(last_time)
                s = ';'.join(a) + '\n'
                f.write(s)
            last_uuid = ''
            last_id = ''
            last_metrs = 0
            last_time = ''
            last_type = ''
            bot.send_message(message.chat.id, 'Ваши данные приняты, спасибо. Отправляйте фотографии результатов для дальнейшего анализа.')
        except:
            bot.send_message(message.chat.id, 'Некорректные данные, попробуйте еще раз!')
            return
    elif message.text == 'Получить папки с фото.':
        for i in os.listdir(directory_save):
            bot.send_message(message.chat.id, i)
    
@bot.message_handler(content_types=['photo'])
def save_photo(message):

    global last_id
    last_id = str(message.from_user.id)
    global last_uuid
    
    dirr = directory_save + str(message.from_user.id)
    bot.send_message(message.chat.id, "Введите тип тренировки.", reply_markup=keyboard1)

    if not os.path.exists(dirr):
        os.mkdir(dirr)
    dirr += r'/'
    fileID = message.photo[-1].file_id
    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)
    last_uuid = str(fileID)
    with open(dirr + str(fileID) + '.jpeg', 'ab') as new_file:
        new_file.write(downloaded_file)

bot.polling(none_stop=True, timeout=123)