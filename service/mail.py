from dataclasses import dataclass

from sqlalchemy import or_

from ..engine import DBConnection, connect
from ..model import User, Group, UserGroupMap, InternalEmailMap, InternalEmail, ExternalEmail


@dataclass
class GroupMailMap:
    ml_address: str
    external_address: str


@connect
def get_group_mail(ml_address: str, *, db: DBConnection = None):
    for _, external in db.s.query(
        ExternalEmail.id,
        ExternalEmail.address
    ).join(User, User.id == ExternalEmail.user_id).outerjoin(
        UserGroupMap, UserGroupMap.user_id == User.id
    ).outerjoin(Group, Group.id == UserGroupMap.group_id).outerjoin(
        InternalEmailMap, or_(InternalEmailMap.user_id == User.id, InternalEmailMap.group_id == Group.id)
    ).outerjoin(InternalEmail, InternalEmail.id == InternalEmailMap.internal_email_id).filter(
        InternalEmail.address == ml_address
    ).group_by(ExternalEmail.id):
        yield GroupMailMap(ml_address=ml_address, external_address=external)
