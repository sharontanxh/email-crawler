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
    """

    __tablename__ = 'Threads'

    row_id = Column(Integer, primary_key=True, autoincrement=True)
    thread_id = Column(String(255))
    message_body = Column(Text)
    subject = Column(String(255))
    from_email = Column(String(255))
    user_email = Column(String(255))
    timestamp_of_last_message = Column(TIMESTAMP)
    email_link = Column(Text)
    processed_status = Column(Boolean)
    last_updated = Column(TIMESTAMP)
    user_status = Column(String(100))
    to_do = Column(Text)

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

    def add_thread(self, **kwargs):
        """
        Add a new thread to the database.
        """
        session = self.Session()
        new_thread = Thread(**kwargs)
        session.add(new_thread)
        session.commit()
        session.close()

    def get_all_threads(self):
        """
        Retrieve all threads from the database.
        """
        session = self.Session()
        threads = session.query(Thread).all()
        session.close()
        return threads
