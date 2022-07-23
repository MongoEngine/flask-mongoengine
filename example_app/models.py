import datetime

from flask_mongoengine import MongoEngine
from flask_mongoengine.wtf.orm import model_form

db = MongoEngine()


class Todo(db.Document):
    title = db.StringField(max_length=60)
    text = db.StringField()
    done = db.BooleanField(default=False)
    pub_date = db.DateTimeField(default=datetime.datetime.now)


TodoForm = model_form(Todo)
