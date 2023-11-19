
from fastapi import FastAPI, Depends, HTTPException
from typing import List
from utils import models, schemas, crud
from utils.database import SessionLocal, engine
from sqlalchemy.orm.session import Session

#Used in Tes endpoints
from pydantic import EmailStr
import uvicorn

#from datetime import date

models.Base.metadata.create_all(bind=engine)

api = FastAPI(title="CloudBeds API", version="1.0.0" )


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#===========================
# Test endpoints
#===========================
# FIXME: Modify this endpoint so that caller can search for employee by employee ID or email
@api.get("/get_employee",
         name = "Get Employee by Email",
         response_model= schemas.ReadEmployee,
         tags=["admin"])
async def get_emp_by_email(email: EmailStr, db: Session = Depends(get_db)):
    employee: schemas.ReadEmployee|None = crud.get_employee_by_email(email=email, db=db)
    if employee:
        return employee
    else:
         raise HTTPException(status_code=404, detail="Email isn't registered.")
    
@api.get("/get_employee/{emp_id}",
         name = "Get employee by ID",
         response_model=schemas.ReadFullEmployeeData,
         tags=["admin"])
async def get_emp_by_id(emp_id: int, db: Session = Depends(get_db)):
    employee: schemas.ReadFullEmployeeData|None = crud.get_employee_by_id(emp_id, db=db)
    if employee:
        return employee
    else:
        raise HTTPException(status_code=404, detail="Invalid employee ID.")


#===========================
# Login and logoff endpoints
#===========================


#==========================
# Admin endpoints
#==========================
@api.post("/add_employee/", 
          name="Add Employee",
          response_model=schemas.CreateEmployeeResult,
          tags=["admin"])
#FIXME: Implemnet multiple addresses support (correspondence and permanent)
#FIXME: Implement callback URL
async def add_employee(payload: schemas.CreateEmployee, db: Session = Depends(get_db)):
    employee: schemas.ReadEmployee|None = crud.get_employee_by_email(email=payload.emp_details.email,db=db)
    if employee:
        raise HTTPException(status_code=400, detail="Email already registered.")
    result: schemas.CreateEmployeeResult = crud.create_employee(db=db, payload=payload)
    return result


@api.get("/list_employees/",
         name = "List Employees",
         response_model=List[schemas.ReadFullEmployeeData],
         tags=["admin"])

async def list_employees(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    result:List[schemas.ReadFullEmployeeData] = crud.list_employees(db=db, skip=skip, limit=limit)
    return result


@api.post("/update_employee",
          name="Update employee",
          response_model=schemas.UpdateEmployeeResponse,
          tags=["admin"])
async def update_employee(payload: schemas.CreateEmployee, db: Session = Depends(get_db)):
    employee: schemas.ReadEmployee|None = crud.get_employee_by_email(email=payload.emp_details.email,db=db)
    if not employee:
        raise HTTPException(status_code=400, detail="Invalid employee email.")
    result: schemas.UpdateEmployeeResponse = crud.update_employee_details(db=db, payload=payload)
    return result


if __name__ == "__main__":
    # USed to run the code in debug mode.
    uvicorn.run(api, host="0.0.0.0", port=8000)