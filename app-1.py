from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import URL
from flask_wtf import FlaskForm

# Instantiate the Flask app
app = Flask(__name__)

# SQL-Alchemy app configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://n19obzau069o5r7vh8pk:pscale_pw_B4pQrciKqXlIi5VghLXMNSU8GRSVr6IZidFOEYXHwGG@aws.connect.psdb.cloud/cloudbeds'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {'ssl': {'ca': '/etc/ssl/certs/ca-certificates.crt'}}
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_QUOTED_IDENTIFIERS'] = True  # Preserve casing
app.secret_key = 'your_secret_key'  # used to encrypt session data

# Instantiate the MySQL DB
db = SQLAlchemy(app)

# with app.app_context():
#     empls = db.session.execute(text("SELECT * from employees"))
#     print("Connection successful!")
#     for emp in empls:
#         print(emp)

# Employees model represents the Employees table
class Employees(db.Model):
    __tablename__ = "Employees"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(30), nullable=False, unique=True)
    emp_pass = db.Column(db.String(255), nullable=False, unique=True)

    def __repr__(self):
        return f"User('{self.employee_login_id}')"

class Rooms(db.Model):
    __tablename__ = "Rooms"
    room_number = db.Column(db.Integer, primary_key = True, autoincrement=True)
    status = db.Column(db.String(10), nullable = False, default = "Available")

    def __repr__(self):
        return f"User('{self.room_number}')"

class Bookings(db.Model):
    __tablename__ = "Bookings"
    booking_id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    guest_id = db.Column(db.Integer, nullable=False,  index=True)
    room_number = db.Column(db.Integer, nullable=True,  index=True)
    booking_date = db.Column(db.DateTime, nullable=True)
    booking_status = db.Column(db.String, nullable=True)
    checkin_date = db.Column(db.DateTime, nullable=True)
    checkout_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"User('{self.booking_id}')"


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        employee = Employees.query.filter_by(email=username).first()

        if employee and password == employee.emp_pass:
            session['user_id'] = employee.id
            return redirect('/dashboard')
        else:
            return render_template('home.html', error='Invalid username or password')

    return render_template('home.html')

# If the employee is authenticated, display the dashboard page
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        employee = Employees.query.get(session['user_id'])

        # Retrive information about all the rooms from DB and pass it to 
        # the template through the rooms variable.
        rooms = Rooms.query.all()

        # Retrive information about all the bookings from DB and pass it to 
        # the template through the bookings variable.
        bookings = Bookings.query.all()

        return render_template('dashboard.html', user=employee, rooms=rooms, bookings=bookings)
    else:
        return redirect('/')

# Logout the employee
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/')


# HTML Page isn't developed yet!
# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         existing_user = User.query.filter_by(username=username).first()
#         if existing_user:
#             return render_template('register.html', error='Username already exists')

#         new_user = User(username=username, password=password)
#         db.session.add(new_user)
#         db.session.commit()
#         return redirect('/')
     
#     return render_template('register.html')

if __name__ == '__main__':
    app.run()