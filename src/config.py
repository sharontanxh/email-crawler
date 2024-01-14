import os
from urllib.parse import quote


class Config:
    """
    Singleton to store app configuration.
    """

    def __init__(self):
        self.flask_app_port = os.getenv("flask_app_port", 5000)
        self.db_host = os.getenv("host", "127.0.0.1")
        self.postgres_db_port = os.getenv("db_port", 5432)
        self.sql_user = os.getenv("sql_user", 'postgres')
        self.sql_pass = quote(os.getenv("sql_pass", 'password'))
        self.swiftly_db_name = os.getenv("db_name", "swiftlydb")
        self.swiftly_db_uri = f"postgresql://{self.sql_user}:{self.sql_pass}@{self.db_host}:{self.postgres_db_port}/{self.swiftly_db_name}"


CONFIG = Config()
