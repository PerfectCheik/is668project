
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


    __tablename__ = "intructors"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128))
    password_hash = db.Column(db.String(128))


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def get_id(self):
        return self.username


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(username=user_id).first()

#class Student(db.Model):

#    __tablename__ = "students"

#    id = db.Column(db.Integer, primary_key=True)
#    firstname = db.Column(db.String(128))
#    lastname = db.Column(db.String(128))
#    posted = db.Column(db.DateTime, default=datetime.now)
#    commenter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
#    commenter = db.relationship('User', foreign_keys=commenter_id)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        #return render_template("main_page.html", comments=Comment.query.all())
        return render_template("gradebook_main_page.html")
    if not current_user.is_authenticated:
        return redirect(url_for('index'))
    #comment = Comment(content=request.form["contents"], commenter=current_user)
    #db.session.add(comment)
    #db.session.commit()

    return redirect(url_for('index'))

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