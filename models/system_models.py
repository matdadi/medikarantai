from public import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    fullname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=False)