from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Item(db.Model):
    __tablename__ = 'Items'
    ItemName = db.Column(db.String, primary_key=True)
    Quantity  = db.Column(db.Integer, nullable=False)
    Price     = db.Column(db.Float, nullable=False)
    Stock     = db.Column(db.Integer, nullable=False)
    Category  = db.Column(db.String(100), nullable=False, default='Uncategorized')