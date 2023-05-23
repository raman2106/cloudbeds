from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import URL
from faker import Faker
import random
from datetime import datetime, timedelta

# Instantiate the Flask app
app = Flask(__name__)
# Create an instance of the Faker class
fake = Faker()



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


# Generate dummy data for bookings
bookings = []

for _ in range(10):
    booking = {
        'guest_id': random.randint(1, 100),
        'room_number': random.randint(101, 200),
        'booking_date': fake.date_time_between(start_date='-1y', end_date='now'),
        'booking_status': random.choice(['confirmed', 'pending', 'cancelled']),
        'checkin_date': fake.date_time_between(start_date='now', end_date='+1y'),
        'checkout_date': fake.date_time_between(start_date='+2d', end_date='+7d'),
        'total_price': random.uniform(50, 500)
    }
    bookings.append(booking)

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

B

# # Print the generated data
# for booking in bookings:
#     print(booking)