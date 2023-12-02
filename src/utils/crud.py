from sqlalchemy.orm.session import Session
from . import models, schemas
from pydantic import EmailStr
from sqlalchemy import select, Row, or_, Column
from itertools import islice
from typing import List

def build_emp_out_payload(result:Row)->schemas.EmployeeOut:
    '''Builds the EmployeeOut payload'''
    emp_id: int = result.emp_id
    emp_details: dict(str,str) = dict(islice(result._asdict().items(), 1, 7))
    emp_address: dict(str,str) = dict(islice(result._asdict().items(), 7, len(result._asdict())))
    # Create an instance of the EmployeeOut class
    employee: schemas.EmployeeOut = schemas.EmployeeOut(emp_id=emp_id, emp_details=emp_details, emp_address=emp_address)
    return employee


def get_employee(id: int|EmailStr, db: Session) -> schemas.EmployeeOut|None:
    '''
    Returns the details of an employee. If Employee isn't found in the database, it returns None.
    Args:
        * id: Employee ID (int) or Employee email (EmailString)
        * db: SQL Alchemy session object
    '''
    stmt = select(models.Employee.emp_id, 
            models.Employee.first_name,
            models.Employee.middle_name,
            models.Employee.last_name,
            models.Employee.phone,
            models.Employee.email,
            models.Employee.is_active,
            models.EmployeeAddress.address_type,
            models.EmployeeAddress.first_line,
            models.EmployeeAddress.second_line,
            models.EmployeeAddress.landmark,
            models.EmployeeAddress.district,
            models.EmployeeAddress.state,
            models.EmployeeAddress.pin).    \
        select_from(models.Employee).   \
        join(models.EmployeeAddress, models.Employee.emp_id == models.EmployeeAddress.emp_id).\
         where(or_(models.Employee.emp_id == id, models.Employee.email == id))
    
    result: Row|None = db.execute(stmt).fetchone()

    if result:
        employee: schemas.EmployeeOut = build_emp_out_payload(result)
    else:
        employee = None

    return employee

def list_employees(db: Session, skip: int = 0, limit: int = 10) -> List[schemas.EmployeeOut]|None:
    '''
    Returns the list of all employees from the database. If the database is empty, it returns [None].
    By default, it returns 10 records at a time.
    Args:
        * db: SQL Alchemy session object
        * skip: (int) Starting record number
        * limit: (int) End record number
    '''
    stmt = select(models.Employee.emp_id, 
            models.Employee.first_name,
            models.Employee.middle_name,
            models.Employee.last_name,
            models.Employee.phone,
            models.Employee.email,
            models.Employee.is_active,
            models.EmployeeAddress.address_type,
            models.EmployeeAddress.first_line,
            models.EmployeeAddress.second_line,
            models.EmployeeAddress.landmark,
            models.EmployeeAddress.district,
            models.EmployeeAddress.state,
            models.EmployeeAddress.pin).    \
        select_from(models.Employee).   \
        join(models.EmployeeAddress, models.Employee.emp_id == models.EmployeeAddress.emp_id). \
        limit(limit).offset(skip)
    
    result: Row|None = db.execute(stmt).fetchall()
    if result:
        employees:List[schemas.EmployeeOut] = []
        for employee in result:
            employees.append(build_emp_out_payload(employee))
        return employees
    return None