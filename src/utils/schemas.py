# Fro more info on string constraint validator, see https://docs.pydantic.dev/latest/concepts/models/
from pydantic import (
    BaseModel,
    EmailStr
)

class CustomerBase(BaseModel):
    first_name: str
    middle_name: str | None
    last_name: str
    email: EmailStr
    phone: str

class CustomerAddressBase(BaseModel):
    first_line: str
    second_line: str|None
    landmark: str|None
    district: str
    state: str
    pin: str
    address_type: str

class CreateCustomerResult(BaseModel):
    msg: str
    customer_id: int

class CustomerIn(BaseModel):
    cust_details: CustomerBase
    cust_address: CustomerAddressBase

class CustomerOut(BaseModel):
    customer_id: int
    cust_details: CustomerBase
    cust_address: CustomerAddressBase

class EmployeeBase(BaseModel):
    first_name: str 
    middle_name: str | None
    last_name: str
    email: EmailStr
    phone: str
    is_active: bool = False

class EmployeeAddressBase(BaseModel):
    first_line: str
    second_line: str|None
    landmark: str|None
    district: str
    state: str
    pin: str
    address_type: str

class EmployeeIn(BaseModel):
    emp_details: EmployeeBase
    emp_address: EmployeeAddressBase

class EmployeeOut(BaseModel):
    emp_id: int
    emp_details: EmployeeBase
    emp_address: EmployeeAddressBase

class EmployeePasswordOut(BaseModel):
    emp_id: int
    password: str

class ManageEmployeeOut(BaseModel):
    emp_id: int
    is_active: bool

class RoomTypeBase(BaseModel):
    room_types: list[str]

class RoomStateBase(BaseModel):
    room_states: list[str]
    
class RoomTypeIn(BaseModel):
    room_type: str

class GenericMessage(BaseModel):
    msg:str

class RoomBase(BaseModel):
    room_number: int
    room_type: str
    room_state: str | None = "Available"

class ListRooms(BaseModel):
    room_type: str | None = None
    room_state: str | None = None