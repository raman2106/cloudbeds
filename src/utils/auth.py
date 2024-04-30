from datetime import timedelta, datetime
from typing import Annotated
from pydantic import SecretStr, EmailStr
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status
from utils.database import SessionLocal
from utils import models, crud, schemas
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

# Load environmental variables from .env
load_dotenv()
SECRET_KEY: SecretStr = os.getenv("SECRET_KEY")
ALGORITHM: str = os.getenv("ALGORITHM")

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


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    cb_employee: crud.Employee = crud.Employee(db=db)
    employee: models.Employee =  cb_employee.authenticate_employee(form_data.username, form_data.password,)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    emp_roles: list[str] | None = [assigned_role.role.name for assigned_role in employee.roles]
    token = cb_employee.create_access_token(employee.email, employee.emp_id, expires_delta=timedelta(minutes=30), roles=emp_roles)
    employee_token: schemas.Token = schemas.Token(access_token=token, token_type="bearer")
    return employee_token

async def get_current_employee(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: EmailStr = payload.get("sub")
        emp_id: int = payload.get("id")
        roles: list[str] = payload.get("role")
        
        if email is None or emp_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldn't validate user.")
        
        return {"email": email, "emp_id": emp_id, "roles": roles}

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldn't validate user.")
