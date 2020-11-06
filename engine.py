from configparser import ConfigParser
from typing import Dict, Optional, Union

from ex_tools import Empty, wraps
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, Connection
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sshtunnel import SSHTunnelForwarder


class DBConnectionConfig:
    def __init__(self, config: Dict[str, Union[str, Dict]] = Empty, config_file: str = 'db_config.ini'):
        if config is Empty:
            config = ConfigParser()
            try:
                config.read(config_file)
            except Exception as e:
                raise ValueError('you must provide at least one valid config source')
        try:
            db = config['db']
            self.protocol = db.get('protocol', 'mysql+pymysql')
            self.user = db.get('user', 'admin')
            self.password = db.get('password', 'password')
            self.host = db.get('host', 'localhost')
            self.port = int(db.get('port', '3306'))
            self.database = db.get('database', 'db')
        except Exception as e:
            print(e)
            raise ValueError('invalid config')
        try:
            self.ssh = config['ssh']
        except Exception as e:
            self.ssh = False
            del e
            pass
        if self.ssh:
            try:
                ssh_config = config['ssh']
                self.ssh_host = ssh_config['ssh_host']
                self.ssh_port = int(ssh_config.get('ssh_port', 22))
                self.ssh_user = ssh_config['ssh_user']
                self.ssh_password = ssh_config.get('ssh_password')
                self.ssh_identity = ssh_config.get('ssh_identity')
                if not self.ssh_password and not self.ssh_identity:
                    raise ValueError('password or identity file is needed')
            except Exception as e:
                raise ValueError('wrong ssh config')


class DBConnection:
    session_class = scoped_session(sessionmaker(), lambda: "DBConnection")

    def __init__(self, db_config: DBConnectionConfig = None, engine_options=None, **kwargs):
        self.db_config = db_config or DBConnectionConfig()
        self.engine: Optional[Engine] = None
        self.ssh_connection: Optional[SSHTunnelForwarder] = None
        self.connection: Optional[Connection] = None
        self.s: Optional[Session] = None
        self.engine_options = engine_options or {}
        self.execution_options = kwargs
        self.bind_dict = {
            'protocol': self.db_config.protocol,
            'db_user': self.db_config.user,
            'db_password': self.db_config.password,
            'db_host': self.db_config.host,
            'db_port': self.db_config.port,
            'db_name': self.db_config.database,
        }

    def enter(self):
        if self.db_config.ssh:
            self.ssh_connection = SSHTunnelForwarder(
                (self.db_config.ssh_host, self.db_config.ssh_port),
                ssh_username=self.db_config.ssh_user,
                ssh_password=self.db_config.ssh_password,
                ssh_pkey=self.db_config.ssh_identity,
                remote_bind_address=(self.db_config.host, self.db_config.port)
            )
            self.ssh_connection.start()
            self.bind_dict.update({
                'db_host': 'localhost',
                'db_port': self.ssh_connection.local_bind_port
            })
        self.engine = create_engine(
            self.url,
            **self.engine_options
        )
        self.session_class.configure(bind=self.engine)
        self.s = self.session_class()
        self.connection = self.s.connection(execution_options=self.execution_options)
        return self

    def __enter__(self):
        return self.enter()

    @property
    def url(self):
        return '{protocol}://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'.format(**self.bind_dict)

    def exit(self, exc_type=None, exc_val=None, exc_tb=None):
        del exc_type, exc_val, exc_tb
        self.connection.close()
        self.session_class.remove()
        self.engine.dispose()
        if self.ssh_connection:
            self.ssh_connection.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.exit(exc_type, exc_val, exc_tb)


def connect(func):
    from config import DBConnection

    @wraps(func)
    def inner(*args, db=None, **kwargs):
        if not db:
            with DBConnection() as temp_db:
                return func(*args, db=temp_db, **kwargs)
        return func(*args, db=db, **kwargs)
    return inner
