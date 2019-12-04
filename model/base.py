from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    schema
)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.sql.functions import current_timestamp
from inflection import underscore, pluralize

metadata = schema.MetaData()
BaseObject = declarative_base(metadata=metadata)


class BasicMixin:
    # noinspection PyMethodParameters
    @declared_attr
    def __tablename__(cls):
        # SomeModel -> some_models
        return pluralize(underscore(cls.__name__))

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=current_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=current_timestamp(), onupdate=current_timestamp(), nullable=False)
