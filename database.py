from config import database_url
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import time
from sqlalchemy import create_engine, ForeignKey, Column, Integer, Unicode , TEXT, CheckConstraint, Time, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, validates, relationship
from pattern import is_valid_date, is_validate_time_format, is_validate_relative_time
Base = declarative_base()
url=database_url
engine = create_engine(url)
Session = sessionmaker(bind=engine)
metadata = Base.metadata
jobstore=SQLAlchemyJobStore(engine=create_engine(url), metadata=Base.metadata)
jobstore.jobs_t.append_column(Column('task_id',Integer, ForeignKey('tasks.id',ondelete='CASCADE'),unique=True))
def takeConfigScheduler():
    jobstores = {
        'default': jobstore
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
    def get_task(self,**kwarg):
        with Session() as session:
            task=session.query(TaskTable).filter_by(**kwarg).one_or_none()
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



class TaskTable(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(Integer, ForeignKey('users', ondelete='CASCADE'),nullable=False)
    timetype = Column(Unicode(9), nullable=False)
    date_or_relativetime = Column(Unicode(40), nullable=False)
    time = Column(Time, nullable=False)
    timezone = Column(Unicode(20), nullable=False)
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

class Job(Base):
    __table__ = jobstore.jobs_t


class JobManager:
    def get_job(self,**kwarg):
        with Session() as session:
            job = session.query(Job).filter_by(**kwarg).one_or_none()
            return job
    def update_job(self,job):
        with Session() as session:
            instance = session.query(Job).filter_by(id = job.id).one_or_none()
            for key, value in job.__dict__.items():
                if key != '_sa_instance_state':  # Skip SQLAlchemy internal state
                    setattr(instance, key, value)
                try:
                    session.commit()
                except Exception as e:
                    session.rollback()
                    print(str(e))

class UserTable(Base):
    __tablename__ = 'users'
    chat_id = Column(Integer,primary_key=True)
    language = Column(Unicode(3),default='en')
    timezone = Column(Unicode(20),default='Asia/Tehran')

    def save(self):
        UserTableManager().create_or_update_user(self)

class UserTableManager:
    def create_or_update_user(self, usertable):
        Base.metadata.create_all(engine)
        if not isinstance(usertable, UserTable):
            raise ValueError(f'The entry was not UserTable objects type: {type(usertable)}')
        session = Session()
        try:
            instance = session.query(UserTable).filter_by(chat_id=usertable.chat_id).one_or_none()
            if instance:
                for key, value in usertable.__dict__.items():
                    if key != '_sa_instance_state':  # Skip SQLAlchemy internal state
                        setattr(instance, key, value)
            else:
                # Add new user
                session.add(usertable)

            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_user(self,**kwarg):
        with Session() as session:
            user = session.query(UserTable).filter_by(**kwarg).one_or_none()
        return user

    def get_or_create_user(self,**kwargs):
        with Session() as session:
            instance = session.query(UserTable).filter_by(**kwargs).one_or_none()
            if instance:
                return instance, False
            else:
                params = {k: v for k, v in kwargs.items()}
                instance = UserTable(**params)
                try:
                    session.add(instance)
                    session.commit()
                except Exception as e:  # The actual exception depends on the specific database so we catch all exceptions. This is similar to the official documentation: https://docs.sqlalchemy.org/en/latest/orm/session_transaction.html
                    session.rollback()
                    print(str(e))
                    instance = session.query(UserTable).filter_by(**kwargs).one()
                    return instance, False
                else:
                    return instance, True



if __name__ == '__main__':
    Base.metadata.create_all(engine)