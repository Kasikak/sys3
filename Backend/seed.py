from app import app
from models import db, Role, User
import hashlib
import random

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def random_pin():
    length = random.randint(3, 8)
    return str(random.randint(10**(length-1), 10**length - 1))

with app.app_context():
    db.create_all()

    for role_name in ['Owner', 'Manager', 'Cashier']:
        if not Role.query.filter_by(roleName=role_name).first():
            db.session.add(Role(roleName=role_name))
    db.session.commit()

    users = [
        ('Admin User',   'admin',   'admin@carols.com',   'Owner'),
        ('Manager User', 'manager', 'manager@carols.com', 'Manager'),
        ('Cashier User', 'cashier', 'cashier@carols.com', 'Cashier'),
    ]

    print("Done! Login credentials:")
    for full_name, username, email, role_name in users:
        existing = User.query.filter_by(username=username).first()
        if not existing:
            pin  = random_pin()
            role = Role.query.filter_by(roleName=role_name).first()
            db.session.add(User(
                full_name=full_name,
                username=username,
                email=email,
                passwordHash=hash_password(pin),
                roleID=role.roleID
            ))
            db.session.commit()
            print(f"  {username:10s} PIN: {pin:>8s}  ({role_name})")
        else:
            print(f"  {username:10s} already exists — skipped (PIN unchanged)")
