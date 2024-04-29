from datetime import timedelta, datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from utils.database import SessionLocal
from utils import models, crud, schemas
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm



router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

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

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    cb_employee: crud.Employee = crud.Employee(db=db)
    employee: models.Employee =  cb_employee.authenticate_employee(form_data.username, form_data.password)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    emp_roles: list[str] = employee.roles
    token = cb_employee.create_access_token(employee.email, employee.emp_id, expires_delta=timedelta(minutes=30))

    return {"access_token": token,
            "token_type": "bearer"
            }