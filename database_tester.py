from reminder_timer_db import TaskTable,takeConfigScheduler,DatabaseManager,TaskTableManagement
from datetime import datetime, timedelta
import time
# def send_helloworld():
#     print('hello world')
# scheduler = takeConfigScheduler()
# job=scheduler.add_job(send_helloworld,'date',run_date=datetime.now()+timedelta(days=40))
# task=TaskTable(chat_id=123,timetype='Absolute',date_or_relativetime='2023/03/03'
# ,time='20:20:20',description='alaki',apscheduler_job_id=job.id)
# scheduler.start()
# task.add_task()
# time.sleep(40)

# session= DatabaseManager().get_session()
# session.query(TaskTable).filter(TaskTable.id==1).delete()
# session.commit()


# print(DatabaseManager().get_metadata().tables.get('apscheduler_jobs'))

tasks=TaskTableManagement().get_all_tasks()
for task in tasks:
    print(task.id)