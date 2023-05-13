from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

#Create a Flask instance
app = Flask(__name__)
app.config['SECRET_KEY'] = "Super secret key. Do not upload to public github repo."

#Create a Form class
class LoginForm(FlaskForm):
  username = StringField("Username", validators=[DataRequired()])
  password = StringField("Password", validators=[DataRequired()])
  submit = SubmitField("Submit")

@app.route("/")
# def login():
#   return render_template("login.html")
def home():
  #Log the client's IP'
  client_ip = request.remote_addr
  print(f'Client IP:{client_ip}')#Improvement: Should we log it to a log file?
  return render_template("home.html")

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
