from base64 import b64decode, b64encode
from dataclasses import dataclass, asdict
from io import BytesIO
from json import loads, JSONDecodeError, dumps
from typing import Tuple

from sqlalchemy import or_
from werkzeug.datastructures import MultiDict
from werkzeug.formparser import parse_form_data
from werkzeug.wrappers import BaseRequest

from ..engine import DBConnection, connect
from ..model import User, Group, UserGroupMap, InternalEmailMap, InternalEmail, ExternalEmail


@dataclass
class GroupMailMap:
    ml_address: str
    external_address: str
    group_name: str
    user_id: int


@connect
def get_group_mail(internal_email: InternalEmail, *, db: DBConnection = None):
    for _, external, name, user_id in db.s.query(
        ExternalEmail.id,
        ExternalEmail.address,
        Group.name,
        User.id
    ).join(User, User.primary_external_email_id == ExternalEmail.id).outerjoin(
        UserGroupMap, UserGroupMap.user_id == User.id
    ).outerjoin(Group, Group.id == UserGroupMap.group_id).outerjoin(
        InternalEmailMap, or_(
            InternalEmailMap.user_id == User.id,
            InternalEmailMap.group_id == Group.id
        )
    ).filter(
        InternalEmailMap.internal_email_id == internal_email.id,
        ExternalEmail.disabled.isnot(None)
    ).group_by(ExternalEmail.id):
        yield GroupMailMap(ml_address=internal_email.address,
                           external_address=external,
                           group_name=name,
                           user_id=user_id)


@dataclass
class MailRequestDump:
    content_type: str = 'text/plain'
    content_length: str = '0'
    data_dump: bytes = b''

    @classmethod
    def from_json(cls, json_str):
        try:
            data = loads(json_str)
        except JSONDecodeError as e:
            return cls()
        return cls(**{**data, 'data_dump': b64decode(data.get('data_dump'))})

    @classmethod
    def from_request(cls, request: BaseRequest):
        return cls(content_type=request.environ.get('CONTENT_TYPE'),
                   content_length=request.environ.get('CONTENT_LENGTH'),
                   data_dump=request.get_data())

    def to_json(self):
        dict_data = asdict(self)
        return dumps({**dict_data, 'data_dump': b64encode(dict_data.get('data_dump')).decode()})

    def parse_form_data(self) -> Tuple[MultiDict, MultiDict]:
        return parse_form_data({
            'CONTENT_TYPE': self.content_type,
            'CONTENT_LENGTH': self.content_length,
            'wsgi.input': BytesIO(self.data_dump)
        })[1:]
