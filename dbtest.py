from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from database import db, Student, Course

db.create_all()
cos_333 = Course('cos333')
cos_126 = Course('cos126')

admin = Student('vinay', 'ayyala', 'vayyala', cos_333)
james = Student('james', 'evans', 'jaevans', cos_126)
richard = Student('richard', 'freling', 'rfreling', cos_126)

db.session.add(admin)
db.session.add(james)
db.session.add(richard)

db.session.commit()

students = Student.query.all()
print students

print cos_333.students.all()
print cos_126.students.all()