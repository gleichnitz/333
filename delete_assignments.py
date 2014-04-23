from import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import pickle
from database import *

assignments = Assignment.query.all()

for item in assignments:
  db.session.delete(item)
  db.session.commit()