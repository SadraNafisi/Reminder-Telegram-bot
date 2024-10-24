from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_tasktable import Task

engine= create_engine('postgresql://root:M5cdvDnzgYo8Y9sW9FDJz3ra@himalayas.liara.cloud:31190/postgres')
Session = sessionmaker(bind=engine)
session=Session()

session.add(Task(chat_id=123, timetype='Absolute',
date_or_relativetime='2024/09/09', description='Sample task'))
try:
    session.commit()
except Exception as e:
    session.rollback()  # Rollback the session to maintain integrity
    print(f"Error occurred: {e}")
finally:
    session.close()