import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import pickle
from database import *

# name = 'Nbody'
# files = []
# nbody_= open('nbody.java', 'r')
# file_content = nbody_.read()
# files.append(file_content)
# addAssignment('cos333', 'vayyala', name, files)

name = 'Assignment1'
files = []
hello_= open('HelloWorld.java', 'r')
file_content = nbody_.read()
files.append(file_content)

hifour = open('HiFour.java', 'r')
file_content = hifour.read()
files.append(file_content)

sumthree = open('SumThree.java', 'r')
file_content = sumthree.read()
files.append(file_content)

addAssignment('cos333', 'vayyala', name, files)