import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import pickle
from database import *


def AddtoListAssignment(files, file_name):
  file_ = open(file_name, 'r')
  file_content = file_.read()
  ass_file = {'name': file_name, 'content': file_content}
  files.append(ass_file)
  return files


files = []
files = AddtoListAssignment(files, 'nbody.java')
name = "Nbody"
addAssignment('cos333', 'rfreling', name, files)

files = []
files = AddtoListAssignment(files, 'HelloWorld.java')
files = AddtoListAssignment(files, 'HiFour.java')
files = AddtoListAssignment(files, 'SumThree.java')
name = 'Assignment1'
addAssignment('cos333', 'rfreling', name, files)

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