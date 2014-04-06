import os
from flask import Flask, render_template, send_from_directory
from flask import request, redirect, session
from flask.ext.sqlalchemy import SQLAlchemy
from database import db, Student, Course, Grader, Admin
import urllib2
from xml.etree import ElementTree

# initialization
app = Flask(__name__)
app.config.update(
    DEBUG = True,
)
#db.create_all()
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

# controllers
@app.route('/datatest')
def datatest():
    _admins = Admin.query.all()
    _students = Student.query.all()
    _graders = Grader.query.all()

    # student_string = ""
    # for i in _students:
    #     student_string = student_string + str(i) + ","

    # string = "Students: {0} \n Graders: {1} \n Admins: {2}".format(student_string, _graders, _admins)
    return str(_students)

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
    return render_template('index.html')

@app.route("/index")
def index2():
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/team")
def team():
    return render_template('team.html')

@app.route("/submittedcode")
def submitted():
    f = open('BaseballElimination.java', 'r')
    code = f.read()
    "<br />".join(code.split("\n"))
    return render_template('student_submittedcode.html', studentwork = code)

@app.route("/grader_NBody")
def graded():
    return render_template('grader_NBody.html')

@app.route("/grader_vayyala")
def gradedwork():
    return render_template('grader_NBody_vayyala.html')

@app.route("/grader")
def grader():
    response = urllib2.urlopen('https://fed.princeton.edu/cas/validate?ticket=' + request.args.get('ticket') + '&service=http://saltytyga.herokuapp.com/grader')
    data = response.read()
    result = validate(data)

    # check if netid corresponds to grader

    if result != "NO":
        return render_template('grader.html', netid=result)
    else:
        return redirect('/')

@app.route("/student")
def student():
    response = urllib2.urlopen('https://fed.princeton.edu/cas/validate?ticket=' + request.args.get('ticket') + '&service=http://saltytyga.herokuapp.com/student')
    data = response.read()
    result = validate(data)

    # check if netid corresponds to student

    if result != "NO":
        return render_template('student.html', netid=result)
    else:
        return redirect('/')

@app.route("/admin")
def admin():
    response = urllib2.urlopen('https://fed.princeton.edu/cas/validate?ticket=' + request.args.get('ticket') + '&service=http://saltytyga.herokuapp.com/admin')
    data = response.read()
    result = validate(data)

    #check if netid corresponds to admin

    if result != "NO":
        return render_template('admin.html', netid=result)
    else:
        return redirect('/')


# launch
if __name__ == "__main__":
    app.secret_key = 'qeqg;abuerjabyekeusxjblelauwbajbhvyhenssj'
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
