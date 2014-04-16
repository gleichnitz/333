import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import pickle
from database import *


vinay = Student.query.filter_by(netid = 'vayyala').first()
Assignments = Assignment.query.filter_by(student = vinay).all()

for item in Assignments:
  db.session.delete(item)
  item.addGrader('jaevans')
  db.session.add(item)
  db.session.commit()
