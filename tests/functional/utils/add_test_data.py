from tests.functional.test_data.data import users, roles
from src.models.user import User, Role
from src.db.postgres import db
from sqlalchemy.exc import IntegrityError


def _save_obj(obj):
    db.session.add(obj)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()


def add_test_data() -> None:
    roles_dict = {}
    for role in roles:
        r = Role(**role)
        _save_obj(r)
        roles_dict[r.name] = r

    for user in users:
        u = User(**user)
        role = roles_dict.get(u.email.split('@')[0])
        u.roles.append(role)
        _save_obj(u)


if __name__ == '__main__':
    add_test_data()
