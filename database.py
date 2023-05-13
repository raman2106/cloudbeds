from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import URL
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://n19obzau069o5r7vh8pk:pscale_pw_B4pQrciKqXlIi5VghLXMNSU8GRSVr6IZidFOEYXHwGG@aws.connect.psdb.cloud/cloudbeds'
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {'ssl': {'ca': '/etc/ssl/certs/ca-certificates.crt'}}
}
db = SQLAlchemy(app)

with app.app_context():
    empls = db.session.execute(text("SELECT * from employees"))
    print("Connection successful!")
    for emp in empls:
        print(emp)