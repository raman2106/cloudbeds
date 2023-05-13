from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

#Create a Flask instance
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://n19obzau069o5r7vh8pk:pscale_pw_B4pQrciKqXlIi5VghLXMNSU8GRSVr6IZidFOEYXHwGG@aws.connect.psdb.cloud/cloudbeds?charset=utf8mb4'
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = "Super secret key. Do not upload to public github repo." # Used to create the CSRF token

#Create a Form class
class LoginForm(FlaskForm):
  username = EmailField("Username", validators=[DataRequired()])
  password = PasswordField("Password", validators=[DataRequired()])
  login = SubmitField("login")

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
with app.app_context():
  employees = Employee.query.all()
  for employee in employees:
    print(employee)

@app.route("/", methods=["GET","POST"])
# def login():
#   return render_template("login.html")
def home():
  username = None
  password = None
  login_form = LoginForm()
  #Validate form
  if login_form.validate_on_submit():
    username = login_form.username.data
    print(username)
    login_form.username.data = ""
    password = login_form.password.data
    login_form.password.data = ""
    
  return render_template("login.html",
                        username = username,
                        password = password,
                        login_form = login_form)

#Invalid URL
@app.errorhandler(404)
def page_not_found(e):
  return render_template("404.html"), 400

#Internal server error
@app.errorhandler(500)
def page_not_found(e):
  return render_template("500.html"), 500

if __name__ == "__main__":
  app.run(host="0.0.0.0", debug=True)
