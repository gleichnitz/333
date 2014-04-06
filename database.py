from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    netid = db.Column(db.String(80), unique = True)
    courseid = db.Column(db.Integer, db.ForeignKey('course.id'))
    course = db.relationship('Course', backref = db.backref('students', lazy = 'dynamic'))

    assignments = db.relationship('Assignment', backref = 'student', lazy = 'dynamic')
    def __init__(self, firstname, lastname, netid, course):
      self.firstname = firstname
      self.lastname = lastname
      self.netid = netid
      self.course = course

    def __repr__(self):
      return '<Student {0} {1} {2} {3}>'.format(self.firstname, self.lastname, self.netid, self.course.name)

class Grader(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    netid = db.Column(db.String(80), unique = True)
    courseid = db.Column(db.Integer, db.ForeignKey('course.id'))
    course = db.relationship('Course', backref = db.backref('students', lazy = 'dynamic'))
    graded_assignments = db.relationship('Assignment', backref = 'grader', lazy = 'dynamic')
    def __init__(self, netid, course):
      self.netid = netid
      self.course = course

    def __repr__(self):
      return '<Grader {0} {1}>'.format(self.netid, self.course.name)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    netid = db.Column(db.String(80), unique = True)
    courseid = db.Column(db.Integer, db.ForeignKey('course.id'))
    course = db.relationship('Course', backref = db.backref('students', lazy = 'dynamic'))

    def __init__(self, netid, course):
      self.netid = netid
      self.course = course

    def __repr__(self):
      return '<Admin {0} {1}>'.format(self.netid, self.course.name)

class Course(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(80), unique = True)

  def __init__(self, name):
    self.name = name

  def __repr__(self):
    return '<Course %r>' % self.name

class Assignment(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  courseid = db.Column(db.Integer, db.ForeignKey('course.id'))  
  course = db.relationship('Course', backref = db.backref('assignments', lazy = 'dynamic'))
  student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
  grader_id = db.Column(db.Integer, db.ForeignKey('grader.id'))



