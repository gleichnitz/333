# Project: codePost
# Template for Main Page
# Authors: Ayyala, Evans, Freling, Kubiak, Leichnitz
# Date: May 2014

import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import pickle
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

def addAssignment(course_name, student_netid, name, files):
    new_assignment = Assignment(course_name, student_netid, name)
    new_assignment.sub_date = datetime.today()
    new_assignment.AddFiles(files)
    db.session.add(new_assignment)
    db.session.commit()
    return new_assignment.id

s_courses = db.Table('s_courses',
  db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
  db.Column('student_id', db.Integer, db.ForeignKey('student.id')))

g_courses = db.Table('g_courses',
  db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
  db.Column('grader_id', db.Integer, db.ForeignKey('grader.id')))

a_courses = db.Table('a_courses',
  db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
  db.Column('admin_id', db.Integer, db.ForeignKey('admin.id')))

class Student(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    netid = db.Column(db.String(80), unique = True)
    courses = db.relationship('Course', secondary=s_courses,
      backref=db.backref('students', lazy='dynamic'))

    # assignments = db.relationship('Assignment', backref = 'student', lazy = 'dynamic')
    def __init__(self, firstname, lastname, netid):
      self.firstname = firstname
      self.lastname = lastname
      self.netid = netid

    def addCourse(self, course):
      new_course = Course.query.filter_by(name = course).first()
      if new_course is not None:
        self.courses.append(new_course)

    def __repr__(self):
      return 'Student {} {} {}'.format(self.firstname, self.lastname, self.netid )

class Grader(db.Model):
    id = db.Column(db.Integer, primary_key = True)

    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))

    netid = db.Column(db.String(80), unique = True)
    courses = db.relationship('Course', secondary=g_courses,
      backref=db.backref('graders', lazy='dynamic'))

    def __init__(self, netid):
      self.netid = netid


    def addCourse(self, course):
      new_course = Course.query.filter_by(name = course).first()
      if new_course is not None:
        self.courses.append(new_course)



    def __repr__(self):
      return 'Grader {}'.format(self.netid)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    netid = db.Column(db.String(80), unique = True)
    courses = db.relationship('Course', secondary=a_courses,
      backref=db.backref('admins', lazy='dynamic'))
    def __init__(self, netid):
      self.netid = netid

    def addCourse(self, course):
      new_course = Course.query.filter_by(name = course).first()
      if new_course is not None:
        self.courses.append(new_course)



    def __repr__(self):
      return 'Admin {}'.format(self.netid)

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

  sub_date = db.Column(db.String(80))
  due_date = db.Column(db.String(80))

  student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
  student = db.relationship('Student', backref = db.backref('assignments', lazy = 'dynamic'))

  grader = db.relationship('Grader', backref = db.backref('assignments', lazy = 'dynamic'))
  grader_id = db.Column(db.Integer, db.ForeignKey('grader.id'))

  name = db.Column(db.String(80))
  files = db.Column(db.PickleType)

  rubric = db.Column(db.PickleType)

  graded = db.Column(db.Boolean)
  in_progress = db.Column(db.Boolean)

  master = db.Column(db.Boolean)

  grade = db.Column(db.Float)
  points_possible = db.Column(db.Integer)

  def __init__(self, course_name, student_netid, name):
    self.course = Course.query.filter_by(name = course_name).first()
    self.student = Student.query.filter_by(netid = student_netid).first()
    self.name = name
    self.master = False
    self.graded = False
    self.in_progress = False

  def AddFiles(self, files):
    self.files = files

  def PointsPossible(self, points):
    self.points_possible = points

  def Master(self):
    self.master = True

  def Grade(self, grade):
    self.grade = grade

  def Sub_date(self, sub_date):
    self.sub_date = sub_date

  def Due_date(self, due_date):
    self.due_date = due_date

  def addRubric(self, rubric):
    self.rubric = rubric

  def mark_ungraded(self):
    self.graded = False
    self.in_progress = False

  def mark_inprogress(self):
    self.graded = False
    self.in_progress = True

  def mark_graded(self):
    self.graded = True
    self.in_progress = False

  def addGrader(self, grader_netid):
    self.grader = Grader.query.filter_by(netid = grader_netid).first()

  def __repr__(self):
    return 'Assignment {} {} {} {}'.format(self.course.name, self.student.netid, self.name, self.sub_date)

