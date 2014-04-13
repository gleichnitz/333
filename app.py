import os
from flask import Flask, render_template, send_from_directory
from flask import request, redirect, session
from flask.ext.sqlalchemy import SQLAlchemy
from database import db, Student, Course, Grader, Admin
import urllib2
from xml.etree import ElementTree
import cgi

# initialization
app = Flask(__name__)
app.config.update(
    DEBUG = True,
)
db.create_all()
# print Student.query.all()
# print Course.query.all()

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

def isLoggedIn(page):
    if 'ticket' in session:
        response = urllib2.urlopen('https://fed.princeton.edu/cas/validate?ticket=' + session['ticket'] + '&service=http://saltytyga.herokuapp.com/' + page)
    else:
        return redirect('/')
    data = response.read()
    result = validate(data)

    if result is "NO":
        return redirect('/')
    else:
        return result

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

@app.route('/login')
def login():
    session['ticket'] = request.args.get('ticket')
    return redirect('/' + request.args.get('dest'))

# controllers
@app.route('/datatest')
def datatest():
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
    netid = isLoggedIn('viewer')
    html_escape_table = {
        "&" : "&amp;",
        '"': "&quot;",
        "'": "&apos;",
        ">": "&gt;",
        "<": "&lt;",
    }
    f = open('BaseballElimination.java', 'r')
    code = f.read()
    return render_template('viewer.html', studentwork = code, netid = netid)

@app.route("/grader")
def grader():
    netid = isLoggedIn("grader")             
    return render_template('grader.html', netid=netid)

@app.route("/student")
def student():
    netid = isLoggedIn("student")
    return render_template('student.html', netid=netid)

@app.route("/admin")
def admin():
    netid = isLoggedIn("admin")
    render_template('admin.html', netid=netid)

# launch
if __name__ == "__main__":
    app.secret_key = 'qeqg;abuerjabyekeusxjblelauwbajbhvyhenssj'
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
