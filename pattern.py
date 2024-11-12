from datetime import datetime, date, time, timedelta
import pytz
import re
timezone='Asia/Tehran'
def today_date_string(timezone=timezone):
    d=today_date()
    text=f'{d.year}/{d.month}/{d.day}'
    return text

def tomorrow_date_string(timezone=timezone):
    d=tomorrow_date(timezone)
    text=f'{d.year}/{d.month}/{d.day}'
    return text

def string_to_date(string_date):
    if is_valid_date(string_date):
        year,month,day=string_date.split('/')
        return datetime(int(year),int(month),int(day)).date()
    else:
        raise ValueError('Input is not in date form.')

def tomorrow_date(timezone='Asia/Tehran'):
    return today_date(timezone) + timedelta(days=1)

def today_date(timezone=timezone):
    return datetime.now().astimezone(pytz.timezone(timezone)).date()

def extract_date(input):
    if not(isinstance(input, date)):
        return string_to_date(input)
    else:
        return input

def is_outdated(input,timezone=timezone):
    input_date = extract_date(input)
    if input_date>= today_date(timezone):
        return False
    else:
        return True

def is_date_today(input,timezone=timezone):
    input_date = extract_date(input)
    if input_date == today_date(timezone):
        return True
    else:
        return False

def is_valid_date(date_string):
    try:
        year,month,day=date_string.split('/')
        string =f'{int(year)}/{int(month)}/{int(day)}'#for converting persian number to english
        # Try to parse the date string
        datetime.strptime(string, '%Y/%m/%d')

        return True  # If parsing is successful, the format is valid
    except ValueError:
        return False  # If parsing fails, the format is invalid

def is_validate_relative_time(time_string):
    # Define the regex pattern for "number" (hour/min/sec)
    pattern = r'^\d+:\d+:\d+$'
    try:
        # Check if the time_string matches the pattern
        if re.match(pattern, time_string):
            return True  # Valid format
    except ValueError:
        return False  # Invalid format

def string_to_time(string_time):
    if is_validate_time_format(string_time):
        hour,min,sec = string_time.split(':')
        return time(int(hour),int(min),int(sec))
    else:
        raise ValueError('input is not in time format.')

def extract_time(input):
    if not(isinstance(input, time)):
        return string_to_time(input)
    else:
        return input

def is_validate_time_format(time_string):
    try:
        hour,minute,second=time_string.split(':')
        string =f'{int(hour)}:{int(minute)}:{int(second)}'#for converting persian number to english
        # Attempt to parse the time_string
        datetime.strptime(string, '%H:%M:%S')
        return True  # Valid format
    except ValueError:
        return False  # Invalid format

def is_time_expired(date_input,time_input,timezone=timezone):
    tz=pytz.timezone(timezone)
    time=extract_time(time_input)
    date=extract_date(date_input)
    if is_outdated(date) or (is_date_today(date) and time<datetime.now().astimezone(tz).time()):
        return True
    else:
        return False

