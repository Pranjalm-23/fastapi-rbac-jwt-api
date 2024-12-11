from datetime import datetime
from mongoengine import Document, StringField, DateTimeField

# User Model
class User(Document):
    username = StringField(required=True, unique=True, description='Username of the user')
    password = StringField(required=True, description='Password of the user')
    role = StringField(required=True, choices=["admin", "user"], description='Role of the user (default: user)')
    email = StringField(description='Email of the user')

# Project Model
class Project(Document):
    name = StringField(required=True)
    description = StringField()
    created_at = DateTimeField(default=datetime.utcnow)