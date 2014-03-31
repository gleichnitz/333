import os
from flask import Flask, render_template, send_from_directory
from flask import render_template
from flask import request
import urllib2
from xml.etree import ElementTree

# initialization
app = Flask(__name__)
app.config.update(
    DEBUG = True,
)

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

@app.route("/index.html")
def index2():
    return render_template('index.html')

@app.route("/about.html")
def about():
    return render_template('about.html')

@app.route("/team.html")
def team():
    return render_template('team.html')

@app.route('/validate.html')
def validate():
    response = urllib2.urlopen('https://fed.princeton.edu/cas/serviceValidate?ticket=' + request.args.get('ticket') + '&service=http://saltytyga.herokuapp.com/validate.html')
    data = response.read()
    rdata = []
    rdata.append(data)
    tree = ElementTree.fromstring(''.join(rdata))
    return request.args.get('ticket')

@app.route("/grader.html")
def grader():
    return render_template('grader.html')

@app.route("/student.html")
def student():
    return render_template('student.html')

@app.route("/admin.html")
def admin():
    return render_template('admin.html')

# launch
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
