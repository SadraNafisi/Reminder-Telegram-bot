#!/bin/bash
echo "today is " `date`
python ~/Reminder_timer/database.py
python ~/Reminder_timer/telegram_bot.py