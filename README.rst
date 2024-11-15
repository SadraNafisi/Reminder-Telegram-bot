##############
Reminder_timer
##############

A Telegram bot that allows users to set one-time(**absolute**) and repeating(**Relative**) alarms. Users can notify themselves by scheduling **tasks** that send alerts at specified times.

Feature
================

* One-time Alarm(Absolute):user can set alarm for a certain time in a certain date.
* Repeating Alarm(relative):user can set alarm to repeat at specified interval (e.g: every 4 hour)

Requirement
================

``python 3.6`` or higher

SQL database( e.g: ``PostgreSQL``)

Telegram bot

Installation
================

1- Clone the project from repository:

.. code-block:: bash

  git clone https://github.com/SadraNafisi/Reminder-timer-bot.git
  cd Reminder_timer

2- Obtain a bot in telegram from a bot called `BotFather <https://t.me/botfather>`_

3- BotFather gives **api-token** when process of creating bot finished. copy that!

4- in ``config.py`` put api_token from BotFather in ``telegram_api_key`` ::

  telegram_api_key='put telegram_api_key here'

5- in ``config.py`` also put Database url in ``database_url``::

  database_url='put database url here'

6- create *virtenv* in python and include with **source** command(I named the file .venv, it is optional name):

.. code-block:: bash

  python -m venv .venv
  source .venv/bin/activate

7- install required modules from ``requirement.txt``:

.. code-block:: bash

  pip install -r requirement.txt

8- Now by running ``runner.sh`` bash script, The bot Begin to work

.. code-block:: bash

  bash runner.sh

**NOTE**: after first installation , for rerunnig the telegram bot just do step 8. 

Bot Commands
==============

``/add_task``: create new task for alert in specified time

``/show_tasks``: demonstrate all tasks user that still remain

``/delete_task``: remove a task

Example
=============
.. raw:: html

   <div style="display: flex; justify-content: space-around;">
       <img src="example_images/test1.png" alt="Image 1" style="width: 330px;height:600px;">
       <img src="example_images/test2.png" alt="Image 2" style="width: 330px;height:600px;">
       <img src="example_images/test3.png" alt="Image 3" style="width: 330px;height:600px;">
       <img src="example_images/test4.png" alt="Image 4" style="width: 330px;height:600px;">
       <img src="example_images/test5.png" alt="Image 5" style="width: 330px;height:600px;">
   </div>

