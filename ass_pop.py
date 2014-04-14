import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import pickle
from database import *

name = 'Nbody'
files = []
nbody_= open('nbody.java', 'r')
file_content = nbody_.read()
files.append(file_content)
addAssignment('cos333', 'vayyala', name, files)
