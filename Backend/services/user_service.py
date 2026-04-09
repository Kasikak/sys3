import hashlib
from models import db, User, Role


class UserService:

    @staticmethod
    def get_all():
        return User.query.all()

    @staticmethod
    def create(full_name, username, pin, role_name):
        if not full_name or not username or not pin:
            return None, 'Name, username, and PIN are required'
        if User.query.filter_by(username=username).first():
            return None, f'Username "{username}" is already taken'
        role = Role.query.filter_by(roleName=role_name.capitalize()).first()
        if not role:
            return None, 'Invalid role'
        password_hash = hashlib.sha256(pin.encode()).hexdigest()
        user = User(
            full_name=full_name,
            username=username,
            email=f'{username}@carols.com',
            passwordHash=password_hash,
            roleID=role.roleID
        )
        db.session.add(user)
        db.session.commit()
        return user, None

    @staticmethod
    def update_role(user_id, role_name):
        user = User.query.get(int(user_id))
        if not user:
            return False, 'User not found'
        role = Role.query.filter_by(roleName=role_name.capitalize()).first()
        if not role:
            return False, 'Invalid role'
        user.roleID = role.roleID
        db.session.commit()
        return True, None
