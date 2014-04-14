import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import pickle
from database import *

name = 'Nbody'
files = []
files[0] = open('Nbody.java', 'w')
addAssignment('cos333', 'vayyala', name, files)