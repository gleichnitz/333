import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import pickle
from database import *


def AddtoListAssignment(files, file_name):
  file_ = open(file_name, 'r')
  file_content = file_.read()
  ass_file = {'name': file_name, 'content': file_content, 'annotations': []}
  files.append(ass_file)
  return files


files = []
print "here1"
files = AddtoListAssignment(files, 'nbody.java')
assignments = Assignment.query.all()

print "here2"
for item in assignments:
  print "here3"
  item.files = files
  db.session.commit()

# files = []
# files = AddtoListAssignment(files, 'HelloWorld.java')
# files = AddtoListAssignment(files, 'HiFour.java')
# files = AddtoListAssignment(files, 'SumThree.java')
# name = 'Assignment1'
# addAssignment('cos333', 'gtl', name, files)

# ass_file = {}
# name = 'Nbody'
# files = []

# # file_name = 'nbody.java'
# nbody_= open(file_name, 'r')
# file_content = nbody_.read()
# ass_file[name] = file_name
# ass_file[content] = file_content
# files.append(ass_file)
# addAssignment('cos333', 'rfreling', name, files)


# name = 'Assignment1'

# file_name = 'HelloWorld.java'
# files = []
# hello_= open(file_name, 'r')
# file_content = hello_.read()
# ass_file[name] = file_name
# ass_file[content] = file_content
# files.append(ass_file)

# hifour = open('HiFour.java', 'r')
# file_content = hifour.read()
# ass_file[name] = "Hi Four"
# ass_file[content] = file_content
# files.append(ass_file)

# sumthree = open('SumThree.java', 'r')
# file_content = sumthree.read()
# files.append(file_content)
# addAssignment('cos333', 'rfreling', name, files)