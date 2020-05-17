
# Cheik Kone and Perfect Torkornoo Gradebook Application


from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_migrate import Migrate
from flask_login import login_user, LoginManager, UserMixin, logout_user, login_required, current_user
from werkzeug.security import check_password_hash


app = Flask(__name__)

app.config["DEBUG"] = True
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="PerfectCheik",
    password="IS668_2020",
    hostname="PerfectCheik.mysql.pythonanywhere-services.com",
    databasename="PerfectCheik$gradebook",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

migrate = Migrate(app, db)
app.secret_key = "d84yt82y3nc2ut3utnytu2"
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):


    __tablename__ = "instructors"

    instructor_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))
    courses = db.relationship("Course", backref="instructors")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def get_id(self):
        return self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()

class Course(db.Model):

    __tablename__ = "courses"

    course_id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(128))
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructors.instructor_id'), nullable=True)
    instructor = db.relationship('User', foreign_keys=instructor_id)

class Assignment(db.Model):

    __tablename__ = "assignments"

    assignment_id = db.Column(db.Integer, primary_key=True)
    assignment_desc = db.Column(db.String(128))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'), nullable=True)
    course = db.relationship('Course', foreign_keys=course_id)


class Student(db.Model):

    __tablename__ = "students"

    student_id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(128))
    lastname = db.Column(db.String(128))
    student_major = db.Column(db.String(128))
    student_email = db.Column(db.String(128))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'), nullable=True)
    course = db.relationship('Course', foreign_keys=course_id)
    #student email address missing from table

class Gradebook(db.Model):

    __tablename__ = "gradebooks"

    gradebook_id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.course_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.assignment_id'), nullable=False)
    grade = db.Column(db.Integer)
    course = db.relationship('Course', foreign_keys=course_id)
    student = db.relationship('Student', foreign_keys=student_id)
    assignment = db.relationship('Assignment', foreign_keys=assignment_id)

#default course id for new students
course_default = 101

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
       grades = db.session.query(Gradebook, Course, Student, Assignment).order_by(Student.lastname, Student.firstname).join(Course, Gradebook.course_id == Course.course_id).join(Student, Gradebook.student_id == Student.student_id).join(Assignment, Gradebook.assignment_id == Assignment.assignment_id)
    average_grade = 0
    count = 0
    all_grades = Gradebook.query.all()
    for student_grade in all_grades:
           average_grade = student_grade.grade+average_grade
           count = count+1
    average_grade = average_grade/count
    return render_template("gradebook_main_page.html", grades=grades, average_grade=average_grade )


#route displays assignments with capability of adding and deleting assignments
@app.route("/all_assignments", methods=["GET", "POST"])
def assignments():
    if request.method == "GET":
       return render_template("gradebook_assignments_page.html", assignments=Assignment.query.all())
    if request.method == "POST":
        new_assignment=Assignment(assignment_desc=request.form["assignment_name"])
        db.session.add(new_assignment)
        db.session.commit()
    return render_template("gradebook_assignments_page.html", assignments=Assignment.query.all())


#Deletes assignment from database
@app.route("/<int:id>/assignment_delete", methods=["POST"])
def deleteAssignment(id):
    deleted_assignment = Assignment.query.get_or_404(id)
    db.session.delete(deleted_assignment)
    db.session.commit()
    return redirect(url_for('all_assignments'))

#Webpage display student roster in aphlabetical order, redirects user to add and delete students
@app.route("/student_roster", methods=["GET", "POST"])
def roster():
    if request.method == "GET":
        return render_template("gradebook_student_roster_page.html", students=Student.query.order_by(Student.lastname, Student.firstname).all())
    if request.method == "POST":
        new_student=Student(firstname=request.form["first_name"],lastname=request.form["last_name"],student_major=request.form["major"], student_email=request.form["email"],course_id=course_default)
        db.session.add(new_student)
        db.session.commit()
    return render_template ("gradebook_student_roster_page.html", students=Student.query.order_by(Student.lastname, Student.firstname).all())

#Deletes student from database
@app.route("/<int:id>/student_delete", methods=["POST"])
def deleteStudent(id):
    deleted_student = Student.query.get_or_404(id)
    db.session.delete(deleted_student)
    db.session.commit()
    return redirect(url_for('roster'))

#Retrieve and displays single student information from database
@app.route("/<int:id>/student_info", methods=["POST"])
def viewStudent(id):
    student_info = db.session.query(Gradebook, Course, Student, Assignment).join(Course, Gradebook.course_id == Course.course_id).join(Student, Gradebook.student_id == Student.student_id).join(Assignment, Gradebook.assignment_id == Assignment.assignment_id).filter(Student.student_id == id)
    new_average = db.session.query(func.avg(Gradebook.grade)).join(Course, Gradebook.course_id == Course.course_id).join(Student, Gradebook.student_id == Student.student_id).filter(Course.course_id == course_default).filter(Student.student_id == id).scalar()
    return render_template("gradebook_student_information_page.html", grades=student_info, average_grade = new_average)

#updates students grades
@app.route("/update_grade/", methods=["POST"])
def update_grade():
    if request.method == "POST":
        # query.get() method gets a Row by the primary_key
        record = Gradebook.query.get(request.form.get('id'))
        # change the values you want to update
        record.grade = request.form.get('change_grade')
        # commit changes
        db.session.commit()
    # redirect back to your main view
    return redirect(url_for('index'))

#login page
@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("gradebook_login_page.html", error=False)

    user = load_user(request.form["username"])
    if user is None:
        return render_template("gradebook_login_page.html", error=True)

    if not user.check_password(request.form["password"]):
        return render_template("gradebook_login_page.html", error=True)

    login_user(user)
    return redirect(url_for('index'))
#logout page
@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))





