from ex_tools import Empty
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

    def update_from_model(self, other):
        for attr in dir(self):
            cls_attr = getattr(type(self), attr, None)
            if cls_attr is None or not hasattr(cls_attr, "__clause_element__"):
                continue
            if isinstance(cls_attr.__clause_element__(), Column):
                val = getattr(other, attr, None)
                if val is None:
                    continue
                if val is Empty:
                    val = None
                setattr(self, attr, val)
