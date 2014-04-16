import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import pickle
from database import *

cos333 = Course.query.filter_by(name = 'cos333').first()
James = Grader('jaevans', cos333)

db.session.add(James)
db.session.commit()

vinay = Student.query.filter_by(netid = 'vayyala').first()
Assignments = Assignment.query.filter_by(student = vinay).all()

for item in Assignments:
  item.addGrader('jaevans')

db.session.commit()