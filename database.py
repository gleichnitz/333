import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import pickle
from datatime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

def addAssignment(course_name, student_netid, name, files):
    new_assignment = Assignment(course_name, student_netid, name, files)
    new_assignment.date = datetime.today()
    db.session.add(new_assignment)
    db.session.commit()

class Student(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    netid = db.Column(db.String(80), unique = True)
    courseid = db.Column(db.Integer, db.ForeignKey('course.id'))
    course = db.relationship('Course', backref = db.backref('students', lazy = 'dynamic'))

    # assignments = db.relationship('Assignment', backref = 'student', lazy = 'dynamic')
    def __init__(self, firstname, lastname, netid, course):
      self.firstname = firstname
      self.lastname = lastname
      self.netid = netid
      self.course = course

    def __repr__(self):
#      return format('<Student {0} {1} {2} {3}>', self.firstname, self.lastname, self.netid,self.course.name)
      #args = [self.firstname, self.lastname, self.netid, self.course.name]
      return 'Student {} {} {} {}'.format(self.firstname, self.lastname, self.netid, self.course.name)
    def __str__(self):
      return format('<Student {0} {1} {2} {3}>', self.firstname, self.lastname, self.netid,self.course.name)

class Grader(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    netid = db.Column(db.String(80), unique = True)
    courseid = db.Column(db.Integer, db.ForeignKey('course.id'))
    course = db.relationship('Course', backref = db.backref('graders', lazy = 'dynamic'))
    # graded_assignments = db.relationship('Assignment', backref = 'graders', lazy = 'dynamic')
    def __init__(self, netid, course):
      self.netid = netid
      self.course = course

    def __repr__(self):
      return 'Grader {} {}'.format(self.netid, self.course.name)

    def __str__(self):
      return '<Grader {} {}>'.format(self.netid, self.course.name)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    netid = db.Column(db.String(80), unique = True)
    courseid = db.Column(db.Integer, db.ForeignKey('course.id'))
    course = db.relationship('Course', backref = db.backref('admins', lazy = 'dynamic'))

    def __init__(self, netid, course):
      self.netid = netid
      self.course = course

    def __repr__(self):
      return 'Admin {} {}'.format(self.netid, self.course.name)

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

  date = db.Column(db.String(80))

  student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
  student = db.relationship('Student', backref = db.backref('assignments', lazy = 'dynamic'))

  grader = db.relationship('Grader', backref = db.backref('assignments', lazy = 'dynamic'))
  grader_id = db.Column(db.Integer, db.ForeignKey('grader.id'))

  name = db.Column(db.String(80))
  files = db.Column(db.PickleType)

  def __init__(self, course_name, student_netid, name, files):
    self.course = Course.query.filter_by(name = course_name).first()
    self.student = Student.query.filter_by(netid = student_netid).first()
    self.files = files
    self.name = name

  def addGrader(self, grader_netid):
    self.grader = Grader.query.filter_by(netid = grader_netid)

  def __repr__(self):
    return 'Assignment {} {} {} {}'.format(self.course.name, self.student.netid, self.name, self.date)

