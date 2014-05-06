from database import *

admin = Admin.query.filter_by(netid = "jaevans").first()
students_db = admin.courses[0].students

students_form = []

for student in students_db:
    students_form.append(StudentClass("no name", student.netid))

assignment_db = admin.courses[0].assignments

masters = []

# Load assignments for reference when uploading code.
for assignment in assignment_db:
    if assignment.master is True:
        masters.append(assignment)

print masters
print students_form
