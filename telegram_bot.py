from pattern import is_outdated, is_date_today, is_time_expired, is_validate_relative_time, is_validate_time_format, tomorrow_date
from pattern import string_to_date, string_to_time
import telebot
from telebot import types
from datetime import datetime
from database import TaskTable, TaskTableManagement, takeConfigScheduler
from deep_translator import GoogleTranslator

scheduler = takeConfigScheduler()
scheduler.start()

parse_mod='html'
bot = telebot.TeleBot('[REDACTED]')

def take_meesage_text(message):
    return GoogleTranslator(source='auto', target='en').translate(message.text)

def send_message(chat_id, text, parse_mode='html'):
    return bot.send_message(chat_id,GoogleTranslator(source='auto', target='fa').translate(text),parse_mode=parse_mode)

def cancel_suggestion():
    return '\nYou can cancel proccess by sending "<b>cancel</b>"'

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
    send_message(chat_id,f'alert ⚠️:\n {tsk.description}')
def store_task(message,tsk):
    timezone= 'Asia/Tehran'
    chat_id = message.chat.id
    if not(tsk.is_relative()):
        job=scheduler.add_job(send_notif,'date',run_date=tsk.date_or_relativetime.replace('/', '-')+' '+ tsk.time,
        args=[tsk, chat_id],timezone=timezone)
    else:
        hour,minute,second = tsk.date_or_relativetime.split(':')
        job = scheduler.add_job(send_notif,'interval',hours=int(hour),minutes=int(minute),seconds=int(second),
        start_date=datetime.combine((tomorrow_date() if is_time_expired(datetime.now().date(),tsk.time) else datetime.now().date()), string_to_time(tsk.time)),
        args=[tsk, chat_id],timezone=timezone)
    if isinstance(tsk, Task):
        task_table = TaskTable(chat_id=message.chat.id,timetype=tsk.timetype,date_or_relativetime=tsk.date_or_relativetime
        ,time=tsk.time,description=tsk.description,apscheduler_job_id=job.id)
        task_table.add_task()
    else:
        raise ValueError('The parameter entered in store_task() is not object Task class')
        return
    send_message(message.chat.id,'your task has been activated <b>successfully</b>!\n'
                                     'The task information:\n'
                                     '<b>'+str(tsk)+'</b>')


def cancel_message(message):
    return send_message(message.chat.id, 'The following'
                                         ' task has been canceled')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('/add_task')
    item2 = types.KeyboardButton('/show_tasks')
    item3 = types.KeyboardButton('/delete_task')
    markup.add(item1, item2 , item3)
    send_message(message.chat.id , ''
                                            'you can see /help for options.' , reply_markup=markup)
@bot.message_handler(commands=['add_task'])
def ask_task(message):
    tsk=Task()
    # msg=bot.reply_to(message,'there are two kind of time you can add. absolute time (date and time) and relative time (daily)\n'
    #                      'for absolute time it should be (abs,yyyy/mm/dd,hh:mm:ss, "description") format, f.g: abs,2025/03/08,14:05:02, meeting)\n'
    #                      'for relative time it should be (rel, "number"(sec/min/hour), hh:mm:ss, "description") format, f.g: '
    #                      'rel, 6 hour, 16:02:05, using med')
    msg= send_message(message.chat.id,'What kind of timetype do you want create?'
                              '<b>Relative</b> or <b>Absolute</b>(rel/abs)?'+cancel_suggestion())
    bot.register_next_step_handler(msg,ask_timetype,tsk)
def ask_timetype(message,tsk):

    text = take_meesage_text(message)
    timetype=''
    next_arg=''
    if(text.lower() in['rel', 'relative', 'r']):
        timetype='Relative'
        next_arg=('Enter your interval time in "<b>hour:min:sec</b>" format\n f.g: for each 6 hour write: 6:0:0')
    elif(text.lower() in ['abs', 'absolute','a']):
        timetype = 'Absolute'
        next_arg = ('Enter your date in "<b>year/month/day</b>" format\n f.g: 2025/03/08')
    elif(text.lower() == 'cancel'):
        cancel_message(message)
        return
    else:
        msg=send_message(message.chat.id,'Your input was <u>wrong</u>\n'
                                         'Remember the input should be "<b>rel</b>" or "<b>abs</b>"'+cancel_suggestion())
        bot.register_next_step_handler(msg,ask_timetype,tsk)
        return
    tsk.timetype=timetype
    next_question=('Enter your '+('interval time in "<b>hour:min:sec</b>" ' if tsk.is_relative() else 'date in "<b>year/month/day</b>" ')
                 +('format!\n f.g: ')+('For each 6 hour write: 6:0:0' if tsk.is_relative() else '2025/03/08'))
    msg=send_message(message.chat.id,f'You choose {timetype} timetype! {next_question}. {cancel_suggestion()} ')
    bot.register_next_step_handler(msg,ask_date_or_relativetime,tsk)
def ask_date_or_relativetime(message,tsk):
    text = take_meesage_text(message)
    if(text.lower() == 'cancel'):
        cancel_message(message)
        return
    try:
        if ((tsk.timetype == 'Absolute' and is_outdated(text)==False) or
            (tsk.timetype == 'Relative' and is_validate_relative_time(text))):
            tsk.date_or_relativetime = text
            msg=send_message(message.chat.id, ('Relative' if tsk.is_relative() else 'Absolute')
                                +' time taken successfully')

        else:
            msg=send_message(message.chat.id,('Your interval time is wrong. remember the pattern should be'
                                            'like this: <b>hour:min:sec</b>' if tsk.is_relative()
                                            else 'your date is outdated, please enter again!' )+cancel_suggestion())
            bot.register_next_step_handler(msg,ask_date_or_relativetime,tsk)
            return
    except ValueError as e:
        msg=send_message(message.chat.id,str(e)+f'remember the date pattern is : "<b>year/month/day</b>"! {cancel_suggestion()}')
        bot.register_next_step_handler(msg,ask_date_or_relativetime,tsk)
        return


    send_message(message.chat.id, 'What time do you want to '
                     + ('trigger' if tsk.is_relative()==False else 'start from')+' ?'
                        'You should send time format like:"<b>hour:minute:second</b>"'+cancel_suggestion())
    bot.register_next_step_handler(msg, ask_time, tsk)

def ask_time(message,tsk):
    text = take_meesage_text(message)
    if(text.lower() == 'cancel'):
        cancel_message(message)
        return

    if is_validate_time_format(text):
        if  tsk.is_relative()==False and is_time_expired(tsk.date_or_relativetime,text):
            msg = send_message(message.chat.id,'The input time is expired, try enter another time!'+cancel_suggestion())
            bot.register_next_step_handler(msg,ask_time,tsk)
            return
        tsk.time=text
        msg = send_message(message.chat.id, ('Begin'if tsk.is_relative() else'The date and ')+
                               'time has been taken successfully ')
    else:
        msg = send_message(message.chat.id, 'The time format or time range was wrong.'
                                                ' remeber the pattern is "<b>hour:minute:second</b>"')
        bot.register_next_step_handler(msg,ask_time,tsk)
        return

    send_message(message.chat.id,'Write you description about the task!')
    bot.register_next_step_handler(msg, ask_description, tsk)

def ask_description(message,tsk):
    text = take_meesage_text(message)
    tsk.description = text
    store_task(message,tsk)
@bot.message_handler(commands=['show_tasks'])
def list_tasks(message):
    tasks=TaskTableManagement().get_tasks_by_chat_id(message.chat.id)
    msg=''
    if tasks:
        msg='Task format: time type | date/relative time | description\n'
        counter=1
        for task in tasks:
            msg +=f'{counter}- {task.timetype} | {task.date_or_relativetime} | {task.description}\n'
            counter+=1
    else:
        msg='You dont have any task yet!'
    send_message(message.chat.id, msg)
    return tasks

@bot.message_handler(commands=['delete_task'])
def ask_delete_task(message):
    tasks=list_tasks(message)
    if tasks:
        msg=send_message(message.chat.id,'send the number of The task you want to remove from above list!')
        bot.register_next_step_handler(msg, check_delete_task,tasks)
    else:
        return
def check_delete_task(message,tasks):
    try:
        text = take_meesage_text(message)
        if not text.isnumeric():
            raise ValueError('That was not a number, try again! ')
        elif int(text)> len(tasks) or int(text)<1:
            raise ValueError('Your input number was wrong, try again! ')
        else:
            task=tasks[int(text)-1]
    except Exception as e:
        msg=send_message(message.chat.id,e)
        bot.register_next_step_handler(msg,check_delete_task,tasks)
        return
    msg = send_message(message.chat.id,f'Chosen task\n\n time type:{task.timetype} | date/relativetime:{task.date_or_relativetime} | description:{task.description}\n\n'
    'Are you sure you want to delete that?(y/n)')
    bot.register_next_step_handler(msg,delete_task,task)
def delete_task(message,task):
    text = take_meesage_text(message)
    if text.lower() in['yes','y','yeah']:
        scheduler.remove_job(task.apscheduler_job_id)##it will automaticly remove its task too.
        send_message(message.chat.id,'Task has been removed successfully! ')
    elif text.lower() in ['no','nope','n']:
        send_message(message.chat.id,'Proccess of removing task has been canceled! ')
    else:
        msg=send_message(message.chat.id,'The input was wrong, please try again! ')
        bot.register_next_step_handler(msg,delete_task,task)

@bot.message_handler(commands=['help'])
def inform_commands(message):
    send_message(message.chat.id, 'list of command:\n'
                                      '/start : initialize\n'
                                      '/help : seeing commands\n'
                                      '/about : what is this bot and how does it works\n')
@bot.message_handler(commands=['about'])
def about_text(message):
    send_message(message.chat.id, "This bot can be use for reminding an event for once or several time.")


if __name__ == '__main__':
    bot.infinity_polling()
