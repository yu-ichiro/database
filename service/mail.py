from dataclasses import dataclass

from sqlalchemy import or_

from ..engine import DBConnection, connect
from ..model import User, Group, UserGroupMap, InternalEmailMap, InternalEmail, ExternalEmail


@dataclass
class GroupMailMap:
    ml_address: str
    external_address: str
    group_name: str


@connect
def get_group_mail(internal_email: InternalEmail, *, db: DBConnection = None):
    for _, external, name in db.s.query(
        ExternalEmail.id,
        ExternalEmail.address,
        Group.name
    ).join(User, User.primary_external_email_id == ExternalEmail.id).outerjoin(
        UserGroupMap, UserGroupMap.user_id == User.id
    ).outerjoin(Group, Group.id == UserGroupMap.group_id).outerjoin(
        InternalEmailMap, or_(InternalEmailMap.user_id == User.id, InternalEmailMap.group_id == Group.id)
    ).filter(
        InternalEmailMap.internal_email_id == internal_email.id
    ).group_by(ExternalEmail.id):
        yield GroupMailMap(ml_address=internal_email.address, external_address=external, group_name=name)
