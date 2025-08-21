from extension import db
from datetime import datetime
from flask_login import UserMixin

class History(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time = db.Column(db.DateTime, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product_name = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    type = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    
    def __init__(self, time, product_id,product_name, user_id, type, amount):
        self.time = time
        self.product_id = product_id
        self.product_name = product_name
        self.user_id = user_id
        self.type = type
        self.amount = amount

    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
