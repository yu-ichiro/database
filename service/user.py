from datetime import datetime
from typing import Optional

from ..model import User, ExternalEmail, UserGroupMap
from ..engine import connect, DBConnection


@connect
def add_user(mail_address, name=None, furigana=None, period=None, group_id=None, db: DBConnection = None) -> User:
    external = ExternalEmail(address=mail_address, active_confirm=datetime.now())
    db.s.add(external)
    db.s.flush()
    db.s.refresh(external)
    user = User(
        name=name,
        furigana=furigana,
        period=period,
        primary_external_email_id=external.id
    )
    db.s.add(user)
    db.s.flush()
    db.s.refresh(user)
    db.s.refresh(external)
    external.user_id = user.id
    db.s.add(external)
    db.s.commit()
    if group_id:
        group_map = UserGroupMap(user_id=user.id, group_id=group_id)
        db.s.add(group_map)
        db.s.commit()
    db.s.refresh(user)
    return user


@connect
def update_info(current_mail, update_data: User = None, new_email: str = None, db: DBConnection = None) -> bool:
    current_address: Optional[ExternalEmail] = db.s.query(ExternalEmail).filter(
        ExternalEmail.address == current_mail
    ).first()
    if not current_address:
        return False
    current_address.active_confirm = datetime.now()
    db.s.add(current_address)
    user = db.s.query(User).filter(User.primary_external_email_id == current_address.id).first()
    if not user:
        return False

    if new_email:
        new_mail = ExternalEmail(user_id=user.id, address=new_email, active_confirm=datetime.now())
        db.s.add(new_mail)
        db.s.flush()
        db.s.refresh(user)
        user.primary_external_email_id = new_mail.id
    if update_data:
        user.update_from_model(update_data)
    db.s.commit()
    return True
