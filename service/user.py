from ..model import User, ExternalEmail
from ..engine import connect, DBConnection


@connect
def add_user(name, mail_address, db: DBConnection = None) -> User:
    external = ExternalEmail(address=mail_address)
    db.s.add(external)
    db.s.flush()
    db.s.refresh(external)
    user = User(name=name, primary_external_email_id=external.id)
    db.s.add(user)
    db.s.commit()
    db.s.refresh(user)
    return user

