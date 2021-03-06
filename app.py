# Project: codePost
# Template for Main Page
# Authors: Ayyala, Evans, Freling, Kubiak, Leichnitz
# Date: May 2014

import os
from flask import Flask, render_template, send_from_directory
from flask import Response, request, redirect, session
from flask import Blueprint
from flask import g, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from database import *
import urllib2
from xml.etree import ElementTree
import cgi
import pickle
import traceback
import json
from werkzeug import secure_filename
import tarfile
import re
import operator
from sets import Set

# initialization
app = Flask(__name__)
app.config.update(
    DEBUG = True,
)

testArray = []

# print Student.query.all()
# print Course.query.all()
Base = declarative_base()

# Verify that netid fulfills OIT requirements.
# Found here: http://www.universitypressclub.com/archive/2013/03/where-does-your-netid-come-from/
def isValidNetid(netid):
    if len(netid) < 2 or len(netid) > 8:
        return False

    if netid.isalnum():
        return True
    else:
        return False

def inSession():
    if 'netid' in session:
        return session['netid']
    else:
        return redirect('/404')

# Adds an assignment from the admin form to the assignment list as a master.
def AddtoListAssignmentMaster(files, file_name):
  ass_file = {'name': file_name, 'content': None, 'grade': "", 'annotations': []}
  files.append(ass_file)
  return files

# Allows mass upload of student files from the admin/students page, filtering by
# filename_netid
@app.route('/_mass_upload_student_files', methods=['GET', 'POST'])
def mass_upload_student_files():

    if 'netid' in session:
        netid = session['netid']
    else:
        return render_template('404.html')

    if isAdmin(netid) is False:
        return redirect('/404')

    try: 
        files = request.files.getlist('file')
        assignmentName = request.form['assignmentTitle']
    except:
        return redirect('/404')

    courseName = Admin.query.filter_by(netid = netid).first().courses[0].name
    content = ""

    studentFiles = {}
    netids = []

    master = Assignment.query.filter_by(master = True, name = assignmentName).first()
    points_possible = master.points_possible
    master_file_names = []
    for item in master.files:
        if item["name"] not in master_file_names:
            master_file_names.append(item["name"])    

    for file in files:
        filename = file.filename
        if len(filename.split('_')) != 2:
            session['error'] = filename + ' does not have the correct format. All filenames should be of the form filename_netid.'

        if re.search("([a-z])+_\w(\w)+.(c|(java))|(.txt)", filename) is not None:
            name = filename.split('_')[0] + '.' + filename.split('_')[1].split('.')[1]
            netid = filename.split('_')[1].split('.')[0]
        elif re.search("[a-z]+_(\w)(\w)+", filename) is not None:
            name = filename.split('_')[0]
            netid = filename.split('_')[1]
        else:
            session['error'] = filename + ' is an invalid filename. All filenames should be of the form filename_netid.'
            return redirect('/admin/students')

        if name not in master_file_names:
            session['error'] = name + ' is not a valid file for ' + assignmentName + '.'
            return redirect('/admin/students')

        if netid not in studentFiles:
            studentFiles[netid] = []
            netids.append(netid)

        studentFiles[netid].append({'name': name, 'content': file.read(), 'grade': "", 'annotations': []})

    for item in netids:
        student = Student.query.filter_by(netid=netid).first()
        assignment = Assignment.query.filter_by(student=student, name=assignmentName).first()
        if assignment is not None:
            id_ = assignment.id
        else:
            id_ = addAssignment(courseName, item, assignmentName, studentFiles[item])
            Assignment.query.filter_by(id = id_).update({"points_possible": points_possible})

        assignFiles = Set()
        
        for fileobject in studentFiles[netid]:
            assignFiles.add(fileobject['name'])

        x = Set()

        if set(assignFiles) != set(master_file_names):
            x = set(master_file_names).difference(set(assignFiles))

        for file_name in x:
            session['warning'] = session['warning'] + '<br>' + file_name + ' not uploaded for ' + item + '.'

        db.session.commit()

    if len(netids) == 1:
        session['success'] = "Your code uploaded successfully for 1 student!"
    else:
        session['success'] = "Your code uploaded successfully for " + str(len(netids)) + " students!"

    return redirect('/admin/students')

# Create a bunch of students from a list of netids.
@app.route('/_mass_upload_students', methods=['GET', 'POST'])
def mass_upload_students():

    if 'netid' in session:
        netid = session['netid']
    else:
        return render_template('404.html')

    if isAdmin(netid) is False:
        return redirect('/404')

    try:
        f = request.files['file']
    except:
        return redirect('/404')

    netids = f.read().split('\n')

    for item in netids:
        if isValidNetid(item) is not True:
            session['error'] = item  + ' is an invalid netid.'
            return redirect('/admin/students')

    course = Admin.query.filter_by(netid = netid).first().courses[0]
    length = len(course.students.all())
    if length > 499:
        session['error'] = 'You have reached the limit of 500 students in your course. Please delete some students to add more.'
        return redirect('/admin/students')

    counter = 0

    for item in netids:
        student = Student.query.filter_by(netid = item).first();
        if student is None:
            student = Student("name", "test", item)
            student.courses.append(course)
            db.session.add(student)
            db.session.commit()
        else:
            student.courses.append(course)
            db.session.commit()
        length = length + 1
        counter = counter + 1
        if length > 499:
            session['warning'] = 'You have reached the limit of 500 students in your course. Only ' + str(counter) + ' students were added'
            return redirect('/admin/students')


    session['success'] = 'You successfully added ' + str(len(netids)) + ' students to your course.'

    return redirect('/admin/students')

# Upload code and create a new assignment bound to a particular student.
@app.route('/_upload_student_files', methods = ['GET', 'POST'])
def upload_student_files():

    if 'netid' in session:
        netid = session['netid']
    else:
        return render_template('404.html')

    if isAdmin(netid) is False:
        return redirect('/404')

    try:
        assignmentName = request.form['assignmentTitle']
        courseName = Admin.query.filter_by(netid = netid).first().courses[0].name
        netid = request.form['netid']
    except:
        return redirect('/404')

    # Netid is automatically generated, so it should be valid.
    if isValidNetid(netid) is False:
        session['error'] = 'An unknown error ocurred.'
        return redirect('/admin/students')

    # Creates a list of the file names specified by the admin when the assignment was created
    master = Assignment.query.filter_by(master = True, name = assignmentName).first()
    points_possible = master.points_possible
    master_files = master.files
    master_file_names = []
    for item in master.files:
        if item["name"].lower() not in master_file_names:
            master_file_names.append(item["name"].lower())

    files = request.files.getlist('file')
    string = ""

    fileList = []

    for file in files:
        # HACK: identify no files uploaded by empty filename
        if file.filename == "":
            session['error'] = 'You didn\'t select any file to upload!'
            return redirect('/admin/students')

        content = file.read()
        lines = content.split('\n')

        # fix this later
        if file.filename.lower() not in master_file_names:
            session['error'] = file.filename + " is not in the list of files for the " + assignmentName + " assignment. " + netid + "\'s assignment was not uploaded."
            return redirect('admin/students')
        master_file_names.remove(file.filename)

        if len(lines) > 1000:
            session['error'] = file.filename + ' has too many lines (' + str(len(lines)) + ').'
            return redirect('/admin/students')

        ass_file = {'name': file.filename, 'content': content, 'grade': "", 'annotations': []}
        fileList.append(ass_file)


    # Checks if the student already has work for this assignment
    student = Student.query.filter_by(netid=netid).first()
    assignment = Assignment.query.filter_by(student=student, name=assignmentName).first()
    if assignment is not None:
        id_ = assignment.id
        old_files = assignment.files
        new_files = fileList
        new_file_names = []
        for item in new_files:
            if item['name'] not in new_file_names:
                new_file_names.append(item['name'])
        for item in old_files:
            if item['name'] not in new_file_names:
                new_files.append(item)
                master_file_names.remove(item['name'])
        Assignment.query.filter_by(id = id_).update({"files": new_files})
        db.session.commit()
        session['success'] = netid + "'s " + assignmentName + " assignment was updated."

    else:
        id_ = addAssignment(courseName, netid, assignmentName, fileList)
        Assignment.query.filter_by(id = id_).update({"points_possible": points_possible})
        db.session.commit()
        if len(master_file_names) == 0:
            session['success'] = 'You successfully uploaded code for ' + netid + '.'
        else:
            files_left = ""
            for item in master_file_names:
                files_left += item + " "
            session['warning'] = files_left + "was not uploaded for this assignment."

    return redirect('/admin/students')

# Called when a grader or admin marks an assignment as graded and saves the overall grade
# and the grade for each file.
@app.route('/_done', methods = ['GET', 'POST'])
def done():

    if 'netid' in session:
        netid = session['netid']
    else:
        return render_template('404.html')

    if isGrader(netid) is False and isAdmin(netid) is False:
        return render_template('404.html')
    
    try: 
        assignmentID = request.form['id']
    except:
        return redirect('/404')

    accountType = str(request.form['type'])
    assignment = Assignment.query.filter_by(id = assignmentID).first()

    new_files = assignment.files
    file_name = ""
    ungraded = False
    for item in new_files:
        file_name = str(item['name'])
        file_name = os.path.splitext(file_name)[0]
        file_grade = request.form[file_name]
        if file_grade is None or file_grade == "":
            ungraded = True
        if file_grade.isdigit() is False and re.search("(\d)+.(\d)+", file_grade) is None:
            session['error'] = "At least one of these files does not a valid grade."
            return redirect('/viewer?assignment='+assignmentID+'*'+accountType)
        item["grade"] = file_grade

    assignment_grade = request.form['total']
    if assignment_grade.isdigit() is False:
        if re.search("(\d)+.(\d)+", str(assignment_grade)) is None:
            session['error'] = "You did not submit a proper grade."
            return redirect('/viewer?assignment='+assignmentID+'*'+accountType)

    if float(assignment_grade) < 0:
        session['error'] = "Please submit a non-negative grade."
        return redirect('/viewer?assignment='+assignmentID+'*'+accountType)

    assignment.grade = float(assignment_grade)
    assignment.graded = True
    assignment.in_progress = False

    try:
        Assignment.query.filter_by(id = assignmentID).update({'files': new_files})
        db.session.commit()
        return redirect('/viewer?assignment='+assignmentID+'*'+accountType)
    except:
        return traceback.format_exc()

# Called when a grader or admin unmarks an assignment as done.
@app.route('/_undone', methods = ['GET', 'POST'])
def undone():
    try:
        assignmentID = request.form['id']
        assignment = Assignment.query.filter_by(id = assignmentID).first()
    except:
        return redirect('/404')

    accountType = request.form['type']
    assignment.in_progress = True
    assignment.graded = False
    try:
        db.session.add(assignment)
        db.session.commit()
        return redirect('/viewer?assignment='+assignmentID+'*'+accountType)
    except:
        return traceback.format_exc()

# Called when a grader "claims" an assignment from the grader page.
@app.route('/_assign')
def assign_assignment():
    if 'netid' in session:
        netid = session['netid']
    else:
        return render_template('404.html')

    if isGrader(netid) is False:
        return render_template('404.html')

    try: 
        assignID = request.args.get('id')
    except:
        return redirect('/404')

    students = Student.query.all()

    for item in students:
        assignments = item.assignments.all()
        for entry in assignments:
            if entry.id == int(assignID):
                if entry.grader is None:
                    try:
                        entry.grader = Grader.query.filter_by(netid = netid).first()
                        entry.in_progress = True
                        entry.graded = False
                        db.session.add(entry)
                        db.session.commit()
                        return "success"
                    except:
                        return traceback.format_exc()
                else:
                    return "failure"

# Called when a grader "releases" an assignment from the grader page
@app.route('/_release')
def release_assignment():
    if 'netid' in session:
        netid = session['netid']
    else:
        return render_template('404.html')

    if isGrader(netid) is False:
        return render_template('404.html')

    try: 
        assignID = request.args.get('id')
    except:
        return render_template('404.html')

    if assignID == "":
        return render_template('404.html')

    a = Assignment.query.filter_by(id  = assignID).first()
    if a is not None:
        a.mark_ungraded()
        a.grader = None
        a.grade = None
        db.session.commit()
        new_files = a.files
        for item in new_files:
            item["annotations"] = []
            item["grade"] = ""
        Assignment.query.filter_by(id = assignID).update({'files': new_files})
        return "success"

    else:
        return render_template('404.html')

# Checks if there are any existing annotations when a grader releases an assignment
@app.route('/_check_annotations')
def check_annotations():
    assignID = request.args.get('id')
    a = Assignment.query.filter_by(id  = assignID).first()
    for submission in a.files:
        annotations = submission["annotations"]
        if len(annotations) != 0:
            return "not_empty"
    return "empty"

# Checks if a student is in the database
@app.route('/_check_student')
def check_student():

    netid = str(request.args.get('netid'))
    student = Student.query.filter_by(netid=netid).first();
    if student is None:
        return ""

    assignments = Assignment.query.filter_by(student=student).all()
    if len(assignments) != 0:
        return "check"
    else:
        return ""

# Adds a single student to the database from the admin page
@app.route('/_add_student')
def add_student():
    if 'netid' in session:
        netid = session['netid']
    else:
        return render_template('404.html')

    if isAdmin(netid) is False:
        return render_template('404.html')

    studentNetid = str(request.args.get('netid'))

    if isValidNetid(studentNetid) is False:
        return "false"

    elif studentNetid == "":
        return render_template('404.html')

    course = Admin.query.filter_by(netid = netid).first().courses[0]
    courseName = course.name

    if len(course.students.all()) > 499:
        return "false"

    student = Student.query.filter_by(netid=studentNetid).first();
    if student is None:
        newStudent = Student("----", "----", studentNetid)
        newStudent.courses.append(course)
        db.session.add(newStudent)
        db.session.commit()
    else:
        student.courses.append(course)
        db.session.commit()

    return "true"

# Adds a single grader to the database from the admin page
@app.route('/_add_grader')
def add_grader():
    if 'netid' in session:
        netid = session['netid']
    else:
        return render_template('404.html')

    if isAdmin(netid) is False:
        return render_template('404.html')

    course = Admin.query.filter_by(netid = netid).first().courses[0]
    courseName = course.name

    graderNetid = str(request.args.get('netid'))
    if isValidNetid(netid) is False:
        return "false"

    if graderNetid == "":
        return render_template('404.html')

    if len(course.graders.all()) > 49:
        session['error'] = 'You have reached the limit of 50 graders.'
        return "error"

    grader = Grader.query.filter_by(netid=graderNetid).first();
    if grader is None:
        newGrader = Grader(graderNetid)
        newGrader.courses.append(course)
        db.session.add(newGrader)
        db.session.commit()
    else:
        grader.courses.append(course)
        db.session.commit()

    return "true"

# Deletes a student from the database from the admin page
@app.route('/_delete_student')
def remove_student():
    if 'netid' in session:
        netid = session['netid']
    else:
        return render_template('404.html')

    if isAdmin(netid) is False:
        return redirect('/404')

    studentNetid = str(request.args.get('netid'))

    course_object = Admin.query.filter_by(netid=netid).first().courses[0]
    
    if course_object is None:
        return "no course"
    if netid.isalnum() is False:
        return "false"

    student = Student.query.filter_by(netid=studentNetid).first()
    if student is None:
        return "true"

    assignments = Assignment.query.filter_by(student=student, course=course_object).all();
    for assignment in assignments:
        db.session.delete(assignment)

    student.courses.remove(course_object)
    db.session.add(student)
    db.session.commit()

    if len(student.courses) == 0:
        db.session.delete(student)
    
    db.session.commit()

    return "true"

# Deletes a grader from the database from the admin page
@app.route('/_delete_grader')
def remove_grader():
    netid = str(request.args.get('netid'))
    course = str(request.args.get('course'))
    course_object = Course.query.filter_by(name=course).first()
    if netid.isalnum() is False:
        return "false"

    grader = Grader.query.filter_by(netid=netid).first();
    if grader is None:
        return "true"

    grader.courses.remove(course_object)
    db.session.add(grader)
    db.session.commit()

    if grader.courses == 0:
        db.session.delete(grader)
        db.session.commit()

    assignments = Assignment.query.filter_by(grader=grader, course=course_object).all();
    for assignment in assignments:
        assignment.grader = None
        if assignment.graded != True:
            assignment.mark_ungraded()
            assignment.grader = None
            db.session.commit()
            new_files = assignment.files
            for item in new_files:
                item["annotations"] = []
            Assignment.query.filter_by(id=assignment.id).update({'files': new_files})

    return "true"

# Checks if a grader has any assignments graded
@app.route('/_check_graded_assignments')
def check_graded_assignments():
    netid = str(request.args.get('netid'))
    if netid.isalnum() is False:
        return "false"

    grader = Grader.query.filter_by(netid=netid).first();
    if grader is None:
        return "true"

    assignments = Assignment.query.filter_by(grader=grader).all();
    if len(assignments) > 0:
        return "not_empty"
    else:
        return "empty"

# Adds an assignment from the admin page
@app.route('/_add_assignment')
def add_assignment():
    if 'netid' in session:
        netid = session['netid']
    else:
        return "false"

    name = request.args.get('name')
    fileNames = request.args.get('files').split()
    rubric = request.args.get('rubric').split()
    totalPoints = request.args.get('totalPoints')
    dueDate = request.args.get('dueDate')
    if 'netid' in session:
        netid = session['netid']
    else:
        return "false"

    PERMITTED_LANGUAGES = ['c', 'cpp', 'py', 'js', 'txt', 'java']

    if len(name) == 0 or name == "":
        session['error'] = 'Please enter an assignment name.'
        return "false"

    for item in fileNames:
        if item.isalpha() is False and re.match("([a-z])+.([a-z])+", item) is None:
            session['error'] = item + ' is an invalid file name.'
            return "false"

        if item.isalpha() is False:
            ext = item.split('.')[1]
            if ext not in PERMITTED_LANGUAGES:
                session['error'] = ext + ' is not a valid file extension.'
                return "false"

    if len(fileNames) > 10:
        session['error'] = 'An assignment can have no more than 10 files.'

    if len(fileNames) != len(rubric):
        session['error'] = 'The rubric you entered does not match the number of files.'
        return "false"

    for item in rubric:
        if re.match("^(\d)+$", item) is None:
            session['error'] = 'You entered an invalid point value.'
            return "false"

    if re.match("^(\d)+$", totalPoints) is None:
        session['error'] = 'You entered an invalid point value.'
        return "false"

    admin = Admin.query.filter_by(netid=netid).first()
    course = admin.courses[0]

    masters = Assignment.query.filter_by(course=course, master=True).all()

    numMasters = len(masters)
    if numMasters > 14:
        session['error'] = 'You\'ve reached the assignment limit of 15.'
        return "false"

    for item in masters:
        if item.name.replace(" ", "").lower() == name.replace(" ", "").lower():
            session['error'] = "Assignment name is too similar to an existing assignment."
            return "false"

    assignment = Assignment(course.name, "", name)
    assignment.master = True
    assignment.points_possible = totalPoints
    assignment.rubric = rubric
    assignment.due_date = dueDate

    files = []
    for string in fileNames:
        AddtoListAssignmentMaster(files, string)

    assignment.files = files

    db.session.add(assignment)
    db.session.commit()

    session['success'] = 'You successfully created \'' + name + '\'.'

    return "true"

# Deletes a master assignment and all submitted assignments from the database from the admin page
@app.route("/_delete_assignment")
def remove_assignment():
    name = str(request.args.get('name'))
    course_name = str(request.args.get('course'))
    course_name.replace('+', ' ')
    course = Course.query.filter_by(name=course_name).first()
    assignments = Assignment.query.filter_by(name=name, course=course).all();
    assignment_count = 0
    for assignment in assignments:
        assignment_count += 1
        db.session.delete(assignment)
        db.session.commit()
    return "true"

# Delete a single assignment from the database from the admin page
@app.route("/_delete_1_assignment")
def remove_1_assignment():
    id = str(request.args.get('id'))
    assignment = Assignment.query.filter_by(id=id).first()
    # if assignment == None:
    #     return "false"
    db.session.delete(assignment)
    db.session.commit()
    return "true"

# Creates a class for an assignment to pass in additional variables
class AssignmentClass:
    def __init__(self, id, course, name, date, files, grade, grader, student, status, points):
        self.id = id
        self.course = course
        self.name = name
        self.date = date
        self.files = files
        self.grade = grade
        self.grader = grader
        self.student = student
        self.status = status
        self.points = points

# Creates a class for a student to pass in additional variables
class StudentClass:
    def __init__(self, student, avg_grade, num_assignments):
        self.student=student
        self.avg_grade=avg_grade
        self.num_assignments=num_assignments

# Creates a class for a grader to pass in additional variables
class GraderClass:
    def __init__(self, netid, avg_grade, num_in_progress, num_graded):
        self.netid = netid
        self.avg_grade = avg_grade
        self.num_in_progress = num_in_progress
        self.num_graded = num_graded

# Creates a class for a master assignment to pass in additional variables
class MasterAssignmentClass:
    def __init__(self, a, avg_grade, graded, submitted):
        self.a = a
        self.avg_grade = avg_grade
        self.graded = graded
        self.submitted = submitted

# Creates a class for an assignment to pass in additional variables for the graphs
class AssignmentProgressClass:
    def __init__(self, a, name, percent_graded, avg_grade, number, due_date):
        self.a = a
        self.name = name
        self.percent_graded = percent_graded
        self.avg_grade = avg_grade
        self.number = number
        self.due_date = due_date

# Creates a class for a file to pass in additional variables
class File:
    def __init__(self, name, code, grade, points, isReadOnly = ""):
        self.name = name.split('.')[0]
        if len(name.split('.')) > 1:
            self.ext = name.split('.')[1]
        else:
            self.ext = "plain"
        if self.ext == "c":
            self.ext = "cpp"
        if self.ext == "txt":
            self.ext = "plain"
        self.code = code
        self.grade = grade
        self.points = points # this is points possible from rubric
        self.isReadOnly = isReadOnly

# Checks if a student is in the database
def isStudent(net_id):
    netid = Student.query.filter_by(netid=net_id).first()
    if netid is None:
        return False
    else:
        return True

# Checks if a grader is in the database
def isGrader(net_id):
    netid = Grader.query.filter_by(netid=net_id).first()
    if netid is None:
        return False
    else:
        return True

# Checks if an admin is in the database
def isAdmin(net_id):
    netid = Admin.query.filter_by(netid=net_id).first()
    if netid is None:
        return False
    else:
        return True

# Checks if a user is logged in and returns the netid
def isLoggedIn(ticket, page):
    request = urllib2.Request('https://fed.princeton.edu/cas/validate?ticket=' + ticket + '&service=http://saltytyga.herokuapp.com/' + page)
    response = urllib2.urlopen(request)
    data = response.read()

    if "yes" in data:
        return data.split()[1]
    else:
        return "0"

# Checks if "yes" is in the data
def validate(data):
    if "yes" in data:
        name = data.split()[1]
        return name
    else:
        return "NO"

# Makes the roles for the dropdown menu on the top right
def makeRoles(netid):
    roles = []
    if isStudent(netid):
        roles.append("student")
    if isGrader(netid):
        roles.append("grader")
    if isAdmin(netid):
        roles.append("admin")
    return roles

# Vinay
@app.route('/store/annotations', methods = ['POST'])
def jsonify(obj, *args, **kwargs):
    res = json.dumps(obj, indent=None if request.is_xhr else 2)
    return Response(res, mimetype='application/json', *args, **kwargs)

# def jsonify(obj, *args, **kwargs):
#     res =json.dumps(obj, indent=None if request.is_xhr else 2)
#     return Response(res, mimetype='application/json', *args, **kwargs)

# Vinay
def find_Annotation(id, name):
    assignment1 = Assignment.query.filter_by(id = id).first()
    for item in assignment1.files:
        if (item["name"].split('.')[0] == name):
            return json.dumps(item["annotations"])
    return None

# Creates an annotation and adds it to the database
@app.route('/store/annotations/create', methods = ['POST'])
def create():
    data = dict(request.json)
    uri = data["uri"]
    name = uri.split(" ")[0]
    id = uri.split(" ")[1]

    a = Assignment.query.filter_by(id = id).first()
    for i in range(0, len(a.files)):
        if (a.files[i]["name"].split('.')[0] == name):
            new_files = a.files
            new_dict = dict(request.json)
            length = len(a.files[i]["annotations"])
            if length == 0:
                new_dict["id"] = 0
            else:
                old_dict = dict(a.files[i]["annotations"][length-1])
                old_id = old_dict["id"]
                new_dict["id"] = old_id + 1

            new_files[i]["annotations"].append(new_dict)
            Assignment.query.filter_by(id = id).update({'files': new_files})
            db.session.commit()
            a = Assignment.query.filter_by(id = id).first()
            return json.dumps(length)

    return json.dumps('No JSON payload sent. Annotation not created.')

# vinay
@app.route('/store/annotations/read/<id>/<name>', methods = ['GET'])
def read(id, name):
    annotation = find_Annotation(id, name)
    if annotation is None:
        obj= json.dumps('Annotation not found!')
        return Response(obj, mimetype = 'application/json', status = 404)

    return Response(annotation, mimetype = 'application/json')

# Updates an existing annotation
@app.route('/store/annotations/update/<id>/<name>/<ann_id>', methods = ['PUT'])
def update(id, name, ann_id):
    a = Assignment.query.filter_by(id = id).first()
    new_files = a.files
    new_dict = dict(request.json)
    for i in range(0, len(a.files)):
        if (a.files[i]["name"].split('.')[0] == name):
            annotations = new_files[i]["annotations"]
            for j in range(0, len(annotations)):
                if str(annotations[j]["id"]) == ann_id:
                    del annotations[j]
                    new_dict["id"] = ann_id
                    new_files[i]["annotations"].append(new_dict)
                    Assignment.query.filter_by(id = id).update({'files': new_files})
                    db.session.commit()
                    return Response(json.dumps("1"), mimetype = 'application/json')
    return Response(json.dumps("0"), mimetype = 'application/json')

# Deletes an existing annotation
@app.route('/store/annotations/destroy/<id>/<name>/<ann_id>', methods = ['DELETE'])
def destroy(id, name, ann_id):
    a = Assignment.query.filter_by(id = id).first()
    new_files = a.files
    for i in range(0, len(a.files)):
        if (a.files[i]["name"].split('.')[0] == name):
            annotations = new_files[i]["annotations"]
            for j in range(0, len(annotations)):
                if str(annotations[j]["id"]) == ann_id:
                    del annotations[j]
                    Assignment.query.filter_by(id = id).update({'files': new_files})
                    db.session.commit()
                    return Response(json.dumps("1"), mimetype = 'application/json')
    return Response(json.dumps("0"), mimetype = 'application/json')

# james
@app.route('/login')
def login():
    response = urllib2.urlopen('https://fed.princeton.edu/cas/validate?ticket=' + request.args.get('ticket') + '&service=http://saltytyga.herokuapp.com/login?dest=' + request.args.get('dest'))
    data = response.read()
    netid = validate(data)
    if netid is "NO":
        return redirect('/')
    else:
        session['username'] = netid
        return redirect('/' + request.args.get('dest'))

# vinay
@app.route('/datatest')
def datatest():
    # if isAdmin(session['username']) is False:
    #     return redirect('/')

    _admins = Admin.query.all()
    _students = Student.query.all()
    _graders = Grader.query.all()

    # student_string = ""
    # for i in _students:
    #     student_string = student_string + str(i) + ","

    string = "Students: {} \n Graders: {} \n Admins: {}".format(str(_students), str(_graders), str(_admins))
    return string

# james
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'ico/favicon.ico')

# Sends user to 404 page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Home page
@app.route("/")
def index():
    # if users can switch between modes (student, grader, admin), then we could redirect to logged-in page
    # if user is logged into CAS.

    alertString = ""
    alertMessage = ""

    if 'error' in session:
        if session['error'] == 'admin':
            alertString = "Looks like you don't have admin rights! If you think this is in error, please contact the CS department."
        elif session['error'] == 'grader':
            alertString = "Looks like you aren't signed up as a grader for any courses. If this is in error, please contact your lead preceptor."
        elif session['error'] == 'student':
            alertString = "Looks like you aren't signed up as a student for any courses. If this is in error, please contact your preceptor."

        alertMessage =  "<div class=\"alert alert-danger alert-dismissable fade in\" style=\"margin-bottom: -52px; z-index: 1\"><button type=\"button\" \
        class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button><strong>Warning! </strong>" + alertString + "</div>"

        session.pop('error', None)

    studentCode = open('Hello.java', 'r').read()

    return render_template('index3.html', alert = alertMessage, studentCode = studentCode)

# Shows the assignment with the grade and annotations for students, graders, and assignments
@app.route("/viewer")
def submitted():
    if 'assignment' not in request.args:
        return redirect('/')

    try:
        ticket = request.args.get('ticket')
    except:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/viewer?assignment=' + request.args.get('assignment'))

    if ticket is None:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/viewer?assignment=' + request.args.get('assignment'))
    if 'ticket_viewer' in session and ticket == session['ticket_viewer']:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/viewer?assignment=' + request.args.get('assignment'))

    session['ticket_viewer'] = ticket
    netid = isLoggedIn(ticket, "viewer?assignment=" + request.args.get('assignment'))
    if netid is "0":
        return redirect('/')

    session['netid'] = netid

    if request.args.get('assignment').count('*') == 1:
        assignmentID = request.args.get('assignment').split('*')[0]
        accountType = request.args.get('assignment').split('*')[1]
    else:
        return redirect('/')

    if not assignmentID.isdigit():
        return redirect('/')

    mark_row = ""
    input_ro = ""
    input_style = ""

    if accountType == "s":
        student = Student.query.filter_by(netid = netid).first()
        assignments = student.assignments.all()
        input_ro = "readonly"
        input_style = "border:none"
    elif accountType == "g":
        grader = Grader.query.filter_by(netid = netid).first()
        assignments = grader.assignments.all()
    elif accountType == "a":
        admin = Admin.query.filter_by(netid = netid).first()
        assignment = Assignment.query.filter_by(id = assignmentID).first()
        if admin is None or assignment is None:
            return redirect('/admin')
        a_courses = admin.courses
        check = False
        for item in a_courses:
            if item.id == assignment.course.id:
                check = True

        if check == False:
            return redirect('/admin')
        assignments = []
        assignments.append(assignment)
    else:
        return redirect('/')

    assignment_active = 0
    for item in assignments:
        assignment_active = 0
        if int(assignmentID) == item.id:
            assignment_active = item
            break

    if assignment_active == 0:
        if accountType == "s":
            return redirect('/student')
        else:
            return redirect('/grader')

    if accountType == "s" and assignment_active.graded != True:
        session['warning'] = 'You\'ll be able to view your assignment after it\'s been graded.'
        return redirect('/student')

    roles = makeRoles(netid)
    if (accountType == "g" and roles.count("grader") != 0):
        roles.remove("grader")
    elif (accountType == "a" and roles.count("admin") != 0):
        roles.remove("admin")
    elif (accountType == "s" and roles.count("student") != 0):
        roles.remove("student")

    title = assignment_active.name

    alertMessage = ""

    if 'error' in session:
        alertString = session['error']
        session.pop('error', None)
        alertMessage =  "<div class=\"alert alert-danger alert-dismissable fade in\" style=\"z-index: 1; margin-top: 20px;\"><button type=\"button\" \
        class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button><strong>Warning! </strong>" + alertString + "</div>"
    elif 'success' in session:
        alertString = session['success']
        session.pop('success', None)
        alertMessage =  "<div class=\"alert alert-success alert-dismissable fade in\" style=\"z-index: 1; margin-top: 20px;\"><button type=\"button\" \
        class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button><strong>Nice! </strong>" + alertString + "</div>"
    elif 'warning' in session:
        alertString = session['warning']
        session.pop('warning', None)
        alertMessage =  "<div class=\"alert alert-warning alert-dismissable fade in\" style=\"z-index: 1; margin-top: 20px;\"><button type=\"button\" \
        class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button><strong>Caution! </strong>" + alertString + "</div>"

    grading_status = ""
    status_redirection = ""
    if (assignment_active.graded):
        grading_status = "Unmark as Done"
        status_redirection = "/_undone"
        input_ro = "readonly"
        input_style = "border:none"
    else:
        grading_status = "Mark Grading as Done"
        status_redirection = "/_done"
        grader_button_display = ""
        input_ro = ""

    if accountType != "s":
        mark_row =  '<tr class="mark_as_done_row" valign="middle"><td><div class="btn-group" align="center"><input style="display: none" name="id" value="' + assignmentID + '"><input style="display: none" name="type" value="'+ accountType +'"><button id="mark_as_done" class="btn btn-default delete-buttons delete-buttons-student" type="submit" style="height:100%;width:100%;background-color: white; color: black; clear: both;" text-align="center">'+ grading_status +'</button></div></td><td></td></tr>'



    files = []
    assignment_name = assignment_active.name
    master_assignment = Assignment.query.filter_by(name=assignment_name, master=True).first()
    rubric = master_assignment.rubric

    i = 0
    for item in assignment_active.files:
        if accountType == "g" and assignment_active.graded is False:
            files.append(File(item['name'], item['content'], item['grade'], rubric[i]))
        else:
            files.append(File(item['name'], item['content'], item['grade'], rubric[i], "{readOnly: true}"))
        i += 1

    return render_template('viewer.html', mark_row = mark_row, alertMessage = alertMessage, type = accountType, roles = roles, netid = netid, a = assignment_active, assignment = files, title=title, id=assignmentID, input_ro=input_ro, input_style=input_style, grading_status=grading_status, status_redirection=status_redirection )

# Shows the grader assignments that have not been claimed and assignments he or she has claimed
@app.route("/grader")
def grader():
    try:
        ticket = request.args.get('ticket')
    except:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "grader")

    if ticket is None:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "grader")
    if 'ticket_grader' in session and ticket == session['ticket_grader']:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "grader")

    session['ticket_grader'] = ticket
    netid = isLoggedIn(ticket, "grader")
    if netid is "0":
        return redirect('/')

    session['netid'] = netid

    if isGrader(netid) is False:
        session['error'] = 'grader'
        return redirect('/')

    grader = Grader.query.filter_by(netid = netid).first()
    assignments = []
    for item in grader.courses:
        a = Assignment.query.filter_by(course=item).all()
        for assign_ in a:
            assignments.append(assign_)

    if grader is None:
        redirect('/')

    alertMessage = ""

    if 'error' in session:
        alertString = session['error']
        session.pop('error', None)
        alertMessage =  "<div class=\"alert alert-danger alert-dismissable fade in\" style=\"z-index: 1; margin-top: 20px;\"><button type=\"button\" \
        class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button><strong>Warning! </strong>" + alertString + "</div>"
    elif 'success' in session:
        alertString = session['success']
        session.pop('success', None)
        alertMessage =  "<div class=\"alert alert-success alert-dismissable fade in\" style=\"z-index: 1; margin-top: 20px;\"><button type=\"button\" \
        class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button><strong>Nice! </strong>" + alertString + "</div>"
    elif 'warning' in session:
        alertString = session['warning']
        session.pop('warning', None)
        alertMessage =  "<div class=\"alert alert-warning alert-dismissable fade in\" style=\"z-index: 1; margin-top: 20px;\"><button type=\"button\" \
        class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button><strong>Caution! </strong>" + alertString + "</div>"

    button_html = "<button type=\"button\" class=\"btn\" style=\"color: black; background-color: white; border: 1px solid black;\">Claim</button>"
    release_html = "&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <button type=\"button\" class=\"btn\" style=\"color: black; background-color: white; border: 1px solid black;\">Release</button>"

    assignments_form = []
    for item in assignments:
        if item.graded:
            status = "Graded"
        elif item.in_progress:
            status = "In Progress"
        else:
            status = "--------"
        if item.master is False and item.grader is None and item.student is not None:
            assignments_form.append(AssignmentClass(item.id, item.course.name, item.name, "", item.files, "40/40", "None", item.student.netid, status, item.points_possible))
        elif item.master is False and item.grader is not None and item.grader.netid == netid and item.student is not None:
            assignments_form.append(AssignmentClass(item.id, item.course.name, item.name, "", item.files, "40/40", item.grader.netid, item.student.netid, status, item.points_possible))

    classes = []
    for item in grader.courses:
        classes.append(item.name)
    # for item in assignments_form:
    #     if item.course not in classes:
    #         classes.append(item.course)

    assignment_names = []
    for item in assignments_form:
        if item.name not in assignment_names:
            assignment_names.append(item.name)

    status = []


    graders = set()
    for item in assignments_form:
        if item.grader not in assignment_names:
            if item.grader == button_html:
                graders.add("None")
            else:
                graders.add(item.grader)

    roles = makeRoles(netid)
    if (roles.count("grader") != 0):
        roles.remove("grader")

    return render_template('grader.html', alertMessage = alertMessage, netid=netid, roles = roles, classes = classes, assignments=assignments_form, assignment_names=assignment_names, graders=graders)

# Shows the student all of their submitted assignments
@app.route("/student")
def student():
    try:
        ticket = request.args.get('ticket')
    except:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "student")

    if ticket is None:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "student")
    if 'ticket_student' in session and ticket == session['ticket_student']:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "student")

    session['ticket_student'] = ticket
    netid = isLoggedIn(ticket, "student")
    if netid is "0":
        return redirect('/')

    session['netid'] = netid

    if isStudent(netid) is False:
        session['error'] = 'student'
        return redirect('/')

    alertMessage=""

    if 'error' in session:
        alertString = session['error']
        session.pop('error', None)
        alertMessage =  "<div class=\"alert alert-danger alert-dismissable fade in\" style=\"z-index: 1; margin-top: 20px;\"><button type=\"button\" \
        class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button><strong>Warning! </strong>" + alertString + "</div>"
    elif 'success' in session:
        alertString = session['success']
        session.pop('success', None)
        alertMessage =  "<div class=\"alert alert-success alert-dismissable fade in\" style=\"z-index: 1; margin-top: 20px;\"><button type=\"button\" \
        class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button><strong>Nice! </strong>" + alertString + "</div>"
    elif 'warning' in session:
        alertString = session['warning']
        session.pop('warning', None)
        alertMessage =  "<div class=\"alert alert-warning alert-dismissable fade in\" style=\"z-index: 1; margin-top: 20px;\"><button type=\"button\" \
        class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button><strong>Caution! </strong>" + alertString + "</div>"

    student = Student.query.filter_by(netid = netid).first()
    assignments = student.assignments.all()

    assignments_form = []
    for item in assignments:
        grade = ""
        if item.graded is True:
            grade = str(item.grade) + " / " + str(item.points_possible)
            status = "Graded"
        elif item.in_progress is True:
            grade = "In Progress"
            status = "In Progress"
        else:
            grade = "In Progress"
            status = "--------"
        assignments_form.append(AssignmentClass(item.id, item.course.name, item.name, item.sub_date, item.files, grade, "", item.student.netid, status, item.points_possible))

    classes = []

    for item in student.courses:
        classes.append(item.name)

    roles = makeRoles(netid)
    if (roles.count("student") != 0):
        roles.remove("student")

    return render_template('student.html', netid=netid, classes = classes, roles = roles, assignments = assignments_form, alertMessage = alertMessage)

# Shows graphs and data about submitted and graded assignments.
@app.route("/admin")
def admin():
    try:
        ticket = request.args.get('ticket')
    except:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "admin")

    if ticket is None:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "admin")
    if 'ticket_admin' in session and ticket == session['ticket_admin']:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "admin")

    session['ticket_admin'] = ticket
    netid = isLoggedIn(ticket, "admin")

    if netid is "0":
        return redirect('/')

    session['netid'] = netid

    if isAdmin(netid) is False:
        session['error'] = 'admin'
        return redirect('/')

    admin = Admin.query.filter_by(netid = netid).first()
    course = admin.courses[0]
    assignment_db = Assignment.query.filter_by(course = course, master = True).all()

    assignments = []
    for assignment in assignment_db:
        graded = 0.0
        avg_grade = 0.0
        total_grade = 0.0
        submitted = 0.0
        non_master = Assignment.query.filter_by(course = course, master = False, name = assignment.name).all()
        for a in non_master:
            if a.graded == True:
                graded += 1
                if a.points_possible != None:
                    total_grade += a.grade/a.points_possible*100
            else:
                submitted += 1
        submitted += graded
        percent_graded = 0.0
        if submitted == 0:
            percent_graded = 0.0
        elif graded != 0:
            percent_graded = str(int(graded/submitted * 100))
            avg_grade = str(int(total_grade/graded))
        assignments.append(AssignmentProgressClass(assignment, assignment.name, percent_graded, avg_grade, 0, assignment.due_date))

    assignments.sort(key=operator.attrgetter('due_date'), reverse=True)

    graph1_assignments = []
    graph2_assignments = []
    i = 0
    while (i < 4 and i < len(assignments)):
        assignments[i].number = i
        graph1_assignments.append(assignments[i])
        i += 1

    i = 0
    while (i < 10 and i < len(assignments)):
        graph2_assignments.append(assignments[i])
        i += 1

    roles = makeRoles(netid)
    if (roles.count("admin") != 0):
        roles.remove("admin")

    if len(graph1_assignments) == 0:
        areAssignments = "none"
    else:
        areAssignments = "initial"

    if areAssignments is "none":
        notAreAssignments = "initial"
    else:
        notAreAssignments = "none"

    forHist = {}
    testAssignment = Assignment.query.filter_by(course = course, master = False, graded=True).all()
    for item in testAssignment:
        if item.name.replace(" ", "") not in forHist:
            forHist[item.name.replace(" ", "")] = {}       
        if item.grade not in forHist[item.name.replace(" ", "")]:
            forHist[item.name.replace(" ", "")][item.grade] = 1
        else:
            forHist[item.name.replace(" ", "")][item.grade] = forHist[item.name.replace(" ", "")][item.grade] + 1

    return render_template('admin2.html', forHist = forHist, areAssignments = areAssignments, notAreAssignments = notAreAssignments, course=course.name, netid=netid, roles = roles, graph1_assignments=graph1_assignments, graph2_assignments=graph2_assignments)

# Shows the admin all of the students in that course
@app.route("/admin/students")
def admin_students():
    #######################################
    # Boiler plate CAS authentication
    #######################################
    try:
        ticket = request.args.get('ticket')
    except:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "admin/students")

    if ticket is None:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "admin/students")
    if 'ticket_admin' in session and ticket == session['ticket_admin']:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "admin/students")

    session['ticket_admin'] = ticket
    netid = isLoggedIn(ticket, "admin/students")
    if netid is "0":
        return redirect('/')

    session['netid'] = netid

    roles = makeRoles(netid)
    if (roles.count("admin") != 0):
        roles.remove("admin")

    #######################################

    # Check to see if an error occured before refresh.
    alertMessage = ""

    if 'error' in session:
        alertString = session['error']
        session.pop('error', None)
        alertMessage =  "<div class=\"alert alert-danger alert-dismissable fade in\" style=\"z-index: 1; margin-top: 20px;\"><button type=\"button\" \
        class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button><strong>Warning! </strong>" + alertString + "</div>"
    elif 'success' in session:
        alertString = session['success']
        session.pop('success', None)
        alertMessage =  "<div class=\"alert alert-success alert-dismissable fade in\" style=\"z-index: 1; margin-top: 20px;\"><button type=\"button\" \
        class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button><strong>Nice! </strong>" + alertString + "</div>"
    elif 'warning' in session:
        alertString = session['warning']
        session.pop('warning', None)
        alertMessage =  "<div class=\"alert alert-warning alert-dismissable fade in\" style=\"z-index: 1; margin-top: 20px;\"><button type=\"button\" \
        class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button><strong>Caution! </strong>" + alertString + "</div>"


    # Load all students in admin's class.
    admin = Admin.query.filter_by(netid = netid).first()
    course = admin.courses[0]
    students_db = course.students.all()

    students_form = []

    for student in students_db:
        avg_grade = 0
        submitted = 0
        graded = 0
        total_grade = 0
        assignments = Assignment.query.filter_by(student=student, course = course).all()
        for a in assignments:
            submitted += 1
            if a.graded == True:
                if a.points_possible != None and a.points_possible != 0:
                    total_grade += a.grade/a.points_possible*100
                graded += 1
        if graded != 0:
            avg_grade = str(int(total_grade/graded)) + "%"
        else:
            avg_grade = "---"
        students_form.append(StudentClass(student, avg_grade, submitted))

    assignment_db = course.assignments.all()

    masters = []

    assignments_master = Assignment.query.filter_by(master=True).all()
    for assignment in assignments_master:
        if assignment.course == course and assignment not in masters:
            masters.append(assignment)

    # Load assignments for reference when uploading code.
    # for assignment in assignment_db:
    #     if assignment.master is True:
    #         masters.append(assignment)

    return render_template('admin_students.html', course=course.name, students=students_form, netid=netid, roles = roles, masters = masters, alert = alertMessage)

# Shows the admin all of the graders for that course 
@app.route("/admin/graders")
def admin_graders():
    try:
        ticket = request.args.get('ticket')
    except:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "admin/graders")

    if ticket is None:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "admin/graders")
    if 'ticket_admin' in session and ticket == session['ticket_admin']:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "admin/graders")

    session['ticket_admin'] = ticket
    netid = isLoggedIn(ticket, "admin/graders")
    if netid is "0":
        return redirect('/')

    session['netid'] = netid

    roles = makeRoles(netid)
    if (roles.count("admin") != 0):
        roles.remove("admin")

    admin = Admin.query.filter_by(netid = netid).first()
    course = admin.courses[0]
    graders = course.graders

    alertMessage = ""

    if 'error' in session:
        alertString = session['error']
        session.pop('error', None)

        alertMessage =  "<div class=\"alert alert-danger alert-dismissable fade in\" style=\"z-index: 1; margin-top: 20px;\"><button type=\"button\" \
        class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button><strong>Warning! </strong>" + alertString + "</div>"
    elif 'success' in session:
        alertString = session['success']
        session.pop('success', None)
        alertMessage =  "<div class=\"alert alert-success alert-dismissable fade in\" style=\"z-index: 1; margin-top: 20px;\"><button type=\"button\" \
        class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button><strong>Nice! </strong>" + alertString + "</div>"
    elif 'warning' in session:
        alertString = session['warning']
        session.pop('warning', None)
        alertMessage =  "<div class=\"alert alert-warning alert-dismissable fade in\" style=\"z-index: 1; margin-top: 20px;\"><button type=\"button\" \
        class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button><strong>Caution! </strong>" + alertString + "</div>"

    grader_db = []
    for grader in graders:
        num_graded = 0
        num_in_progress = 0
        total_grade = 0
        avg_grade = 0
        assignments = Assignment.query.filter_by(grader=grader, course=course).all()
        for assignment in assignments:
            if assignment.points_possible != None and assignment.grade != None:
                total_grade += float(assignment.grade)/assignment.points_possible*100
            if assignment.graded == True:
                num_graded += 1
            elif assignment.in_progress == True:
                num_in_progress += 1
        if num_graded != 0:
            avg_grade = total_grade/num_graded
            avg_grade = str(int(avg_grade)) + "%"
        else:
            avg_grade = '---'

        grader_db.append(GraderClass(grader.netid, avg_grade, num_in_progress, num_graded))

    return render_template('admin_graders.html', course=course.name, graders=grader_db, netid=netid, roles = roles)

# Shows the assignments a particular student has submitted for the admin's course
@app.route('/admin/student_assignment')
def admin_student_assignment():
    try:
        ticket = request.args.get('ticket')
    except:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "admin/student_assignment?student=" + request.args.get('student'))

    if ticket is None:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "admin/student_assignment?student=" + request.args.get('student'))
    if 'ticket_admin' in session and ticket == session['ticket_admin']:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "admin/student_assignment?student=" + request.args.get('student'))

    session['ticket_admin'] = ticket

    admin_netid = isLoggedIn(ticket, "admin/student_assignment?student=" + request.args.get('student'))

    if admin_netid is "0":
        return redirect('/')

    session['netid'] = admin_netid

    student_netid=request.args.get('student')

    roles=makeRoles(admin_netid)
    if (roles.count("admin") != 0):
        roles.remove("admin")
    student = Student.query.filter_by(netid=student_netid).first()
    admin = Admin.query.filter_by(netid=admin_netid).first()
    course = admin.courses[0]
    assignments_student = Assignment.query.filter_by(student=student).all()
    assignments=[]
    for assignment in assignments_student:
        if assignment.course is course and assignment.master is False:
            assignments.append(assignment)
    return render_template('admin_student_assignment.html', course=course.name, roles=roles, netid=admin_netid, student_netid=student_netid, assignments=assignments)

# Shows the assignments a grader has graded for the admin's course
@app.route('/admin/grader_assignment')
def admin_grader_assignments(): 
    try:
        ticket = request.args.get('ticket')
    except:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "admin/grader_assignment?grader=" + request.args.get('grader'))

    if ticket is None:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "admin/grader_assignment?grader=" + request.args.get('grader'))
    if 'ticket_admin' in session and ticket == session['ticket_admin']:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "admin/grader_assignment?grader=" + request.args.get('grader'))

    session['ticket_admin'] = ticket

    admin_netid = isLoggedIn(ticket, "admin/grader_assignment?grader=" + request.args.get('grader'))

    if admin_netid is "0":
        return redirect('/') 

    session['netid'] = admin_netid

    gradernetid= request.args.get('grader')
    roles=makeRoles(admin_netid)
    if (roles.count("admin") != 0):
        roles.remove("admin")

    grader = Grader.query.filter_by(netid=gradernetid).first()
    admin = Admin.query.filter_by(netid=admin_netid).first()
    course = admin.courses[0]
    assignments_grader = Assignment.query.filter_by(grader=grader).all()
    assignments=[]
    for assignment in assignments_grader:
        if assignment.course is course and assignment.master is False:
            assignments.append(assignment)
    return render_template('admin_grader_assignments.html', course=course.name, roles=roles, netid=admin_netid, gradernetid=gradernetid, assignments=assignments)

# Page for all of the submitted assignments within a specified master assignment 
@app.route('/admin/all_assignments')
def admin_all_assignments():
    try:
        ticket = request.args.get('ticket')
    except:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "admin/all_assignments?id=" + request.args.get('id'))

    if ticket is None:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "admin/all_assignments?id=" + request.args.get('id'))
    if 'ticket_admin' in session and ticket == session['ticket_admin']:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "admin/all_assignments?id=" + request.args.get('id'))

    session['ticket_admin'] = ticket

    admin_netid = isLoggedIn(ticket, "admin/all_assignments" + "?id=" + request.args.get('id'))

    session['netid'] = admin_netid

    if admin_netid is "0":
        return redirect('/') 

    roles = makeRoles(admin_netid)
    if (roles.count("admin") != 0):
        roles.remove("admin")

    master = Assignment.query.filter_by(id = request.args.get('id')).first()
    assignment_name = master.name

    admin = Admin.query.filter_by(netid=admin_netid).first()
    course = admin.courses[0]
    assignments = Assignment.query.filter_by(name=assignment_name, course=course, master = False).all()

    return render_template('admin_assignment_assignments.html', course=course.name, roles=roles, assignment_name=assignment_name, netid=admin_netid, assignments=assignments)

# Page for all master assignments for the admin's course
@app.route("/admin/assignments")
def admin_admins():
    try:
        ticket = request.args.get('ticket')
    except:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "admin/assignments")

    if ticket is None:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "admin/assignments")
    if 'ticket_admin' in session and ticket == session['ticket_admin']:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "admin/assignments")

    session['ticket_admin'] = ticket
    netid = isLoggedIn(ticket, "admin/assignments")
    if netid is "0":
        return redirect('/')

    session['netid'] = netid

    roles = makeRoles(netid)
    if (roles.count("admin") != 0):
        roles.remove("admin")

    alertMessage = ""

    if 'error' in session:
        alertString = session['error']
        alertMessage =  "<div class=\"alert alert-danger alert-dismissable fade in\" style=\"z-index: 1; margin-top: 20px;\"><button type=\"button\" \
        class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button><strong>Warning! </strong>" + alertString + "</div>"

        session.pop('error', None)
    elif 'success' in session:
        alertString = session['success']
        session.pop('success', None)
        alertMessage =  "<div class=\"alert alert-success alert-dismissable fade in\" style=\"z-index: 1; margin-top: 20px;\"><button type=\"button\" \
        class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button><strong>Nice! </strong>" + alertString + "</div>"

    admin = Admin.query.filter_by(netid = netid).first()
    course = admin.courses[0]
    assignment_db = Assignment.query.filter_by(course = course, master = True).all()

    assignments = []
    for assignment in assignment_db:
        avg_grade = 0
        total_grade = 0
        graded = 0
        submitted = 0
        non_master = Assignment.query.filter_by(course = course, master = False, name = assignment.name).all()
        for a in non_master:
            if a.graded == True:
                graded += 1
                if a.points_possible != None:
                    total_grade += a.grade/a.points_possible*100
            else:
                submitted += 1
        submitted += graded
        if graded != 0:
            avg_grade = str(int(total_grade/graded)) + "%"
        else:
            avg_grade = "---"
        assignments.append(MasterAssignmentClass(assignment, avg_grade, graded, submitted))

    return render_template('admin_admins.html', assignments=assignments, netid= netid, roles = roles, alert = alertMessage, course=course.name)

# implements CAS logout
@app.route("/logout")
def logout():
    session.pop('netid', None)
    return redirect('https://fed.princeton.edu/cas/logout')

if __name__ == "__main__":
    app.secret_key = 'qeqg;abuerjabyekeusxjblelauwbajbhvyhenssj'
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
