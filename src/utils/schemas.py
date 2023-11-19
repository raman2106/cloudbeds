from pydantic import BaseModel, Field, SecretStr, EmailStr
from datetime import date, timedelta
from typing import Annotated
from enum import Enum

# The *Base model stores the common feilds required during read as well as Create/update operations 
#FIXME: Add validation for the model's fields


class _EmployeeBase(BaseModel):
    '''
    Specifies the common fields used in the following classes:
    * CreateEmployee
    * ReadEmployee 
    '''
    first_name: str
    middle_name: str | None
    last_name: str
    phone: str
    email: EmailStr
    is_active: bool = False

    class Config:
        allow_population_by_field_name = True
        from_attributes=True

class AddressTypeEnum(str, Enum):
    Correspondence = "Correspondence"
    Permanent = "Permanent"

class _EmployeeAddressBase(BaseModel):
    '''
    Specifies the common fields used in the following classes:
    * CreateEmployeeAddress
    * ReadEmployeeAddress 
    '''
    emp_id: int
    first_line: str
    second_line: str
    landmark: str
    district: str
    state: str
    pin: str
    address_type: AddressTypeEnum

    class Config:
        allow_population_by_field_name = True
        from_attributes=True

class _EmployeePassword(BaseModel):
    '''
    Specifies the password attribute for an employee. Use this class with CreateEmployee class only.
    '''
    value: SecretStr

class CreateEmployee(BaseModel):
    '''
    Specifies the attributes required to create an employee record in the database.
    It includes the following group of fields:
    * emp_details
    * password
    * address
    '''
    emp_details: _EmployeeBase
    password: _EmployeePassword
    address: _EmployeeAddressBase

class ReadEmployee(BaseModel):
    '''
    Specifies the fields required to read details of an employee (without address) from the database. 
    '''
    emp_id: int
    details: _EmployeeBase
    
    class Config:
        orm_mode = True
    

class ReadEmployeeAddress(BaseModel):
    '''
    Specifies the fields required to read address of an employee (withiut employee details such as name, email, and so on) from the database.
    '''
    address_id: int | None
    details: _EmployeeAddressBase

    class Config:
        orm_mode = True

# class ReadFullEmployeeData(BaseModel):
#     '''
#     Specifies the fields required to read complete details of an employee from the database.
#     '''
#     employee_details: ReadEmployee
#     #FIXME: schemas.ReadEmployeeAddress(address) should be a list
#     address: ReadEmployeeAddress


class CreateEmployeeResult(BaseModel):
    '''
    Specifies the fields returned upon successful creation of the following records in the DB:
    * Employee
    * EmployeeAddress
    '''
    emp_id: int

    class Config:
        from_attributes=True


class UpdateEmployeeResponse(BaseModel):
    '''
    Specifies the fields returned upon successful update employee operation.
    * msg
    '''
    msg: str


class ReadFullEmployeeData(_EmployeeAddressBase, _EmployeeBase):
    emp_id: int
    class Config:
        from_attributes=True