from pattern import is_outdated, is_date_today, is_time_expired, is_validate_relative_time, is_validate_time_format, tomorrow_date
from pattern import string_to_date, string_to_time
import telebot
from telebot import types
from datetime import datetime
from reminder_timer_db import TaskTable, TaskTableManagement, takeConfigScheduler

scheduler = takeConfigScheduler()
scheduler.start()
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
def send_notif(tsk,chat_id):
    bot.send_message(chat_id,f'alert ⚠️:\n {tsk.description}')
def store_task(message,tsk):
    timezone= 'Asia/Tehran'
    chat_id = message.chat.id
    if not(tsk.is_relative()):
        job=scheduler.add_job(send_notif,'date',run_date=tsk.date_or_relativetime.replace('/', '-')+' '+ tsk.time,
        args=[tsk, chat_id],timezone=timezone)
    else:
        hour,minute,second = tsk.date_or_relativetime.split(':')
        job = scheduler.add_job(send_notif,'interval',hours=int(hour),minutes=int(minute),seconds=int(second),
        start_date=datetime.combine((tomorrow_date() if is_time_expired(tsk.date_or_relativetime,tsk.time) else datetime.now().date()), string_to_time(tsk.time)),
        args=[tsk, chat_id],timezone=timezone)
    if isinstance(tsk, Task):
        task_table = TaskTable(chat_id=message.chat.id,timetype=tsk.timetype,date_or_relativetime=tsk.date_or_relativetime
        ,time=tsk.time,description=tsk.description,apscheduler_job_id=job.id)
        task_table.add_task()
    else:
        raise ValueError('the parameter entered in store_task() is not object Task class')


def cancel_message(message):
    return bot.send_message(message.chat.id, 'the following'
                                             ' task has been canceled')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('/add_task')
    item2 = types.KeyboardButton('/show_tasks')
    item3 = types.KeyboardButton('/delete_task')
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
def ask_timetype(message,tsk):

    text = message.text
    timetype=''
    next_arg=''
    if(text.lower() =='rel'):
        timetype='Relative'
        next_arg=('enter you interval time in "hour:min:sec" format\n f.g: for each 6 hour write: 6:0:0')
    elif(text.lower() == 'abs'):
        timetype = 'Absolute'
        next_arg = ('enter you date in ((yyyy/mm/dd)/cancel) form\n f.g: 2025/03/08)')
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
    try:
        if ((tsk.timetype == 'Absolute' and is_outdated(text)==False) or
            (tsk.timetype == 'Relative' and is_validate_relative_time(text))):
            tsk.date_or_relativetime = text
            msg=bot.send_message(message.chat.id, ('Relative' if tsk.is_relative() else 'Absolute')
                                +' time taken successfully')
                                
        else:
            msg=bot.send_message(message.chat.id,('your interval time is wrong. remember the pattern should be'
                                            'like this: hour:min:sec\n'
                                            ' or cancel task by text "cancel"!' if tsk.is_relative()
                                            else 'your date is outdated, please enter again or send "cancel" text.' ))
            bot.register_next_step_handler(msg,ask_date_or_relativetime,tsk)
            return
    except ValueError as e:
        msg=bot.send_message(message.chat.id,str(e)+'please try again! or send "cancel" text.')
        bot.register_next_step_handler(msg,ask_date_or_relativetime,tsk)
        return 

    
    bot.send_message(message.chat.id, 'what time do you want to '
                     + ('trigger' if tsk.is_relative()==False else 'start from')+' ?'
                        'you should time format like:"hour:min:sec" you can cancel also by sending "cancel"!!')
    bot.register_next_step_handler(msg, ask_time, tsk)

def ask_time(message,tsk):
    text = message.text
    if(text.lower() == 'cancel'):
        cancel_message(message)
        return

    if is_validate_time_format(text):
        if  tsk.is_relative()==False and is_time_expired(tsk.date_or_relativetime,text):
            msg = bot.send_message(message.chat.id,'The input time is expired, try enter another time')
            bot.register_next_step_handler(msg,ask_time,tsk)
            return 
        tsk.time=text
        msg = bot.send_message(message.chat.id, ('Begin'if tsk.is_relative() else'The')+
                               'time has been taken successfully ')
    else:
        msg = bot.send_message(message.chat.id, 'the time format or time range was wrong.'
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
@bot.message_handler(commands=['show_tasks'])
def list_tasks(message):
    tasks=TaskTableManagement().get_tasks_by_chat_id(message.chat.id)
    msg=''
    print(tasks)
    if tasks:
        msg='tasks format is the following format: timetype | date/relative time | description\n'
        for task in tasks:
            msg +=f'{task.timetype} | {task.date_or_relativetime} | {task.description}\n'
    else:
        msg='you dont have any task yet!'
    bot.send_message(message.chat.id, msg)

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
