# app/models/user_models.py
from peewee import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.models.bacula_models import BaseModel

class User(BaseModel, UserMixin):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password_hash = CharField()
    is_admin = BooleanField(default=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)