import hashlib
from datetime import datetime, timezone, timedelta
from models import db, User

MAX_ATTEMPTS  = 3
LOCKOUT_MINS  = 15


class AuthService:

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()

    @staticmethod
    def login(username, password):
        user = User.query.filter_by(username=username).first()
        if not user:
            return None, 'Invalid username or password'

        now = datetime.now(timezone.utc)

        # Check lockout
        if user.locked_until:
            locked_until = user.locked_until
            if locked_until.tzinfo is None:
                locked_until = locked_until.replace(tzinfo=timezone.utc)
            if now < locked_until:
                remaining = int((locked_until - now).total_seconds() / 60) + 1
                return None, f'Account locked. Try again in {remaining} minute(s).'
            else:
                # Lockout expired — reset
                user.failed_attempts = 0
                user.locked_until    = None

        # Check password
        if user.passwordHash != AuthService.hash_password(password):
            user.failed_attempts += 1
            if user.failed_attempts >= MAX_ATTEMPTS:
                user.locked_until    = now + timedelta(minutes=LOCKOUT_MINS)
                user.failed_attempts = 0
                db.session.commit()
                return None, f'Too many attempts. Account locked for {LOCKOUT_MINS} minutes.'
            db.session.commit()
            attempts_left = MAX_ATTEMPTS - user.failed_attempts
            return None, f'Incorrect password. {attempts_left} attempt(s) remaining.'

        # Success — reset counter
        user.failed_attempts = 0
        user.locked_until    = None
        db.session.commit()
        return user, None

    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)
