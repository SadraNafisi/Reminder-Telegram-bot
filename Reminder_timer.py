import re
from datetime import datetime
import telebot
from telebot import types
from database import TaskTable, TaskTableManagement, takeConfigScheduler




def is_valid_date(date_string):
    try:
        # Try to parse the date string
        datetime.strptime(date_string, '%Y/%m/%d')
        return True  # If parsing is successful, the format is valid
    except ValueError:
        return False  # If parsing fails, the format is invalid
def is_validate_relative_time(time_string):
    # Define the regex pattern for "number" (hour/min/sec)
    pattern = r'^\d+\s*(hour|min|sec)$'
    try:
        # Check if the time_string matches the pattern
        if re.match(pattern, time_string):
            return True  # Valid format
    except ValueError:
        return False  # Invalid format

def is_validate_time_format(time_string):
    try:
        # Attempt to parse the time_string
        datetime.strptime(time_string, '%H:%M:%S')
        return True  # Valid format
    except ValueError:
        return False  # Invalid format


bot = telebot.TeleBot('[REDACTED]')
class Task:
    def __init__(self):
        self.timetype =''
        self.date_or_relativetime=''
        self.time=''
        self.description=''

    def __str__(self):
        return (f'timetype : {self.timetype}\n'
                +('relativetime' if self.timetype == "Relative" else 'date')+f' : {self.date_or_relativetime}\n'
                f'time : {self.time}\n'
                f'description: {self.description}')

    def is_relative(self):
        if self.timetype == "Relative":
            return True
        else:
            return False

def store_task(message,tsk):
    scheduler = takeConfigScheduler()
    
    if isinstance(tsk, Task):
        task_table = TaskTable(chat_id=message.chat.id,timetype=tsk.timetype,date_or_relativetime=tsk.date_or_relativetime
        ,time=tsk.time,description=tsk.description,apscheduler_job_id=job.id)
    else:
        raise ValueError('Error:the parameter enter in store_task() is not object Task class')


def cancel_message(message):
    return bot.send_message(message.chat.id, 'the following'
                                             ' task has been canceled')

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
    tsk=Task()
    # msg=bot.reply_to(message,'there are two kind of time you can add. absolute time (date and time) and relative time (daily)\n'
    #                      'for absolute time it should be (abs,yyyy/mm/dd,hh:mm:ss, "description") format, f.g: abs,2025/03/08,14:05:02, meeting)\n'
    #                      'for relative time it should be (rel, "number"(sec/min/hour), hh:mm:ss, "description") format, f.g: '
    #                      'rel, 6 hour, 16:02:05, using med')
    msg= bot.reply_to(message,'what kind of timetype do you want create?'
                              'Relative or Absolute(rel/abs/cancel)?')
    bot.register_next_step_handler(msg,ask_timetype,tsk)
def ask_timetype(message,tsk):#should bring the question in here

    text = message.text
    timetype=''
    next_arg=''
    if(text.lower() =='rel'):
        timetype='Relative'
        next_arg=('relative time(("number" (hour/min/sec)) / cancel)\n f.g:'
                  'for each 6 hours you just write "6 hour"')
    elif(text.lower() == 'abs'):
        timetype = 'Absolute'
        next_arg = ('date ((yyyy/mm/dd)/cancel)\n f.g: 2025/03/08)')
    elif(text.lower() == 'cancel'):
        cancel_message(message)
        return
    else:
        msg=bot.send_message(message.chat.id,'your input was wrong\n'
                                             'remember the input should be "rel" or "abs"'
                                             'or you could cancel it by text "cancel"')
        bot.register_next_step_handler(msg,ask_timetype,tsk)
        return
    tsk.timetype=timetype
    msg=bot.send_message(message.chat.id,f'you choose{timetype} timetype! {next_arg} ')
    bot.register_next_step_handler(msg,ask_date_or_relativetime,tsk)
def ask_date_or_relativetime(message,tsk):
    text = message.text
    if(text.lower() == 'cancel'):
        cancel_message(message)
        return
    if ((tsk.timetype == 'Absolute' and is_valid_date(text)) or
            (tsk.timetype == 'Relative' and is_validate_relative_time(text))):
        tsk.date_or_relativetime = text
        msg=bot.send_message(message.chat.id, ('Relative' if tsk.is_relative() else 'Absolute')
                             +' time taken successfully')
    else:
        msg=bot.send_message(message.chat.id,('you enter date form wrong . remember the patern should be like'
                                         'this: "yyyy/mm/dd", please enter again or send "cancel" text.' if tsk.is_relative() == True
                                          else 'your relative time is wrong. remember the pattern should be'
                                          'like this:\n'
                                          '"number" (hour/min/sec) or cancel task by text "cancel"!'))
        bot.register_next_step_handler(msg,ask_date_or_relativetime,tsk)
        return
    bot.send_message(message.chat.id, 'what time do you want to '
                     + ('trigger' if tsk.timetype != 'Relative' else 'start from')+' ?'
                        ' you can cancel also by sending "cancel"!!')
    bot.register_next_step_handler(msg, ask_time, tsk)


# def ask_relativetime(message,tsk):#should bring the question in here
#     text = message.text
#     if (text.lower() == 'cancel'):
#         cancel_message(message)
#         return
#     if is_validate_relative_time(text):
#         tsk.date_or_relativetime = text
#         msg=bot.send_message(message.chat.id, 'relative time taken successfully')
#     else:
#         msg = bot.send_message(message.chat.id, 'your relative time is wrong. remember the pattern should be'
#                                           'like this:\n'
#                                           '"number" (hour/min/sec) or cancel task by text "cancel"!')
#         bot.register_next_step_handler(msg,ask_relativetime,tsk)

def ask_time(message,tsk):
    text = message.text
    if(text.lower() == 'cancel'):
        cancel_message(message)
        return
    if is_validate_time_format(text):
        tsk.time=text
        msg = bot.send_message(message.chat.id, ('Begin'if tsk.timetype=='Relative' else'The')+
                               'time has been taken successfully ')
    else:
        msg = bot.send_message(message.chat.id, 'the time format was wrong.'
                                                ' remeber the pattern is "h:m:s"')
        bot.register_next_step_handler(msg,ask_time,tsk)
        return
    bot.send_message(message.chat.id,'write you description about the task!')
    bot.register_next_step_handler(msg, ask_description, tsk)
    
def ask_description(message,tsk):
    text = message.text
    tsk.description = text
    bot.send_message(message.chat.id,'your task has been activated successfully!\n'
                                     'The task information:\n'
                                     ''+str(tsk))
    store_task(message,tsk)
# def ask_datetime(message):
    # args = text.split(',')
    # time_type=''
    # if(args[0].lower()== 'rel'):
    #     time_type = 'Relative'
    # elif(args[0].lower() == 'abs'):
    #     time_type = 'Absolute'


    # dml_Query(f"INSERT INTO tasks( chat_id , timetype , time , description) VALUES ({message.chat.id}, '{time_type}', '{args[1]}+{args[2]}', '{args[3]}')")
    # bot.send_message(message.chat.id,'information stored successfully!')

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
