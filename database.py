from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import time
from sqlalchemy import create_engine, ForeignKey, Column, Integer, Unicode , TEXT, CheckConstraint, Time, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, validates, relationship
from pattern import is_valid_date, is_validate_time_format, is_validate_relative_time
Base = declarative_base()
# url='[REDACTED]'
url = 'database_url' #local_database(postgres)
# url='[REDACTED]'#python anywhere(mysql)
engine = create_engine(url)
Session = sessionmaker(bind=engine)
metadata = Base.metadata

class TaskTableManagement:
    def create_task(self,tasktable):
        if isinstance(tasktable, TaskTable):
            Base.metadata.create_all(engine)
            with Session() as session:
                try:
                    session.add(tasktable)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    raise e
        else:
            raise ValueError(f'the entry was not Tasktable object:{type(tasktable)}')
    def get_task(self,task_id):
        with Session() as session:
            task=session.query(TaskTable).filter(TaskTable.id==task_id).first()
            return task

    def get_tasks_by_chat_id(self, chat_id):
        with Session() as session:
            tasks = session.query(TaskTable).filter(TaskTable.chat_id == chat_id).all()
            return tasks

    def get_all_tasks(self):
        with Session() as session:
            tasks=session.query(TaskTable).all()
            return tasks
    def remove_task(self,tasktable):
        with Session() as session:
            try:
                session.delete(tasktable)
                session.commit()
            except exception as e:
                session.rollback()
                raise e


class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(url)
        self.Session = sessionmaker(bind=self.engine)
        self.metadata = Base.metadata

    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)

    def get_metadata(self):
        return self.metadata

    def get_session(self):
        return self.Session()


class TaskTable(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, nullable=False)
    timetype = Column(Unicode(9), nullable=False)
    date_or_relativetime = Column(Unicode(40), nullable=False)
    time = Column(Time, nullable=True)
    description = Column(TEXT, nullable=False)
    apscheduler_job_id = Column(Unicode(191), ForeignKey('apscheduler_jobs.id', ondelete='CASCADE',), unique=True, nullable=False)

    __table_args__ = (
        CheckConstraint(timetype.in_(["Relative", "Absolute"]), name='check_timetype'),
    )
    @validates('date_or_relativetime')
    def validate_datdb_urle_or_relativetime(self, key, value):
        if self.timetype == 'Absolute':
            if not is_valid_date(value):
                raise ValueError("For 'Absolute' timetype, date_or_relativetime must be a valid date.")
        elif self.timetype == 'Relative':
            if not is_validate_relative_time(value):
                raise ValueError("For 'Relative' timetype, date_or_relativetime must be in the format 'number (hour/min/sec)'.")
        return value
    def add_task(self):
        TaskTableManagement().create_task(self)
    def delete_task(self):
        TaskTableManagement().remove_task(self)


def takeConfigScheduler():
    jobstores = {
        'default': SQLAlchemyJobStore(engine=create_engine(url), metadata=Base.metadata)
    }
    executors = {
        'default': ThreadPoolExecutor(2),
        'processpool': ProcessPoolExecutor(1)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 3
    }
    return BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)