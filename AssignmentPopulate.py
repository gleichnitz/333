import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import pickle
from database import *

cos333 = Course.query.filter_by(name = "cos333").first()
gabriella = Grader('gtl', cos333)

db.session.add(gabriella)
db.session.commit()

vinay = Student.query.filter_by(netid = 'rfreling').first()
Assignments = Assignment.query.filter_by(student = vinay).all()

for item in Assignments:
  db.session.delete(item)
  item.addGrader('gtl')
  db.session.add(item)
  db.session.commit()
