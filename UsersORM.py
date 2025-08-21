from extension import db
from flask_login import UserMixin

class Users(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False) # 密码(v1做明文存储)
    type = db.Column(db.String(100), nullable=False) # 用户类型，管理员（admin），普通用户（default），已禁用（disabled）

    def __init__(self, username, password,type = 'default'):
        self.username = username
        self.password = password
        self.type = type


    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()