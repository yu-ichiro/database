from sqlalchemy import Column, String, BigInteger, ForeignKey, Text, Integer, Index, DateTime
from sqlalchemy.dialects.mysql import MEDIUMBLOB, MEDIUMTEXT

from .base import BasicMixin, BaseObject


class ExternalEmail(BaseObject, BasicMixin):
    address = Column(String(128), unique=True)
    active_confirm = Column(DateTime)
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
    message_text = Column(Text)
    message_dump = Column(MEDIUMTEXT)
    reply_address = Column(String(128), unique=True)


class MessageQueueStatus:
    STATUS_UNPROCESSED = 0
    STATUS_ERROR = 1
    STATUS_SENT = 2


class MessagePriority:
    PRIORITY_HIGH = 0
    PRIORITY_PLUS = 25
    PRIORITY_NORMAL = 50
    PRIORITY_MINUS = 75
    PRIORITY_LOW = 100

    PRIORITY_ON_DEMAND = PRIORITY_HIGH
    PRIORITY_DEFAULT = PRIORITY_NORMAL

    PRIORITY_PRE_MAILING_LIST = PRIORITY_NORMAL + 5
    PRIORITY_MAILING_LIST = PRIORITY_NORMAL + 10
    PRIORITY_POST_MAILING_LIST = PRIORITY_NORMAL + 15


class MessageQueue(BaseObject, BasicMixin, MessageQueueStatus, MessagePriority):
    content_type = Column(Text)
    message_dump = Column(MEDIUMBLOB)
    status = Column(Integer, nullable=False, default=0)
    error_text = Column(Text)
    priority = Column(Integer, nullable=False, default=0)
    user_id = Column(BigInteger)
    from_message_id = Column(BigInteger, ForeignKey('messages.id'))

    __table_args__ = Index('idx_status', 'status'),

    @classmethod
    def default_sort_column(cls):
        return cls.priority, cls.user_id, cls.from_message_id
