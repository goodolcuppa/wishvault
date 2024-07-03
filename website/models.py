from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

item_category = db.Table("item_category", 
    db.Column("item_id", db.Integer, db.ForeignKey("item.id")),
    db.Column("category_id", db.Integer, db.ForeignKey("category.id"))
)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    price = db.Column(db.Float)
    url = db.Column(db.String(500))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    categories = db.relationship("Category", secondary=item_category, backref="items")

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(40))
    items = db.relationship('Item')