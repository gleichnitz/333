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


def AddtoListAssignmentMaster(files, file_name):
  #file_ = open(file_name, 'r')
  #file_content = file_.read()
  ass_file = {'name': file_name, 'content': None, 'grade': "", 'annotations': []}
  files.append(ass_file)
  return files

@app.route('/_mass_upload_student_files', methods=['GET', 'POST'])
def mass_upload_student_files():
    files = request.files.getlist('file')
    assignmentName = request.form['assignmentTitle']
    content = ""

    studentFiles = {}
    netids = []

    for file in files:
        text = file.read()
        netid = re.search("netid:\s*[a-z]+", text).group(0).split()[1]
        if netid not in studentFiles:
            studentFiles[netid] = []
            netids.append(netid)
        studentFiles[netid].append({'name': file.filename, 'content': text, 'grade': "", 'annotations': []})

    for item in netids:
        addAssignment("cos333", item, assignmentName, studentFiles[item])

    return "true"

# Create a bunch of students from a list of netids.
@app.route('/_mass_upload_students', methods=['GET', 'POST'])
def mass_upload_students():
    f = request.files['netids']
    courseName = form.request['courseid']
    netids = f.read().split('\n')

    for item in netids:
        if isValidNetid(item) is not True:
            session['error'] = 'invalidid'
            return redirect('/admin/students')

    course = Course.query.filter_by(name= courseName).first()

    for item in netids:
        student = Student.query.filter_by(netid = item).first();
        if student is None:
            student = Student("name", "test", item)
            student.courses.add(course)
            db.session.add(newStudent)
            db.session.commit()
        else:
            student.courses.add(course)
            db.session.commit()


    return redirect('/admin/students')

# Upload code and create a new assignment bound to a particular student.
@app.route('/_upload_student_files', methods = ['GET', 'POST'])
def upload_student_files():
    assignmentName = request.form['assignmentTitle']
    netid = request.form['netid']

    # Netid is automatically generated, so it should be valid.
    if isValidNetid(netid) is False:
        session['error'] = 'unk'
        return redirect('/admin/students')

    files = request.files.getlist('file')
    string = ""

    fileList = []

    for file in files:
        # HACK: identify no files uploaded by empty filename
        if file.filename == "":
            session['error'] = 'nofiles'
            return redirect('/admin/students')

        ass_file = {'name': file.filename, 'content': file.read(), 'grade': "", 'annotations': []}
        fileList.append(ass_file)

    addAssignment("cos333", netid, assignmentName, fileList)

    return redirect('/admin/students')

@app.route('/_done', methods = ['POST'])
def done():
    assignmentID = request.form['id']
    assignment = Assignment.query.filter_by(id = assignmentID).first()

    new_files = assignment.files
    file_name = ""
    for item in new_files:
        ##file_name = item.get('name')
        ##file_name = item
        file_name = str(item['name'])
        file_name = os.path.splitext(file_name)[0]
        file_grade = request.form[file_name]
        ## will be easier if rubric is a dictionary with key being filename
        ## list is fine for now
        item["grade"] = file_grade

    assignment.grade = float(request.form['total'])
    assignment.graded = True
    assignment.in_progress = False

    try:
        Assignment.query.filter_by(id = assignmentID).update({'files': new_files})
        db.session.commit()
        return redirect('/grader')
    except:
        return traceback.format_exc()

@app.route('/_undone', methods = ['POST'])
def undone():
    assignmentID = request.form['id']
    assignment = Assignment.query.filter_by(id = assignmentID).first()

    assignment.in_progress = True
    assignment.graded = False
    try:
        db.session.add(assignment)
        db.session.commit()
        return redirect('/grader')
    except:
        return traceback.format_exc()

@app.route('/_change_grade')
def change_grade():
    value = request.args.get('grade')
    file_name = request.args.get('file')
        # add code to change rubric for this file

@app.route('/_assign')
def assign_assignment():

    assignID = request.args.get('id')
    netid = str(request.args.get('netid')).strip()
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

@app.route('/_release')
def release_assignment():

    assignID = request.args.get('id')
    netid = str(request.args.get('netid')).strip()

    a = Assignment.query.filter_by(id  = assignID).first()
    if a is not None:
        a.mark_ungraded()
        a.grader = None
        db.session.commit()
        new_files = a.files
        for item in new_files:
            item["annotations"] = []
        Assignment.query.filter_by(id = assignID).update({'files': new_files})
        return "success"

    else:
        return "failure"

@app.route('/_check_annotations')
def check_annotations():
    assignID = request.args.get('id')
    a = Assignment.query.filter_by(id  = assignID).first()
    for submission in a.files:
        annotations = submission["annotations"]
        if len(annotations) != 0:
            return "not_empty"
    return "empty"

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

@app.route('/_add_student')
def add_student():
    courseName = request.args.get('courseid')
    netid = str(request.args.get('netid'))
    if netid.isalnum() is False:
        return "false"

    course = Course.query.filter_by(name = courseName).first()

    student = Student.query.filter_by(netid=netid).first();
    if student is None:
        newStudent = Student("name", "test", netid)
        newStudent.courses.append(course)
        db.session.add(newStudent)
        db.session.commit()
    else:
        student.courses.append(course)
        db.session.commit()

    return "true"

@app.route('/_add_grader')
def add_grader():
    courseName = request.args.get('courseid')
    netid = str(request.args.get('netid'))
    if isValidNetid(netid) is False:
        return "false"

    course = Course.query.filter_by(name = courseName).first()
    grader = Grader.query.filter_by(netid=netid).first();
    if grader is None:
        newGrader = Grader(netid)
        newGrader.courses.append(course)
        db.session.add(newGrader)
        db.session.commit()
    else:
        grader.courses.append(course)
        db.session.commit()

    return "true"

@app.route('/_delete_student')
def remove_student():
    netid = str(request.args.get('netid'))
    if netid.isalnum() is False:
        return "false"

    student = Student.query.filter_by(netid=netid).first();
    if student is None:
        return "true"
    assignments = Assignment.query.filter_by(student=student).all();
    for assignment in assignments:
        db.session.delete(assignment)

    db.session.delete(student)
    db.session.commit()

    return "true"

@app.route('/_delete_grader')
def remove_grader():
    netid = str(request.args.get('netid'))
    if netid.isalnum() is False:
        return "false"

    grader = Grader.query.filter_by(netid=netid).first();
    if grader is None:
        return "true"

    db.session.delete(grader)
    db.session.commit()

    assignments = Assignment.query.filter_by(grader=grader).all();
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

@app.route('/_add_assignment')
def add_assignment():
    name = request.args.get('name')
    fileNames = request.args.get('files').split()
    rubric = request.args.get('rubric').split()
    totalPoints = request.args.get('totalPoints')
    dueDate = request.args.get('dueDate')
    netid = request.args.get('form_netid')

    if len(name) == 0 or name == "":
        session['error'] = 'noname'
        return "false"

    for item in fileNames:
        if item.isalpha() is False and re.match("^([a-z])+.(c|(java))$", item) is None:
            session['error'] = 'invalidfilename'
            return "false"

    if len(fileNames) != len(rubric):
        session['error'] = 'rubricmismatch'
        return "false"

    for item in rubric:
        if re.match("^(\d)+$", item) is None:
            session['error'] = 'invalidrubric'
            return "false"

    if re.match("^(\d)+$", totalPoints) is None:
        session['error'] = 'invalidpoints'
        return "false"

    admin = Admin.query.filter_by(netid=netid).first()
    course = admin.courses[0]

    assignment = Assignment(course.name, "", name)
    assignment.master = True
    assignment.points_possible = totalPoints
    assignment.rubric = rubric
    assignment.due_date = dueDate

    i = 0
    files = []
    for string in fileNames:
        string["grade"] = rubric[i]
        AddtoListAssignmentMaster(files, string)
        i += 1

    assignment.files = files

    db.session.add(assignment)
    db.session.commit()

    return redirect('/admin/assignments')

@app.route("/_delete_assignment")
def remove_assignment():
    name = str(request.args.get('name'))
    assignments = Assignment.query.filter_by(name=name).all();
    for assignment in assignments:
        db.session.delete(assignment)
        db.session.commit()
    return "true"

@app.route("/_delete_1_assignment")
def remove_1_assignment():
    id = str(request.args.get('id'))
    assignment = Assignment.query.filter_by(id=id).first()
    # if assignment == None:
    #     return "false"
    db.session.delete(assignment)
    db.session.commit()
    return "true"

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

class GraderClass:
    def __init__(self, netid, num_graded):
        self.netid = netid
        self.num_graded = num_graded

class File:
    def __init__(self, name, code, grade, isReadOnly = ""):
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
        self.isReadOnly = isReadOnly

class StudentClass:
    def __init__(self, name, netid):
        self.name = name
        self.netid = netid

def isStudent(net_id):
    netid = Student.query.filter_by(netid=net_id).first()
    if netid is None:
        return False
    else:
        return True

def isGrader(net_id):
    netid = Grader.query.filter_by(netid=net_id).first()
    if netid is None:
        return False
    else:
        return True

def isAdmin(net_id):
    netid = Admin.query.filter_by(netid=net_id).first()
    if netid is None:
        return False
    else:
        return True

def isLoggedIn(ticket, page):
    response = urllib2.urlopen('https://fed.princeton.edu/cas/validate?ticket=' + ticket + '&service=http://saltytyga.herokuapp.com/' + page)
    data = response.read()
    if "yes" in data:
        return data.split()[1]
    else:
        return "0"

def validate(data):
    if "yes" in data:
        name = data.split()[1]
        return name
    else:
        return "NO"

def makeRoles(netid):
    roles = []
    if isStudent(netid):
        roles.append("student")
    if isGrader(netid):
        roles.append("grader")
    if isAdmin(netid):
        roles.append("admin")
    return roles

@app.route('/store/annotations', methods = ['POST'])
def jsonify(obj, *args, **kwargs):
    res = json.dumps(obj, indent=None if request.is_xhr else 2)
    return Response(res, mimetype='application/json', *args, **kwargs)

# def jsonify(obj, *args, **kwargs):
#     res = json.dumps(obj, indent=None if request.is_xhr else 2)
#     return Response(res, mimetype='application/json', *args, **kwargs)

def find_Annotation(id, name):
    assignment1 = Assignment.query.filter_by(id = id).first()
    for item in assignment1.files:
        if (item["name"].split('.')[0] == name):
            return json.dumps(item["annotations"])
    return None

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


@app.route('/store/annotations/read/<id>/<name>', methods = ['GET'])
def read(id, name):
    annotation = find_Annotation(id, name)
    if annotation is None:
        obj= json.dumps('Annotation not found!')
        return Response(obj, mimetype = 'application/json', status = 404)

    return Response(annotation, mimetype = 'application/json')


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


# @app.route('/store/annotations/search', methods = ['GET'])
# def search:


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

# controllers
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

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'ico/favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

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

    return render_template('index3.html', alert = alertMessage)

@app.route("/index3")
def index3():
    return render_template('index3.html')

@app.route("/account")
def account():
    try:
        ticket = request.args.get('ticket')
    except:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "account")

    if ticket is None:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "account")
    if 'ticket_account' in session and ticket == session['ticket_account']:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "account")

    session['ticket_account'] = ticket
    netid = isLoggedIn(ticket, "account")
    roles = makeRoles(netid)

    if netid is "0":
        return redirect('/')
    return render_template('account.html', roles=roles, netid=netid)

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
    netid = isLoggedIn(ticket, "viewer?assignment=" + request.args.get('assignment') + "&type=student")
    if netid is "0":
        return redirect('/')

    if 'assignment' in request.args:
        assignmentID = request.args.get('assignment').split('*')[0]
        accountType = request.args.get('assignment').split('*')[1]
    else:
        return redirect('/')

    grader_button_display = ""
    input_ro = ""
    input_style = ""

    if accountType == "s":
        student = Student.query.filter_by(netid = netid).first()
        assignments = student.assignments.all()
        grader_button_display = "none"
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
        ### THIS IS GOING TO CHANGE!!!!
        a_courses = admin.courses
        check = False
        for item in a_courses:
            if item.id == assignment.course.id:
                check = True

        if check == False:
            return redirect('/admin')
        assignments = []
        assignments.append(assignment)

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
        return redirect('/student')

    roles = makeRoles(netid)
    if (roles.count("grader") != 0):
        roles.remove("grader")

    title = assignment_active.name


    grading_status = ""
    status_redirection = ""
    if (assignment_active.graded):
        grading_status = "Unmark as Done"
        status_redirection = "/_undone"
        input_ro = "readonly"
        input_style = "border:none"
    elif (assignment_active.in_progress):
        grading_status = "Mark Grading as Done"
        status_redirection = "/_done"

    files = []
    for item in assignment_active.files:
        if accountType == "g":
            files.append(File(item['name'], item['content'], item['grade']))
        else:
            files.append(File(item['name'], item['content'], item['grade'], "{readOnly: true}"))

    ##################################
    # need to pass: item containing assignment files to be loaded
    #               fields:
    #               - name (e.g. "percolaton.java")
    #               - grade ("10/10")
    #               - code (in a big string)
    ##################################

    # render_template('viewer.html', netid = session['username'], assignment=)
    return render_template('viewer.html', roles = roles, netid = netid, a = assignment_active, assignment = files, title=title, id=assignmentID, button_display=grader_button_display, input_ro=input_ro, input_style=input_style, grading_status=grading_status, status_redirection=status_redirection )

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

    if isGrader(netid) is False:
        session['error'] = 'grader'
        return redirect('/')

    ##################################
    # need to pass: class grader is assigned to
    # need to pass: item containing all assignments under that class
    #               fields:
    #               - id
    #               - class (e.g. COS 126)
    #               - name ("Percolation")
    #               - graded by (netid)
    #               - grade
    ##################################

    grader = Grader.query.filter_by(netid = netid).first()
    #course = grader.courses[0]
    assignments = Assignment.query.all()

    if grader is None:
        redirect('/')

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
    for item in assignments_form:
        if item.course not in classes:
            classes.append(item.course)

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

    return render_template('grader.html', netid=netid, roles = roles, classes = classes, assignments=assignments_form, assignment_names=assignment_names, graders=graders)



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

    if isStudent(netid) is False:
        session['error'] = 'student'
        return redirect('/')

    ##################################
    # need to pass: item containing all classes student is in
    # need to pass: item containing all assignments
    #               fields:
    #               - id
    #               - class (e.g. COS 126)
    #               - name ("Percolation")
    #               - date
    #               - grade
    ##################################

    # return render_template('student.html', netid=session['username'], classes=, assignments=)

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

    return render_template('student.html', netid=netid, classes = classes, roles = roles, assignments = assignments_form)

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
    admin = Admin.query.filter_by(netid=netid).first()
    course = admin.courses[0]

    if netid is "0":
        return redirect('/')

    roles = makeRoles(netid)
    if (roles.count("admin") != 0):
        roles.remove("admin")

    return render_template('admin2.html', course=course.name, netid=netid, roles = roles)

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

    roles = makeRoles(netid)
    if (roles.count("admin") != 0):
        roles.remove("admin")

    #######################################

    # Check to see if an error occured before refresh.
    alertMessage = ""

    if 'error' in session:
        if session['error'] == 'unk':
            alertString = "An unknown error occurred while uploading student code. Please try again."
        elif session['error'] == 'nofiles':
            alertString = "No files were selected to upload."
        elif session['error'] == 'invalidid':
            alertString = "The file you uploaded contained an invalid netid. Please try again."
        else:
            alertString = "Test"

        session.pop('error', None)

        alertMessage =  "<div class=\"alert alert-danger alert-dismissable fade in\" style=\"z-index: 1; margin-top: 20px;\"><button type=\"button\" \
        class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button><strong>Warning! </strong>" + alertString + "</div>"


    # Load all students in admin's class.
    admin = Admin.query.filter_by(netid = netid).first()
    course = admin.courses[0]
    students_db = course.students.all()

    course = admin.courses[0]

    students_form = []

    for student in students_db:
        students_form.append(StudentClass("no name", student.netid))

    assignment_db = course.assignments.all()

    masters = []

    # Load assignments for reference when uploading code.
    for assignment in assignment_db:
        if assignment.master is True:
            masters.append(assignment)

    return render_template('admin_students.html', course=course.name, students=students_form, netid=netid, roles = roles, masters = masters, alert = alertMessage)

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
    roles = makeRoles(netid)
    if (roles.count("admin") != 0):
        roles.remove("admin")

    admin = Admin.query.filter_by(netid = netid).first()
    course = admin.courses[0]
    graders = course.graders

    grader_db = []
    for grader in graders:
        num_graded = 0
        assignments = Assignment.query.filter_by(grader=grader)
        for assignment in assignments:
            if assignment.graded == True:
                num_graded += 1
        grader_db.append(GraderClass(grader.netid, num_graded))

    return render_template('admin_graders.html', course=course.name, graders=grader_db, netid=netid, roles = roles)

@app.route('/admin_<netid>/<student>_assignment')
def admin_student_assignment(netid, student):
    admin_netid = netid
    student_netid=student
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

@app.route('/admin_<netid>/<grader>_assignments')
def admin_grader_assignments(netid, grader):
    admin_netid = netid
    gradernetid=grader
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

@app.route('/admin_<netid>/<assignment>_all_assignments')
def admin_all_assignments(netid, assignment):
    admin_netid = netid
    assignment_name=assignment
    roles=makeRoles(admin_netid)
    if (roles.count("admin") != 0):
        roles.remove("admin")
    admin = Admin.query.filter_by(netid=admin_netid).first()
    course = admin.courses[0]
    assignments_name = Assignment.query.filter_by(name=assignment_name).all()
    assignments=[]
    for assignment in assignments_name:
        if assignment.course is course and assignment.master is False:
            assignments.append(assignment)
    return render_template('admin_assignment_assignments.html', course=course.name, roles=roles, assignment_name=assignment_name, netid=admin_netid, assignments=assignments)

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
    roles = makeRoles(netid)
    if (roles.count("admin") != 0):
        roles.remove("admin")

    alertMessage = ""

    if 'error' in session:
        if session['error'] == 'invalidfilename':
            alertString = "You entered an invalid file name. Please try again."
        elif session['error'] == 'rubricmismatch':
            alertString = "There was a mismatch between the number of files you entered and your rubric."
        elif session['error'] == 'invalidrubric':
            alertString = "You entered an invalid rubric value. Please try again."
        elif session['error'] == 'invalidpoints':
            alertString = "You entered an invalid point value. Please try again."
        elif session['error'] == 'noname':
            alertString = "Please enter an assignment name."
        else:
            alertString = "An unknown error occurred."

        alertMessage =  "<div class=\"alert alert-danger alert-dismissable fade in\" style=\"z-index: 1; margin-top: 20px;\"><button type=\"button\" \
        class=\"close\" data-dismiss=\"alert\" aria-hidden=\"true\">&times;</button><strong>Warning! </strong>" + alertString + "</div>"

    session.pop('error', None)

    admin = Admin.query.filter_by(netid = netid).first()
    assignment_db = admin.courses[0].assignments
    course = admin.courses[0]

    assignments = []
    courses = []
    for assignment in assignment_db:
        if assignment.master is True:
            assignments.append(assignment)
        if assignment.courseid not in courses:
            courses.append(assignment.courseid)

    return render_template('admin_admins.html', courses=courses, assignments=assignments, netid= netid, roles = roles, alert = alertMessage, course=course.name)

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect('https://fed.princeton.edu/cas/logout')

# @app.route("/demo")
# def demo():
#     html_escape_table = {
#     "&" : "&amp;",
#     '"': "&quot;",
#     "'": "&apos;",
#     ">": "&gt;",
#     "<": "&lt;",
#     }

#     f = open('Grayscale.java', 'r')
#     code = f.read()
#     code = "".join(html_escape_table.get(c,c) for c in code)
#     code = code.replace("\n","<br>")
#     code = code.replace("    ","&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;")
#     return render_template('demo.html', studentwork = code)
# }

# launch
if __name__ == "__main__":
    app.secret_key = 'qeqg;abuerjabyekeusxjblelauwbajbhvyhenssj'
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
