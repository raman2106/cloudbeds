from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Load environmental variables from .env
load_dotenv()

#SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(os.getenv("DATABASE_URL"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Authenticate user from the given email and password
# Create a connection with the DB and try ro retrieve a user 