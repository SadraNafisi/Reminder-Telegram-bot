from pattern import is_outdated, is_date_today, is_time_expired, is_validate_relative_time, is_validate_time_format, tomorrow_date, today_date
from pattern import string_to_date, string_to_time,today_date_string,tomorrow_date_string
import telebot
from telebot import types
from datetime import datetime,date
from database import TaskTable, TaskTableManagement, takeConfigScheduler, UserTable, UserTableManager, Job, JobManager
from translation import translate_with_regex,translate
import pytz

scheduler = takeConfigScheduler()
scheduler.start()
parse_mod='html'
bot = telebot.TeleBot('[REDACTED]')

class Task:
    def __init__(self):
        self.timetype =''
        self.date_or_relativetime=''
        self.time=''
        self.description=''

    def __str__(self):
        return (f'time type : {self.timetype}\n'
                +('relativetime' if self.timetype == "Relative" else 'date')+f' : {self.date_or_relativetime}\n'
                f'time : {self.time}\n'
                f'description: ^*{self.description}*^')

    def is_relative(self):
        if self.timetype == "Relative":
            return True
        else:
            return False

def get_user_lang(chat_id):
    if user_lang.get(chat_id) is None:
        user,status=UserTableManager().get_or_create_user(chat_id=chat_id)
        if status:
            user = UserTableManager().get_user(chat_id=chat_id)
        user_lang[chat_id]=user.language
    return user_lang[chat_id]

def get_user_tz(chat_id):
    if user_tz.get(chat_id) is None:
        user,status = UserTableManager().get_or_create_user(chat_id=chat_id)
        if status:
            user = UserTableManager().get_user(chat_id=chat_id)
        user_tz[chat_id]=user.timezone
    return user_tz[chat_id]

def take_meesage_text(message,translation=True):
    if(get_user_lang(message.chat.id) == 'en') or translation == False :
        return message.text
    else:
        return translate(message.text)

def send_message(chat_id, text, parse_mode='html',reply_markup=None):
    lang = get_user_lang(chat_id)
    if(lang =='en'):
        text=text.replace('*^','')
        text = text.replace('^*','')
        return bot.send_message(chat_id,text,parse_mode=parse_mode,reply_markup=reply_markup)
    else:
        return bot.send_message(chat_id,translate_with_regex(text,lang),parse_mode=parse_mode,reply_markup=reply_markup)

def cancel_suggestion():
    return '\nYou can cancel proccess by sending "<b>cancel</b>"'

def cancel_message(message):
    return send_message(message.chat.id, 'The creating'
                                         ' task process has been canceled!')
def create_ReplyKeyboard(buttons=[]):
    keyboard=types.ReplyKeyboardMarkup(resize_keyboard=True)
    for button in buttons:
        keyboard.add(button)
    keyboard.add(types.KeyboardButton('cancel'))
    return keyboard
def choose_from_list(arr,number):
    if not number.isnumeric():
        raise ValueError(f'The sending text was not a number')
    elif int(number) not in range(0,len(languages)+1):
        raise ValueError(f'The sending number is not in options.')
    else:
        return arr[int(number)-1]



@bot.message_handler(commands=['start'])
def ask_lang(message):
    msg = send_message(message.chat.id,'Please enter your language number:\n 1-🇺🇸english\n 2-🇮🇷farsi')
    bot.register_next_step_handler(msg,set_lang)

def set_lang(message):
    text = take_meesage_text(message)
    try:

        lang = user_lang[message.chat.id] = choose_from_list(languages,text)
        UserTableManager().create_or_update_user(UserTable(chat_id=message.chat.id,language=lang))
        send_message(message.chat.id,f'Now the language is ^*{lang}*^.')
    except ValueError as e:
        msg =send_message(message.chat.id,str(e))
        ask_lang(msg)
        return
    ask_timezone(message)
def ask_timezone(message):
    tz=pytz.all_timezones
    general_tz=['Asia/Tehran','America/Los_Angeles','Europe/Berlin'
    ,'Europe/Amesterdam','Australia/Sydney','Europe/Paris','Europe/Moscow']
    # for timezone in general_tz:
    #     tz.remove(timezone)
    # tz=general_tz + tz
    timezones_str=''
    for index,timezone in enumerate (general_tz):
        timezones_str += f'{index+1} : {timezone} \n'
    msg= send_message(message.chat.id,f'enter your timezone area(continent/capital city):\n{timezones_str}')
    bot.register_next_step_handler(msg,set_timezone,general_tz)
def set_timezone(message,tz):
    text = take_meesage_text(message)
    try:
        timezone = user_tz[message.chat.id] = choose_from_list(tz,text)
        UserTableManager().create_or_update_user(UserTable(chat_id=message.chat.id,timezone=timezone))
        send_message(message.chat.id,f'The timezone set on {timezone}')
    except ValueError as e:
        msg =send_message(message.chat.id,str(e))
        ask_timezone(msg)
        return

# def send_welcome(message):
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     item1 = types.KeyboardButton('/add_task')
#     item2 = types.KeyboardButton('/show_tasks')
#     item3 = types.KeyboardButton('/delete_task')
#     markup.add(item1, item2 , item3)
#     send_message(message.chat.id , ''
#                                             'you can see /help for options.' , reply_markup=markup)


@bot.message_handler(commands=['add_task'])
def ask_task(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    relative_button = types.InlineKeyboardButton("Relative", callback_data='relative')
    absolute_button = types.InlineKeyboardButton("Absolute", callback_data='absolute')
    cancel_button = types.InlineKeyboardButton('Cancel', callback_data='cancel')
    markup.add(relative_button, absolute_button,cancel_button)
    send_message(message.chat.id, 'What kind of time type do you want to create?', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data =='cancel')
def cancel_call(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    return send_message(call.message.chat.id, 'The creating'
                                         ' task process has been canceled!')

@bot.callback_query_handler(func=lambda call: call.data in ['relative', 'absolute'])
def ask_timetype(call):
    global tsk
    tsk = Task()
    if call.data == 'relative':
        tsk.timetype = 'Relative'
    else:
        tsk.timetype = 'Absolute'

    bot.delete_message(call.message.chat.id, call.message.message_id)
    # Send the next question
    next_question=('Enter your '+('interval time in "<b>hour:minute:second</b> format! " ' if tsk.is_relative() else 'date in "<b>year/month/day</b>" format! '
                    'you could also send "<b>today</b>" or "<b>tomorrow</b>" or just date ')
                 +('\n for example: ')+('For each 6 hour write: 6:0:0' if tsk.is_relative() else '2025/03/08'))

    markup=None
    if not tsk.is_relative():
        markup = types.InlineKeyboardMarkup(row_width=2)
        cancel_button = types.InlineKeyboardButton('Cancel', callback_data='cancel')
        today_button = types.InlineKeyboardButton('Today', callback_data='today')
        tomorrow_button = types.InlineKeyboardButton('Tomorrow', callback_data='tomorrow')
        date_button = types.InlineKeyboardButton('Date', callback_data='date')
        markup.add(today_button)
        markup.add(tomorrow_button)
        markup.add(date_button)
        markup.add(cancel_button)
    else:
        bot.register_next_step_handler(call.message, ask_date_or_relativetime)
    msg = send_message(call.message.chat.id, f'You choose {tsk.timetype} timetype! {next_question}. {cancel_suggestion()} ',reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ['today', 'tomorrow'])
def handle_date_selection(call):
    if call.data == 'today':
        date_selected = today_date_string()
    else:
        date_selected = tomorrow_date_string()
    tsk.date_or_relativetime = date_selected
    bot.delete_message(call.message.chat.id, call.message.message_id)
    send_message(call.message.chat.id, f'You selected: {date_selected}. Now please enter the time in "<b>hour:minute:second</b>" format.{cancel_suggestion()}',
    reply_markup=create_ReplyKeyboard())
    bot.register_next_step_handler(call.message, ask_time, tsk)


@bot.callback_query_handler(func=lambda call: call.data == 'date')
def set_date(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    msg=send_message(call.message.chat.id, f'You choose date. Now please send the date in "<b>year/month/day</b>" format. '+ cancel_suggestion(),
    reply_markup=create_ReplyKeyboard())
    bot.register_next_step_handler(msg, ask_date_or_relativetime)

def ask_date_or_relativetime(message):
    text = take_meesage_text(message)
    if(text.lower() == 'cancel'):
        cancel_message(message)
        return
    try:
        if ((tsk.timetype == 'Absolute' and is_outdated(text,get_user_tz(message.chat.id))==False) or
            (tsk.timetype == 'Relative' and is_validate_relative_time(text))):
            tsk.date_or_relativetime = text
            msg=send_message(message.chat.id, ('Relative' if tsk.is_relative() else 'Absolute')
                                +' time is recorded successfully')
        else:
            msg=send_message(message.chat.id,('Your relative time format is wrong. remember the pattern should be'
                                            'like this: "<b>hour:minute:second</b>"' if tsk.is_relative()
                                            else 'your date is outdated, please enter again!' )+cancel_suggestion(),reply_markup=create_ReplyKeyboard())
            bot.register_next_step_handler(msg,ask_date_or_relativetime)
            return
    except ValueError as e:
        msg=send_message(message.chat.id,str(e)+f'remember the date pattern is : ^*"<b>year/month/day</b>"*^! {cancel_suggestion()}',reply_markup=create_ReplyKeyboard())
        bot.register_next_step_handler(msg,ask_date_or_relativetime)
        return
    send_message(message.chat.id, 'What time do you want to '
                     + ('trigger' if tsk.is_relative()==False else 'start from')+' ?'
                       f'You should send time format like:^*"<b>hour:minute:second</b>"*^ remember your timezone location is <b>{get_user_tz(message.chat.id)}</b> {cancel_suggestion()}'
                        ,reply_markup=create_ReplyKeyboard())
    bot.register_next_step_handler(msg, ask_time, tsk)

def ask_time(message,tsk):
    text = take_meesage_text(message)
    if(text.lower() == 'cancel'):
        cancel_message(message)
        return
    if is_validate_time_format(text):
        if  tsk.is_relative()==False and is_time_expired(tsk.date_or_relativetime,text,get_user_tz(message.chat.id)):
            msg = send_message(message.chat.id,'The input time is expired, try enter another time!'+cancel_suggestion(),reply_markup=create_ReplyKeyboard())
            bot.register_next_step_handler(msg,ask_time,tsk)
            return
        tsk.time=text
        msg = send_message(message.chat.id, ('Begin'if tsk.is_relative() else'The date and ')+
                               'time has been taken successfully ')
    else:
        msg = send_message(message.chat.id, f'The time format or time range was wrong.'
                                            f' remeber the pattern is "<b>hour:minute:second </b>" {cancel_suggestion()}',reply_markup=create_ReplyKeyboard())
        bot.register_next_step_handler(msg,ask_time,tsk)
        return

    send_message(message.chat.id,'Write your description about the task! "<b>cancel</b>" does <u>not work</u> here!!')
    bot.register_next_step_handler(msg, ask_description, tsk)

def ask_description(message,tsk):
    text = take_meesage_text(message,False)
    tsk.description = text
    store_task(message,tsk)

def store_task(message,tsk):
    chat_id = message.chat.id
    timezone=get_user_tz(chat_id)
    if not(tsk.is_relative()):
        job=scheduler.add_job(send_notif,'date',run_date=tsk.date_or_relativetime.replace('/', '-')+' '+ tsk.time,
        args=[tsk, chat_id],timezone=timezone)
    else:
        hour,minute,second = tsk.date_or_relativetime.split(':')
        job = scheduler.add_job(send_notif,'interval',hours=int(hour),minutes=int(minute),seconds=int(second),
        start_date=datetime.combine((tomorrow_date() if is_time_expired(today_date(timezone),tsk.time,timezone) else today_date(timezone))
        , string_to_time(tsk.time)),args=[tsk, chat_id],timezone=timezone)
    if isinstance(tsk, Task):
        task_table = TaskTable(chat_id=message.chat.id,timetype=tsk.timetype,date_or_relativetime=tsk.date_or_relativetime
        ,time=tsk.time,description=tsk.description,apscheduler_job_id=job.id)
        task_table.add_task()
        task_id=TaskTableManagement().get_task(apscheduler_job_id=job.id).id
        jobtable=JobManager().get_job(id=job.id)
        jobtable.task_id=task_id
        JobManager().update_job(jobtable)
    else:
        raise ValueError('The parameter entered in store_task() is not object Task class')
        return
    send_message(message.chat.id,'your task has been activated <b>successfully</b>!\n'
                                     'The task information:\n'
                                     '<b>'+str(tsk)+'</b>')

def send_notif(tsk,chat_id):
    send_message(chat_id,f'alert ⚠️:\n ^*{tsk.description}*^')


@bot.message_handler(commands=['show_tasks'])
def list_tasks(message):
    tasks=TaskTableManagement().get_tasks_by_chat_id(message.chat.id)
    msg=''
    if tasks:
        msg='Your Tasks:\n'
        counter=1
        for task in tasks:
            msg +=f'{counter}- {give_task_info(task)}'
            counter+=1
    else:
        msg='You dont have any task yet!'
    send_message(message.chat.id, msg)
    return tasks

def give_task_info(task):
    task_info=f'time type:<b>{task.timetype}</b> '
    if task.timetype == 'Absolute':
            task_info +=f'| date & time: <b>{task.date_or_relativetime}</b> <b>{task.time}</b> '

    else:
        task_info +=f'| repeating time: <b>{task.date_or_relativetime}</b> | begin: <b>{task.time}</b> '
    task_info +=f'| desciption: <b>^*{task.description}*^</b>\n'
    return task_info

@bot.message_handler(commands=['delete_task'])
def ask_delete_task(message):
    tasks=list_tasks(message)
    if tasks:
        if len(tasks)>1:
            msg=send_message(message.chat.id,'send the number of The task you want to remove from above list!')
            bot.register_next_step_handler(msg, choose_deleted_task,tasks)
        else:
            candidate_delete_task(message.chat.id,tasks[0])
    else:
        return

def candidate_delete_task(chat_id,task):
    msg = send_message(chat_id,f'Chosen task\n\n {give_task_info(task)}\n\n'
    'Are you sure you want to delete that?(y/n)')
    bot.register_next_step_handler(msg,delete_task,task)

def choose_deleted_task(message,tasks):
    try:
        text = take_meesage_text(message)
        if not text.isnumeric():
            raise ValueError('That was not a number, try again! ')
        elif int(text)> len(tasks) or int(text)<1:
            raise ValueError('Your input number was wrong, try again! ')
        else:
            task=tasks[int(text)-1]
    except Exception as e:
        msg=send_message(message.chat.id,str(e))
        bot.register_next_step_handler(msg,choose_deleted_task,tasks)
        return
    candidate_delete_task(message.chat.id,task)

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
                                      '/start: Begin work with bot and set language\n'
                                      '/add_task: Create new task for alarm at certain time\n'
                                      '/show_tasks: Demonstrate all active tasks \n'
                                      '/delete_task: Remove an active \n'
                                      '/help: Show commands\n'
                                      '/about: What is this bot and how does it works\n')
@bot.message_handler(commands=['about'])
def about_text(message):
    send_message(message.chat.id, "This bot can be used for reminding an event for one-time<b>(absolute)</b> or repeating alert base on a interval time<b>(relative)</b>. "
                                    "you could also choosing the language by sending /start, for now there are two languages available,Persian and English.")
@bot.message_handler(func= lambda message : True)
def other_messages(message):
    send_message(message.chat.id,'the purpose of sending message is unknown,you could see commands through sending /help .')

if __name__ == '__main__':
    languages=['en','fa']
    user_lang={}
    user_tz={}
    bot.infinity_polling()


