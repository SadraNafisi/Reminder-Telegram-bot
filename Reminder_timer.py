import telebot
from telebot import types
def connect_database():
    import psycopg2
    conn = psycopg2.connect(database='postgres',
                            user='root',
                            host='himalayas.liara.cloud',
                            password='M5cdvDnzgYo8Y9sW9FDJz3ra',
                            port=31190)
    return conn
def retrieve_Query(query):
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    return rows
def dml_query(query): #data manuplating language form
    conn = connect_database()
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    conn.close()

bot = telebot.TeleBot('[REDACTED]')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('/add_task')
    item2 = types.KeyboardButton('/edit_task')
    item3 = types.KeyboardButton('/show_tasks')
    item4 = types.KeyboardButton('⬅️')
    markup.add(item1, item2 , item3, item4)
    bot.send_message(message.chat.id , ''
                                            'you can see /help for options.' , reply_markup=markup)
@bot.message_handler(commands=['add_task'])
def ask_task(message):
    msg=bot.reply_to(message,'there are two kind of time you can add. absolute time (date and time) and relative time (daily)\n'
                         'for absolute time it should be (abs,yyyy/mm/dd,hh:mm:ss, "description") format, f.g: abs,2025/03/08,14:05:02, meeting)\n'
                         'for relative time it should be (rel, "number"(sec/min/hour), hh:mm:ss, "description") format, f.g: '
                         'rel, 6 hour, 16:02:05, using med')
    bot.register_next_step_handler(msg,add_task)
def add_task(message):
    text = message.text
    args = text.split(',')
    time_type=''
    if(args[0].lower()== 'rel'):
        time_type = 'Relative'
    elif(args[0].lower() == 'abs'):
        time_type = 'Absolute'


    dml_query(f"INSERT INTO tasks( chat_id , timetype , time , description) VALUES ({message.chat.id}, '{time_type}', '{args[1]}+{args[2]}', '{args[3]}')")
    bot.send_message(message.chat.id,'information stored successfully!')

@bot.message_handler(commands=['help'])
def inform_commands(message):
    bot.send_message(message.chat.id, 'list of command:\n'
                                      '/start : initialize\n'
                                      '/help : seeing commands\n'
                                      '/about')
@bot.message_handler(commands=['about'])
def about_text(message):
    bot.reply_to(message, "A reminder of time for certain event of dates")


if __name__ == '__main__':
    bot.infinity_polling()
