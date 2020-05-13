
# Cheik Kone and Perfect Torkornoo Gradebook Application


from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
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


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        #return render_template("gradebook_main_page.html", grades=Gradebook.query.join(Assignment, Assignment.assignment_id==Gradebook.assignment_id))
        return render_template("gradebook_main_page.html", grades=db.session.query(Gradebook, Course, Student, Assignment).join(Course, Gradebook.course_id == Course.course_id).join(Student, Gradebook.student_id == Student.student_id).join(Assignment, Gradebook.assignment_id == Assignment.assignment_id))
  # if request.method == "POST":
        #new_student=Student(firstname=request.form["first_name"],lastname=request.form["last_name"],student_major=request.form["major"], student_email=request.form["email"],course_id=course_default)
       # db.session.add(new_student)
        #db.session.commit()
    #return render_template ("gradebook_student_roster_page.html", students=Student.query.all())


   # if request.method == "GET":
        #return render_template("main_page.html", comments=Comment.query.all())
      #  return render_template("gradebook_main_page.html")
   # if not current_user.is_authenticated:
    #    return redirect(url_for('index'))
    #comment = Comment(content=request.form["contents"], commenter=current_user)
    #db.session.add(comment)
    #db.session.commit()



#default course id for new students
course_default = 101

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

#update feature
@app.route("/update/", methods=["POST"])
def update_grade():
    if request.method == "POST":
        # query.get() method gets a Row by the primary_key
        record = Student.query.get(request.form.get('id'))
        # change the values you want to update
        record.student_major = request.form.get('change_grade')
        # commit changes

        db.session.commit()
    # redirect back to your main view
    return redirect(url_for('roster'))

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

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

#for testing template format and code, route will be deleted
@app.route("/gradebook/")
def gradebook():
    return render_template("gradebook_main_page.html")

#for Adding assignment records, route will be updated
@app.route("/assignments/")
def addAssigment():
#    assignment1 = Assignment(assignment_desc='Homework 1',course_id=course_default)
#    db.session.add(assignment1)
#    assignment2 = Assignment(assignment_desc='Homework 2',course_id=course_default)
#    db.session.add(assignment2)
#    assignment3 = Assignment(assignment_desc='Term Paper',course_id=course_default)
#    db.session.add(assignment3)
#    assignment4 = Assignment(assignment_desc='Final Exam',course_id=course_default)
#    db.session.add(assignment4)
#    db.session.commit()
    return 'Assignments 1-4 Added'

@app.route("/add-gradebooks/")
def addGrade():
#    grade1 = Gradebook(course_id=course_default, student_id = 1 , assignment_id = 1 , grade = 76 )
#    db.session.add(grade1)
#    grade2 = Gradebook(course_id=course_default, student_id = 2 , assignment_id = 1 , grade = 88 )
#    db.session.add(grade2)
#    grade3 = Gradebook(course_id=course_default, student_id = 3 , assignment_id = 1 , grade = 79 )
#    db.session.add(grade3)
#    grade4 = Gradebook(course_id=course_default, student_id = 4 , assignment_id = 1 , grade = 100 )
#    db.session.add(grade4)
#    grade5 = Gradebook(course_id=course_default, student_id = 3 , assignment_id = 2 , grade = 99 )
#    db.session.add(grade5)
#    grade6 = Gradebook(course_id=course_default, student_id = 4 , assignment_id = 2 , grade = 75 )
#    db.session.add(grade6)
#    grade7 = Gradebook(course_id=course_default, student_id = 2 , assignment_id = 2 , grade = 85 )
#    db.session.add(grade7)
#    grade8 = Gradebook(course_id=course_default, student_id = 1 , assignment_id = 2 , grade = 100 )
#    db.session.add(grade8)
#    grade9 = Gradebook(course_id=course_default, student_id = 2 , assignment_id = 3 , grade = 87 )
#    db.session.add(grade9)
#    grade10 = Gradebook(course_id=course_default, student_id = 4 , assignment_id = 3 , grade = 95 )
#    db.session.add(grade10)
#    grade11 = Gradebook(course_id=course_default, student_id = 3 , assignment_id = 3 , grade = 70 )
#    db.session.add(grade11)
#    grade12 = Gradebook(course_id=course_default, student_id = 1 , assignment_id = 3 , grade = 80 )
#    db.session.add(grade12)
#    grade13 = Gradebook(course_id=course_default, student_id = 1 , assignment_id = 4 , grade = 97 )
#    db.session.add(grade13)
#    grade14 = Gradebook(course_id=course_default, student_id = 2 , assignment_id = 4 , grade = 100 )
#    db.session.add(grade14)
#    grade15 = Gradebook(course_id=course_default, student_id = 3 , assignment_id = 4 , grade = 75 )
#    db.session.add(grade15)
#    grade16 = Gradebook(course_id=course_default, student_id = 4 , assignment_id = 4 , grade = 78 )
#    db.session.add(grade16)
#    db.session.commit()
    return 'Grades 1-16 Added'