from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()


def utcnow():
    return datetime.now(timezone.utc)


class Role(db.Model):
    __tablename__ = 'Roles'
    roleID   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roleName = db.Column(db.String(50), nullable=False, unique=True)
    users    = db.relationship('User', backref='role', lazy=True)


class User(db.Model):
    __tablename__ = 'Users'
    userID       = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name    = db.Column(db.String(150), nullable=False)
    username     = db.Column(db.String(100), nullable=False, unique=True)
    email        = db.Column(db.String(150), nullable=False, unique=True)
    passwordHash = db.Column(db.String(255), nullable=False)
    roleID       = db.Column(db.Integer, db.ForeignKey('Roles.roleID'), nullable=False)
    created_at      = db.Column(db.DateTime, default=utcnow, nullable=False)
    failed_attempts = db.Column(db.Integer, nullable=False, default=0)
    locked_until    = db.Column(db.DateTime, nullable=True)
    sales           = db.relationship('Sale', backref='cashier', lazy=True)
    reports      = db.relationship('Report', backref='generatedByUser', lazy=True)


class Item(db.Model):
    __tablename__ = 'Items'
    ItemName         = db.Column(db.String(200), primary_key=True)
    Price            = db.Column(db.Float, nullable=False)
    Stock            = db.Column(db.Integer, nullable=False)
    Category         = db.Column(db.String(100), nullable=False, default='Uncategorized')
    reorderThreshold = db.Column(db.Integer, nullable=False, default=10)
    saleItems        = db.relationship('SaleItem', primaryjoin='Item.ItemName == foreign(SaleItem.ItemName)', backref='product', lazy=True)
    alerts           = db.relationship('Alert',    primaryjoin='Item.ItemName == foreign(Alert.ItemName)',    backref='product', lazy=True)


class Sale(db.Model):
    __tablename__ = 'Sales'
    transactionID  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cashierID      = db.Column(db.Integer, db.ForeignKey('Users.userID'), nullable=True)
    date           = db.Column(db.DateTime, default=utcnow, nullable=False)
    total          = db.Column(db.Float, nullable=False)
    tax            = db.Column(db.Float, nullable=False, default=0.0)
    payment_method = db.Column(db.String(50), nullable=False, default='cash')
    saleItems      = db.relationship('SaleItem', backref='sale', lazy=True, cascade='all, delete-orphan')


class SaleItem(db.Model):
    __tablename__ = 'SaleItems'
    saleItemID    = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transactionID = db.Column(db.Integer, db.ForeignKey('Sales.transactionID'), nullable=False)
    ItemName      = db.Column(db.String(200), nullable=False)
    quantity      = db.Column(db.Integer, nullable=False)
    priceAtSale   = db.Column(db.Float, nullable=False)


class Report(db.Model):
    __tablename__ = 'Reports'
    reportID      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    generatedBy   = db.Column(db.Integer, db.ForeignKey('Users.userID'), nullable=True)
    reportType    = db.Column(db.String(50), nullable=False)
    dateRangeFrom = db.Column(db.DateTime, nullable=True)
    dateRangeTo   = db.Column(db.DateTime, nullable=True)
    createdAt     = db.Column(db.DateTime, default=utcnow, nullable=False)


class Alert(db.Model):
    __tablename__ = 'Alerts'
    alertID   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ItemName  = db.Column(db.String(200), nullable=False)
    alertType = db.Column(db.String(50), nullable=False, default='low_stock')
    message   = db.Column(db.String(255), nullable=False)
    status    = db.Column(db.String(20), nullable=False, default='active')
    createdAt = db.Column(db.DateTime, default=utcnow, nullable=False)
