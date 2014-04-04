import os
from flask import Flask, render_template, send_from_directory
from flask import request, redirect, session
from flask.ext.sqlalchemy import SQLAlchemy
from database import db, Student, Course
import urllib2
from xml.etree import ElementTree

# initialization
app = Flask(__name__)
app.config.update(
    DEBUG = True,
)
db.create_all()
# print Student.query.all()
# print Course.query.all()

def validate():
    response = urllib2.urlopen('https://fed.princeton.edu/cas/validate?ticket='\
 + request.args.get('ticket') + '&service=http://saltytyga.herokuapp.com/valida\
te')
    data = response.read()
    if "yes" in data:
        name = data.split()[1]
        session['name'] = name
        netid = Student.query.filter_by(netid=name).first()
        if netid is None:
            cos_333 = Course.query.filter_by(name= 'cos333').first()
            if cos_333 is None:
                cos_333 = Course('cos333')
                db.session.add(cos_333)
            new_student = Student('dummy', 'name', name, cos_333)
            db.session.add(new_student)
            db.session.commit()
        return name
    else:
        return "NO"

# controllers
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'ico/favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/")
def index():
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
    return render_template('student_submittedcode.html')

@app.route("/grader_NBody")
def graded():
    return render_template('grader_NBody.html')

@app.route("/grader_vayyala")
def gradedwork():
    return render_template('grader_NBody_vayyala.html')

@app.route('/validate')
def validatepage():
    validate()

@app.route('/validategrader')
def validategrader():
    # if 'return' in request.args:    
    #     return_page = request.args.get('return')
    response = urllib2.urlopen('https://fed.princeton.edu/cas/validate?ticket=' + request.args.get('ticket') + '&service=http://saltytyga.herokuapp.com/validategrader')
    data = response.read()
    if "yes" in data:
        name = data.split()[1]
        session['name'] = name
        netid = Student.query.filter_by(netid=name).first()
        if netid is None:
            cos_333 = Course.query.filter_by(name= 'cos333').first()
            if cos_333 is None:
                cos_333 = Course('cos333')
                db.session.add(cos_333)
            new_student = Student('dummy', 'name', name, cos_333)
            db.session.add(new_student)
            db.session.commit()
        return redirect("/grader")
    else:
        return "NO"

@app.route('/validateadmin')
def validateadmin():
    # if 'return' in request.args:    
    #     return_page = request.args.get('return')
    response = urllib2.urlopen('https://fed.princeton.edu/cas/validate?ticket=' + request.args.get('ticket') + '&service=http://saltytyga.herokuapp.com/validateadmin')
    data = response.read()
    if "yes" in data:
        name = data.split()[1]
        session['name'] = name
        netid = Student.query.filter_by(netid=name).first()
        if netid is None:
            cos_333 = Course.query.filter_by(name= 'cos333').first()
            if cos_333 is None:
                cos_333 = Course('cos333')
                db.session.add(cos_333)
            new_student = Student('dummy', 'name', name, cos_333)
            db.session.add(new_student)
            db.session.commit()
        return redirect("/admin")
    else:
        return "NO"

@app.route("/grader")
def grader():
    if 'name' in session:
        return render_template('grader.html', netid=session['name'])
    else:
        return redirect("https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/validategrader")


@app.route("/student")
def student():
    return validate()
    if result != "NO":
        return render_template('student.html', netid=result)
    else:
        return "NO"

@app.route("/admin")
def admin():
    if 'name' in session:
        return render_template('admin.html', netid=session['name'])
    else:
        return redirect("https://fed.princeton.edu/cas/login?service=http://saltytyga.herokuapp.com/validateadmin")


# launch
if __name__ == "__main__":
    app.secret_key = 'qeqg;abuerjabyekeusxjblelauwbajbhvyhenssj'
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
