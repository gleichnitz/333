import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import pickle
from database import *

db.drop_all()
db.create_all()

cos333 = Course("cos333")
Vinay = Student('vinay', 'ayyala', 'vayyala', cos333)

db.session.add(cos333)
db.session.add(Vinay)


db.session.commit()