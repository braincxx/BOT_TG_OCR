import telebot
import os
from telebot import apihelper
import re
import sqlite3

#regular for time total
reg = re.compile('(:?\d\d:|\d:){0,1}(:?\d\d|\d){0,1}(:?:\d\d.\d|:\d.\d){1}')
#regular for time relax
reg_relax = re.compile('(:?\d:\d\d|\d\d:\d\d)')
#regular for word
reg_word = re.compile('[^a-zA-Zа-яА-ЯёЁ]+')

#config
database_dir = r'/root/RABOTA/BOT_TG_OCR/bot_tg.db'
directory_save = r'/root/RABOTA/BOT_TG/NEW_COLLECTION/'
'''
directory_save = r'/root/RABOTA/BOT_TG/NEW_COLLECTION/'
csv_data_dump = r'/root/RABOTA/BOT_TG/data_name.csv'
csv_data_training = r'/root/RABOTA/BOT_TG/data_training.csv'
'''
'''
directory_save = r'/root/BOT/PHOTO/'
csv_data_dump = r'/root/BOT/data_name.csv'
csv_data_training = r'/root//BOT/data_training.csv'
'''


#init data_base 
conn = sqlite3.connect(database_dir, check_same_thread=False)
cur = conn.cursor()

if not os.path.exists(database_dir):
    print("DATABASE IS NOT EXISTS")
    exit(0) 

#global variable for writing in csv file


last_id_dic = {}

#1128659144:AAFmr_DS-p-_iPRUk1Xc7U-Mv7edaWfz07M - Concept_2

apihelper.proxy = {'https': 'socks5://96.96.33.133:1080'}
bot = telebot.TeleBot('1128659144:AAFmr_DS-p-_iPRUk1Xc7U-Mv7edaWfz07M')
#@Concept_2_bot
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

types_training = ['just row', 'single distance', 'single time']

def time_to_second(st):
    sec = 0 
    if '.' in st:
        full, ml = st.split('.')
    else:
        full = st
    full = [int(i) for i in full.split(":") if i is not '']
    full.reverse()
    for i in range(len(full)):
        sec += full[i] * 60 ** i
    return sec

@bot.message_handler(commands=['start'])
def start_message(message):
    data_name = cur.execute("select * from personal_data").fetchall()
    for st in data_name:
        if st[4] == message.from_user.id:
            bot.send_message(message.chat.id, "Для проведения дальнейшей аналитики, отправляйте фотографии результатов.")
            return
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
        bot.send_message(message.chat.id, "Введите свою фамилию, имя и город(через пробел, например, Иванов Иван Москва)", reply_markup=keyboard_remove)
    elif message.text == 'Нет':
        bot.send_message(message.chat.id, 'Хорошо, для записи результатов Вашей тренировки отправляйте фотографии', reply_markup=keyboard_remove)
    elif message.text.split().__len__() == 3:
        if reg_relax.fullmatch(message.text.split()[1]) and reg_relax.fullmatch(message.text.split()[0]):
            a, b, c = message.text.split()
            try:
                c = int(c)
                sec_1 = time_to_second(a)
                sec_2 = time_to_second(b)
                totally = sec_1 * c + sec_2 * (c - 1)
                query_time = "select total_time from base_training where id_record=%d" % (last_id_dic[str(message.chat.id)])
                time_full = cur.execute(query_time).fetchall()[0][0]
                time_full = time_to_second(time_full)
                if time_full != totally:
                    bot.send_message(message.chat.id, 'Данные времени не совпадают, введите корректные данные!')
                    return 
                query = "insert into intervals_time(id_ref, time_work, time_relax, count_sets) values (%d, '%s', '%s', %d)" %(last_id_dic[str(message.chat.id)], a, b, c)
            except:
                bot.send_message(message.chat.id, "Некоррректные данные, попробуйте еще раз!")
            cur.execute(query)
            conn.commit()
            last_id_dic.pop(str(message.chat.id))
            bot.send_message(message.chat.id, 'Ваши данные приняты, спасибо. Отправляйте фотографии результатов для дальнейшего анализа.')
            return
        elif reg_relax.fullmatch(message.text.split()[1]):
            a, b, c = message.text.split()
            try:
                a = int(a)
                c = int(c)
                total_meters = a * c
                query_2 = "select total_distance from base_training where id_record=%d" % (last_id_dic[str(message.chat.id)])
                total_base = int(cur.execute(query_2).fetchall()[0][0])
                if total_meters != total_base:
                    bot.send_message(message.chat.id, 'Данные дистанции не совпадают, введите корректные данные!')
                    return 
                query = "insert into intervals_distance(id_ref, meters, time_relax, count_sets) values (%d, '%d', '%s', %d)" %(last_id_dic[str(message.chat.id)], a, b, c)
            except:
                bot.send_message(message.chat.id, "Некоррректные данные, попробуйте еще раз!")
            cur.execute(query)
            conn.commit()
            last_id_dic.pop(str(message.chat.id))
            bot.send_message(message.chat.id, 'Ваши данные приняты, спасибо. Отправляйте фотографии результатов для дальнейшего анализа.')
            return

        
        try:
            a, b, c = [str(i) for i in message.text.split()]
        except:
            bot.send_message(message.chat.id, "Попробуйте еще раз!")
        if reg_word.search(a) is not None or reg_word.search(b) is not None or reg_word.search(c) is not None:
            bot.send_message(message.chat.id, "Попробуйте еще раз!")
            return
        quer = "insert into personal_data(Last_name, First_name, Town, Id_user) values('%s', '%s', '%s', %d)" %  (a, b, c, message.from_user.id)
        try:
            cur.execute(quer)
            conn.commit()
        except:
            bot.send_message(message.chat.id, 'bad open data_base')
            exit(0)
        bot.send_message(message.chat.id, 'Отлично, отправляйте фотографии результатов для дальнейшего анализа.')
   
    elif message.text == 'intervals distance':
        bot.send_message(message.chat.id, 'Введите пройденное количество метров (total distance) и общее время (total time) через пробел.(например 2000 10:10:10.3)', reply_markup=keyboard_remove)
        query = "update base_training set type_workout='%s' where id_record=%d" % (message.text, last_id_dic[str(message.chat.id)])
        cur.execute(query)
    elif message.text == 'intervals time':
        bot.send_message(message.chat.id, 'Введите пройденное количество метров (total distance) и общее время (total time) через пробел.(например 2000 10:10:10.3)', reply_markup=keyboard_remove)
        query = "update base_training set type_workout='%s' where id_record=%d" % (message.text, last_id_dic[str(message.chat.id)])
        cur.execute(query)
    elif message.text in types_training:
        bot.send_message(message.chat.id, 'Введите пройденное количество метров (total distance) и общее время (total time) через пробел.(например 2000 10:10:10.3)', reply_markup=keyboard_remove)
        query = "update base_training set type_workout='%s' where id_record=%d" % (message.text, last_id_dic[str(message.chat.id)])
        cur.execute(query)

    elif message.text.split().__len__() == 2:
        try:
            metrs, time = message.text.split()
            if not reg.fullmatch(time):
                bot.send_message(message.chat.id, 'Некорректное время, формат времени HH:MM:SS.MS(например 1:54.2), попробуйте еще раз!')
                return

            query = "update base_training set total_distance=%d where id_record=%d" % (int(metrs), last_id_dic[str(message.chat.id)])
            cur.execute(query)
            query = "update base_training set total_time='%s' where id_record=%d" % (time, last_id_dic[str(message.chat.id)])
            cur.execute(query)
            conn.commit()
            typ = cur.execute('select type_workout from base_training where id_record=%d' % (last_id_dic[str(message.chat.id)])).fetchall()[0][0]
            if typ == 'intervals time':
                bot.send_message(message.chat.id, 'Введите также интервал, время отдыха между подходами и их количество(через пробел, например, 3:00 1:00 4)')
                return
            elif typ == 'intervals distance':
                bot.send_message(message.chat.id, 'Введите также интервал дистанции, время отдыха между подходами и их количество(через пробел, например, 500 1:00 4)')
                return
            last_id_dic.pop(str(message.chat.id))
            bot.send_message(message.chat.id, 'Ваши данные приняты, спасибо. Отправляйте фотографии результатов для дальнейшего анализа.')
        except:
            bot.send_message(message.chat.id, 'Некорректные данные, попробуйте еще раз!')
            return
    elif message.text == 'Получить папки с фото.':
        for i in os.listdir(directory_save):
            bot.send_message(message.chat.id, i)
    
@bot.message_handler(content_types=['photo'])
def save_photo(message):

    global last_id_dic
    last_id_dic[str(message.from_user.id)] = ''
    
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

    query = "insert into base_training(id_user, uuid_photo) values(%d, '%s')" % (message.from_user.id, str(fileID))
    cur.execute(query)
    query = "select id_record from base_training where id_user=%d and uuid_photo='%s'" % (message.from_user.id, str(fileID))
    cur.execute(query)
    data = cur.fetchall()[0][0]
    last_id_dic[str(message.from_user.id)] = int(data)

bot.polling(none_stop=True, timeout=123)