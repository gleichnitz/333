import os
from flask import Flask, render_template, send_from_directory
from flask import render_template
import CASClient
import urllib2
import xml.etree.ElementTree as ET

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

@app.route("/grader.html")
def grader():
    return render_template('grader.html')

@app.route("/validate.html?ticket=<ticket>")
def validate():
    # req = urllib2.Request('https://fed.princeton.edu/cas/serviceValidate?ticket=' + ticket + '?service=http://saltytyga.herokuapp.com/validate.html')
    # response = urllib2.urlopen(req)
    # data = response.read()
    # tree = ET.parse(data)
    # if tree.attrib.contains_key('cas:authenticationSuccess'):  
    return 'Success'
    # else:
      #  return 'Failure'

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
