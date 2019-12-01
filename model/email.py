from sqlalchemy import Column, String, BigInteger, ForeignKey
from sqlalchemy.dialects.mysql import MEDIUMTEXT

from .base import BasicMixin, BaseObject


class ExternalEmail(BaseObject, BasicMixin):
    address = Column(String(128), unique=True)
    user_id = Column(BigInteger, ForeignKey('users.id'))


class InternalEmail(BaseObject, BasicMixin):
    address = Column(String(128), unique=True)


class InternalEmailMap(BaseObject, BasicMixin):
    internal_email_id = Column(BigInteger, ForeignKey('internal_emails.id'))
    user_id = Column(BigInteger, ForeignKey('users.id'))
    group_id = Column(BigInteger, ForeignKey('groups.id'))


class Message(BaseObject, BasicMixin):
    internal_email_id = Column(BigInteger, ForeignKey('internal_emails.id'))
    message_to = Column(String(128))
    message_from = Column(String(128))
    message_text = Column(String(128))
    message_dump = Column(MEDIUMTEXT)
    reply_address = Column(String(128), unique=True)
