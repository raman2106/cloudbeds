from sqlalchemy.orm.session import Session
from . import models, schemas
from pydantic import EmailStr
from sqlalchemy import select, Row
from typing import List

def get_employee_by_email(email: EmailStr, db: Session)-> schemas.ReadEmployee|None:
    '''
    Returns the information of the employee (without address) that matches the provided email.
    '''
    employee: models.Employee|None = db.query(models.Employee).filter(models.Employee.email == email).first()
    emp_data: schemas.ReadEmployee|None
    if employee:
        emp_data = schemas.ReadEmployee(emp_id=employee.emp_id, details = schemas._EmployeeBase.model_validate(employee, from_attributes=True))
    else:
        emp_data = None
    
    return emp_data

def get_employee_by_id(id: int, db: Session) -> schemas.ReadFullEmployeeData:
    '''
    Returns the information of the employee (with address) that matches the provided employee ID.
    '''
    # If employee ID exists in DB, retuen the employee details(along with address)
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
            join(models.EmployeeAddress, models.Employee.emp_id == models.EmployeeAddress.emp_id).where(models.Employee.emp_id == id)

    print(stmt)
    employees: list(Row) = db.execute(stmt).fetchall()
    employee: schemas.ReadFullEmployeeData =  schemas.ReadFullEmployeeData.model_validate(employees[0], from_attributes=True)
    return employee

def create_employee(db: Session, payload: schemas.CreateEmployee)-> schemas.CreateEmployeeResult | None:
    '''
    Creates an employee record from the provided information.
    '''
    # Create a record in the Employees table
    employee: models.Employee = models.Employee(**payload.emp_details.model_dump())
    employee.set_password(payload.password.value.get_secret_value())
    db.add(employee)
    db.commit()
    #Refresh the instance so that it contains any new data from the DB, such as generated record ID.
    db.refresh(employee)

    # Create a record in the EmployeeAddresses table
    address: models.EmployeeAddress = models.EmployeeAddress(**payload.address.model_dump(exclude="emp_id"))
    address.emp_id = employee.emp_id
    db.add(address)
    db.commit()

    # Create the return payload
    result: schemas.CreateEmployeeResult = schemas.CreateEmployeeResult(emp_id=employee.emp_id)
    return result

def list_employees(db: Session) -> List[schemas.ReadFullEmployeeData]:
    '''
    Returns a list of all the employee records available in the database.
    '''
    #FIXME: Implement pagination
    # Create  a join statement to get the full employee data from the database
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
            join(models.EmployeeAddress, models.Employee.emp_id == models.EmployeeAddress.emp_id)

    employees: list(schemas.ReadFullEmployeeData) = db.execute(stmt).fetchall()
    return employees

def update_employee_details(db: Session, payload: schemas.CreateEmployee) -> schemas.UpdateEmployeeResponse:
    '''
    Updates the employee record (Employees and EmployeeAddresses tables). It uses the email to identify the employee record.
    '''
    # Identify the employee record
    emp: schemas.ReadEmployee = get_employee_by_email(email=payload.emp_details.email, db=db)
    if not emp:
        pass
    # Identify the info that needs to be updated.
    # Update info in DB
    # Return response
    pass