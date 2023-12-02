
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
# Login and logoff endpoints
#===========================


#==========================
# Admin endpoints
#==========================
@api.get("/get_emp/",
         name="Get Employee",
         response_model=schemas.EmployeeOut,
         tags=["admin"],
         description= '''Returns the details of an employee for the provided employee id or email. 
         If employee isn't found in the database, it returns HTTP 404.'''
         )
async def get_employee(id: int|EmailStr,  db: Session = Depends(get_db)):
    employee: schemas.Employee|None = crud.get_employee(id, db)
    if employee:
        return employee
    else:
        raise HTTPException(status_code=404, detail="Email isn't registered.")

@api.get("/get_emp/list/",
         name="List Employees",
         response_model=List[schemas.EmployeeOut],
         tags=["admin"],
         description= '''Returns the list of all employees from the database. If the database is empty, it returns HTTP 404.'''
         )
async def list_employee(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    employees: List[schemas.EmployeeOut]|None = crud.list_employees(db, skip, limit)
    if employees:
        return employees
    else:
        raise HTTPException(status_code=404, detail="The database is empty.")        



if __name__ == "__main__":
    # USed to run the code in debug mode.
    uvicorn.run(api, host="0.0.0.0", port=8000)