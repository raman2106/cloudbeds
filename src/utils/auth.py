from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from utils.database import SessionLocal
from utils import models, crud, schemas
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

SECRET_KEY = "JWT_SECRET_KEY"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

# class CreateEmployeeRequest(BaseModel):
#     username: str
#     password: str

class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
 
db_dependency = Annotated[Session, Depends(get_db)]


@router.post("/", 
             name="Create Employee",
             response_model= schemas.EmployeePasswordOut,
              description='''Creates an employee record in the database.
          If the provided email exists in the database, returns HTTP 404.''',
             status_code=status.HTTP_201_CREATED
             )
async def create_employee(db: db_dependency,
                          payload: schemas.EmployeeIn):
    employee: crud.Employee = crud.Employee(db=db)
    # Check if employee already exists
    result: list[schemas.EmployeeOut]|None = employee.list_employees(query_value=payload.emp_details.email)
    if result:
        raise HTTPException(status_code=400, detail="Email already registered.")
    result: list[schemas.EmployeeOut]|None = employee.list_employees(query_value=payload.emp_details.phone)
    if result:
        raise HTTPException(status_code=400, detail="Phone number already registered.")
    
    # Create employee
    result: schemas.EmployeePasswordOut = employee.create_employee(payload)
    return result
