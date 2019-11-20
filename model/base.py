from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    schema
)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.sql.functions import GenericFunction
from inflection import underscore, pluralize

metadata = schema.MetaData()
BaseObject = declarative_base(metadata=metadata)


# noinspection PyPep8Naming
class current_timestamp(GenericFunction):
    type = DateTime


class BasicMixin:
    # noinspection PyMethodParameters
    @declared_attr
    def __tablename__(cls):
        # SomeModel -> some_models
        return pluralize(underscore(cls.__name__))

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=current_timestamp(), nullable=False)
    updated_at = Column(DateTime, default=current_timestamp(), onupdate=current_timestamp(), nullable=False)
