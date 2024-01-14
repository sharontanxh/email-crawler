from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, TIMESTAMP, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.config import CONFIG

Base = declarative_base()


class Thread(Base):
    """
    In the context of Sql Alchemy:
    Thread class represents a table in SwiftlyDb
    Each instance of the Thread class represents a row in the Threads table.
    processed_status: True if the thread has been checked for todos, False otherwise
    user_status: True if the user has marked the thread's todos as complete, False otherwise
    """

    __tablename__ = 'Threads'

    row_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Fields populated by fetching from Google
    thread_id = Column(String(255))
    message_body = Column(Text)
    subject = Column(String(255))
    from_email = Column(String(255))
    user_email = Column(String(255))
    timestamp_of_last_message = Column(TIMESTAMP)
    email_link = Column(Text)
    last_updated = Column(TIMESTAMP)

    # Fields populated due to processing by Swiftly
    processed_status = Column(Boolean)
    user_status = Column(String(100))
    next_step = Column(String(100))
    action = Column(Text)
    deadline = Column(TIMESTAMP)
    summary = Column(Text)
    effort = Column(String(100))
    todo_constraint = Column(Text)

    def __repr__(self):
        return f"<Thread(subject='{self.subject}', from_email='{self.from_email}')>"


class SwiftlyDB:
    def __init__(self):
        """
        Initialize the database connection.
        """
        self.db_uri = CONFIG.swiftly_db_uri
        self.engine = create_engine(self.db_uri)
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        """
        Create the tables in the database.
        """
        Base.metadata.create_all(self.engine)

    def add_threads(self, threads_data):
        """
        Add multiple new threads to the database.
        """
        session = self.Session()
        try:
            for data in threads_data:
                new_thread = Thread(**data)
                session.add(new_thread)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_all_threads(self):
        """
        Retrieve all threads from the database.
        """
        session = self.Session()
        threads = session.query(Thread).all()
        session.close()
        return threads

    def get_unprocessed_threads(self):
        """
        Retrieve all threads that have not been processed.
        """
        session = self.Session()
        threads = session.query(Thread).filter(Thread.processed_status != True).all()
        session.close()
        return threads

    def get_processed_threads(self):
        """
        Retrieve all threads that have not been processed.
        """
        session = self.Session()
        threads = session.query(Thread).filter(Thread.processed_status == True).all()
        session.close()
        return threads

    def update_thread(self, thread_id, processed_gpt_output):
        """
        Update the thread with the processed GPT output.
        """
        session = self.Session()
        thread = session.query(Thread).get(thread_id)
        if thread:
            thread.next_step = processed_gpt_output.get('next_step')
            thread.action = processed_gpt_output.get('action')
            thread.deadline = processed_gpt_output.get('deadline')
            thread.summary = processed_gpt_output.get('summary')
            thread.effort = processed_gpt_output.get('effort')
            thread.todo_constraint = processed_gpt_output.get('constraint')
            thread.processed_status = True
            session.commit()
        session.close()