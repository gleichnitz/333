import os
from flask import Flask, render_template, send_from_directory
from flask import request, redirect, session
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from database import *
import urllib2
from xml.etree import ElementTree
import cgi
import pickle

# initialization
app = Flask(__name__)
app.config.update(
    DEBUG = True,
)

# print Student.query.all()
# print Course.query.all()
Base = declarative_base()

class Assignment:
    def __init__(self, id, course, name, date, files, grade, grader, student):
        self.id = id
        self.course = course
        self.name = name
        self.date = date
        self.files = files
        self.grade = grade
        self.grader = grader
        self.student = student

class File:
    def __init__(self, name, code, grade):
        self.name = name.split('.')[0]
        if len(name.split('.')) > 1:
            self.ext = name.split('.')[1]
        else:
            self.ext = ""
        self.code = code
        self.grade = grade

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
        netid = Student.query.filter_by(netid=name).first()
        if netid is None:
            cos_333 = Course.query.filter_by(name= 'cos333').first()
            if cos_333 is None:
                cos_333 = Course('cos333')
                db.session.add(cos_333)
                db.session.commit()
            new_student = Student('dummy', 'name', name, cos_333)
            db.session.add(new_student)
            db.session.commit()
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
    return render_template('index3.html')

@app.route("/index")
def index2():
    return render_template('index.html')

@app.route("/index3")
def index3():
    return render_template('index3.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/team")
def team():
    return render_template('team.html')

@app.route("/viewer")
def submitted():
    try:
        ticket = request.args.get('ticket')
    except:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "viewer" + "?assignment=" + request.args.get('assignment') + "&type=" + request.args.get('type'))

    if ticket is None:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "viewer" + "?assignment=" + request.args.get('assignment') + "&type=" + request.args.get('type'))
    if 'ticket_viewer' in session and ticket == session['ticket_viewer']:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "viewer" + "?assignment=" + request.args.get('assignment') + "&type=" + request.args.get('type'))

    session['ticket_viewer'] = ticket
    netid = isLoggedIn(ticket, "viewer?assignment=" + request.args.get('assignment'))
    if netid is "0":
        return redirect('/')

    if id is None:
        return redirect('https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/' + "student")

    student = Student.query.filter_by(netid = netid).first()
    assignments = student.assignments.all()       

    for item in assignments:
        assignment_active = 0
        if int(request.args.get('assignment')) == item.id:
            assignment_active = item
            break

    if assignment_active == 0:
        return redirect('/student')

    title = assignment_active.name

    files = []

    for item in assignment_active.files:
        files.append(File(item['name'], item['content'], "10/10"))

    ##################################
    # need to pass: item containing assignment files to be loaded
    #               fields:
    #               - name (e.g. "percolaton.java")
    #               - grade ("10/10")
    #               - code (in a big string)
    ##################################

    # render_template('viewer.html', netid = session['username'], assignment=)
    return render_template('viewer.html', netid = netid, assignment = files, title=title)

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

    # if isGrader(session['username']) is False:
    #     return redirect('/')

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
    course = grader.course
    assignments = course.assignments.all()

    assignments_form = []
    for item in assignments:
        if item.grader is None:
            assignments_form.append(Assignment(item.id, item.course.name, item.name, item.date.split()[0], item.files, "40/40", "None", item.student.netid))
        elif item.grader.netid == netid:
            assignments_form.append(Assignment(item.id, item.course.name, item.name, item.date.split()[0], item.files, "40/40", item.grader.netid, item.student.netid))
        
    classes = []
    for item in assignments_form: 
        if item.course not in classes:
            classes.append(item.course)

    roles = makeRoles(netid)
    if (roles.count("grader") != 0):
        roles.remove("grader")

    return render_template('grader.html', netid=netid, roles = roles, classes = classes, assignments=assignments_form)

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

    # if isStudent(session['username']) is False:
    #     return redirect('/')

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
        assignments_form.append(Assignment(item.id, item.course.name, item.name, item.date.split()[0], item.files, "40/40", "", item.student.netid))

    classes = []
    for item in assignments_form: 
        if item.course not in classes:
            classes.append(item.course)

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
    if netid is "0":
        return redirect('/')

    # if isAdmin(session['username']) is False:
    #     return redirect('/')

    roles = makeRoles(netid)
    if (roles.count("admin") != 0):
        roles.remove("admin")

    return render_template('admin.html', netid=session['username'], roles = roles)

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect('/')

# launch
if __name__ == "__main__":
    app.secret_key = 'qeqg;abuerjabyekeusxjblelauwbajbhvyhenssj'
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
