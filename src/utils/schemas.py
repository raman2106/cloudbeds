from pydantic import (
    BaseModel,
    EmailStr,
    root_validator,
    validator,
    SecretStr
)
from typing import Any

class EmployeeBase(BaseModel):
    first_name: str 
    middle_name: str | None
    last_name: str
    email: EmailStr
    phone: str
    is_active: bool = False

    # @root_validator(pre=True)
    # def check_string_length(cls, values: dict[str, Any]):
    #     for field_name, field_value in values.items():
    #         if isinstance(field_value, str):
    #             if len(field_value) > 20:
    #                 raise ValueError(f"{field_name} exceeds maximum length (limit: 20)")
    #     return values    

    # @validator("email", "phone")
    # def check_length(cls, value: str, field: str) -> str:
    #     if field.name == "email":
    #         max_len: int = 40
    #     elif field.name == "phone":
    #         max_len: int = 20
    #     else:
    #         raise ValueError(f"Unexpected field: {field.name}")

    #     if len(value) > max_len:
    #         raise ValueError(f"{field.name} exceeds maximum length (limit: {max_len})")
    #     return value  

class EmployeeAddressBase(BaseModel):
    first_line: str
    second_line: str|None
    landmark: str|None
    district: str
    state: str
    pin: str
    address_type: str

    # @root_validator(pre=True)
    # def check_string_length(cls, values: dict[str, Any]):
    #     for field_name, field_value in values.items():
    #         if isinstance(field_value, str):
    #             if len(field_value) > 20:
    #                 raise ValueError(f"{field_name} exceeds maximum length (limit: 20)")
    #     return values    

    # @validator("landmark", "district", "state", "pin", "address_type")
    # def check_length(cls, value: str, field: str) -> str:
    #     if field.name == "landmark" or field.name == "district":
    #         max_len: int = 30
    #     elif field.name == "state" or field.name == "address_type":
    #         max_len: int = 20
    #     elif field.name == "pin":
    #         max_len: int = 20
    #     else:
    #         raise ValueError(f"Unexpected field: {field.name}")

    #     if len(value) > max_len:
    #         raise ValueError(f"{field.name} exceeds maximum length (limit: {max_len})")
    #     return value 

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
