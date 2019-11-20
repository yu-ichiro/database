from sqlalchemy import Column, Text, ForeignKey, BigInteger, Index

from .base import BaseObject, BasicMixin


class User(BaseObject, BasicMixin):
    name = Column(Text)
    furigana = Column(Text)
    primary_external_email_id = Column(BigInteger)

    # tuple
    __table_args__ = Index('idx_primary_external_email_id', 'primary_external_email_id'),


class Group(BaseObject, BasicMixin):
    name = Column(Text)


class UserGroupMap(BaseObject, BasicMixin):
    user_id = Column(BigInteger, ForeignKey('users.id'))
    group_id = Column(BigInteger, ForeignKey('groups.id'))
