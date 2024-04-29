# Fro more info on string constraint validator, see https://docs.pydantic.dev/latest/concepts/models/
from fastapi import UploadFile
from typing import Optional
from pydantic import (
    BaseModel,
    EmailStr,
    Field
)
from datetime import datetime, date, timezone
from dateutil import tz
from enum import Enum

class AddressType(str, Enum):
    Permanent = "Permanent"
    Correspondence = "Correspondence"

class GovtIdtype(str, Enum):
    Aadhar = "AADHAR"
    PAN = "PAN"
    VoterID = "Voter ID"
    Passport = "Passport"
    DrivingLicense = "Driving License"

class RoomType(str, Enum):
    standard = "Standard"
    deluxe = "Deluxe"
    club = "Club"
    suite = "Suite"

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
    address_type: AddressType = Field(..., pattern='^(Permanent|Correspondence)$')

class CreateCustomerResult(BaseModel):
    msg: str
    customer_id: int

class CustomerIn(BaseModel):
    customer_details: CustomerBase
    customer_address: CustomerAddressBase

class CustomerOut(BaseModel):
    customer_id: int
    customer_details: CustomerBase
    customer_address: CustomerAddressBase

class EmployeeBase(BaseModel):
    first_name: str 
    middle_name: str | None
    last_name: str
    email: EmailStr
    phone: int
    is_active: bool = False

class EmployeeAddressBase(BaseModel):
    first_line: str
    second_line: str|None
    landmark: str|None
    district: str
    state: str
    pin: str
    # Address type can be either 'Permanent' or 'Correspondence'
    address_type: AddressType = Field(..., pattern='^(Permanent|Correspondence)$')

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
    room_type: RoomType
    room_state: str | None = "Available"

class ListRooms(BaseModel):
    room_type: str | None = None
    room_state: str | None = None

class BookingBase(BaseModel):
    booked_on: datetime = Field(default_factory=lambda: datetime.now)
    status: Optional[str| None] = Field(default=None, description="Don't specify any value for this field. It will be set to 'Booked' automatically.")
    checkin: date
    checkout: date
    government_id_type: GovtIdtype
    government_id_number: str
    exp_date: Optional[date | None] = Field(default=None)
    govt_id_image: Optional[UploadFile| None] = Field(default=None)
    room_num: int | None
    comments: str | None
    emp_id: int

class BookingIn(BaseModel):
    customer: CustomerIn
    booking: BookingBase

class BookingResult(GenericMessage):
    booking_id: str

class BookingOut(BaseModel):
    booking_id: str
    customer: CustomerOut
    booking: BookingBase

class GovtIdTypeBase(BaseModel):
    name: str

