from datetime import datetime, date, time, timedelta
import re
def string_to_date(string_date):
    if is_valid_date(string_date):
        year,month,day=string_date.split('/')
        return datetime(int(year),int(month),int(day)).date()
    else:
        raise ValueError('Input is not in date form!')
        
def tomorrow_date():
    return datetime.now().date() + timedelta(days=1)
def extract_date(input):
    if not(isinstance(input, date)):
        return string_to_date(input)
    else:
        return input

def is_outdated(input):
    input_date = extract_date(input)
    if input_date>= datetime.now().date():
        return False
    else:
        return True

def is_date_today(input):
    input_date = extract_date(input)
    if input_date == datetime.now().date():
        return True
    else:
        return False
            
def is_valid_date(date_string):
    try:
        # Try to parse the date string
        datetime.strptime(date_string, '%Y/%m/%d')
        
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
        # Attempt to parse the time_string
        datetime.strptime(time_string, '%H:%M:%S')
        return True  # Valid format
    except ValueError:
        return False  # Invalid format

def is_time_expired(date_input,time_input):
    time=extract_time(time_input)
    date=extract_date(date_input)
    if is_date_today(date)and time<datetime.now().time():
        return True
    else:
        return False

