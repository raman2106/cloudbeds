from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired

#Create a Flask instance
app = Flask(__name__)
app.config['SECRET_KEY'] = "Super secret key. Do not upload to public github repo." # Used to create the CSRF token

#Create a Form class
class LoginForm(FlaskForm):
  username = EmailField("Username", validators=[DataRequired()])
  password = PasswordField("Password", validators=[DataRequired()])
  login = SubmitField("login")


@app.route("/", methods=["GET","POST"])
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


@app.route("/dashboard")
def dashboard():
  return render_template("dashboard.html")

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
