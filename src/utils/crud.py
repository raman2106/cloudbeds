from sqlalchemy.orm.session import Session
from . import models, schemas, cloudbeds_exceptions
from pydantic import EmailStr, SecretStr
from sqlalchemy import select, Row, or_, update, Delete, Insert, Select
from itertools import islice
from typing import List, Dict
import secrets, string
from werkzeug.security import generate_password_hash

def generate_password(length=10) -> str:
    '''
    Generates secured default password. Default length of the generated password record is 10.
    '''
    characters: str = string.ascii_letters + string.digits + string.punctuation
    password: SecretStr = ''.join(secrets.choice(characters) for _ in range(length))
    return password

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
    
    result: List[Row]|None = db.execute(stmt).fetchall()
    if result:
        employees:List[schemas.EmployeeOut] = []
        for employee in result:
            employees.append(build_emp_out_payload(employee))
        return employees
    return None

def create_employee(payload: schemas.EmployeeIn, db: Session) -> schemas.EmployeePasswordOut:
    '''
    Creates an employee record in the database.
    '''
    # Create a record in the Employees table
    employee: models.Employee = models.Employee(**payload.emp_details.model_dump())
    # Set a secured password
    password:SecretStr = generate_password()
    employee.set_password(password)
    db.add(employee)
    db.commit()
    #Refresh the instance so that it contains any new data from the DB, such as generated record ID.
    db.refresh(employee)
    # Create a record in the EmployeeAddresses table
    address: models.EmployeeAddress = models.EmployeeAddress(**payload.emp_address.model_dump(exclude="emp_id"))
    address.emp_id = employee.emp_id
    db.add(address)
    db.commit()
    # Create the return payload
    result: schemas.EmployeePasswordOut = schemas.EmployeePasswordOut(emp_id=employee.emp_id, password=password)
    return result

def reset_password(emp_id: int, db: Session) -> schemas.EmployeePasswordOut:
    '''
    Resets the employee's password and returns the new password to the caller.
    Args:
    * emp_id: (int) Employee ID
    * db: (Session) SQL alchemy session
    '''
    # Create an update statement
    password:SecretStr = generate_password()
    stmt = update(models.Employee).where(models.Employee.emp_id == emp_id).values(password_hash=generate_password_hash(password))
    
    db.execute(stmt)
    db.commit()
    # Create the return payload
    result: schemas.EmployeePasswordOut = schemas.EmployeePasswordOut(emp_id=emp_id, password=password)
    return result

def manage_employee(emp_id:int, is_active: bool, db: Session)  -> schemas.ManageEmployeeOut:
    '''
    Sets the activation status of the specifed employee.
    Args:
    * emp_id: (int) Employee ID
    * is_active: (bool) Status of the employee
    * db: (Session) SQL alchemy session 
    '''
    # Create an update statement
    stmt = update(models.Employee).where(models.Employee.emp_id == emp_id).values(is_active=is_active)
    db.execute(stmt)
    db.commit()
    # Create the return payload
    stmt = select(models.Employee.emp_id,
                  models.Employee.is_active).   \
            select_from(models.Employee).   \
            where(models.Employee.emp_id == emp_id)
    employee: Row = db.execute(stmt).fetchone()
    result: schemas.ManageEmployeeOut = schemas.ManageEmployeeOut.model_validate(employee._asdict())
    return result


class Room():
    def __init__(self, db: Session):
        self.db = db

    # Private methods
    def __add_room_type(self, room_type: str) -> int:
        '''
        Adds a room type to the database.

        Returns:
            0 (int): If the operation is successful.

        Raises:
            ValueError: If the room_type exists in the database.
            DBError: If the operation fails to add the room type to the database.
        '''
        try:
            # Check if the supplied room_type is available in DB. If yes, raise ValueError
            stmt = Select(models.RoomType.room_type).where(models.RoomType.room_type == room_type)
            result: Row = self.db.execute(stmt).fetchone()
            if result:
                raise ValueError
            stmt =  Insert(models.RoomType).values(room_type=room_type)
            self.db.execute(stmt)
            self.db.commit()
            return 0
        except Exception as e:
            match e.__class__.__name__:
                case "ValueError":
                    raise ValueError(f"{room_type} exists in the database.")
                case _:
                    raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}:DB operation failed.")
        
    def __delete_room_type(self, room_type: str) -> int:
        '''
        Removes a room type from the database.

        Returns:
            0 (int): If the operation is successful.

        Raises:
            ValueError: If the room_type doesn't exist in the database.
        '''
        try:
            # Check if the supplied room_type is available in DB. If no, raise ValueError
            stmt = Select(models.RoomType.room_type).where(models.RoomType.room_type == room_type)
            result: Row = self.db.execute(stmt).fetchone()
            if result == None:
                raise ValueError            
            stmt = Delete(models.RoomType).where(models.RoomType.room_type == room_type)
            self.db.execute(stmt)
            self.db.commit()
            return 0
        except Exception as e:
            match e.__class__.__name__:
                case "ValueError":
                    raise ValueError(f"{room_type} doesn't exist in the database.")
                case _:
                    raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}:DB operation failed.")
    def __update_room_type(self, room_type: str, new_room_type: str) -> int:
            '''
            Updates a room type in the database.

            Args:
                room_type (str): The current room type to be updated.
                new_room_type (str): The new room type to replace the current room type.

            Returns:
                int: 0 if the operation is successful.

            Raises:
                ValueError: If the room_type doesn't exist in the database.
                cloudbeds_exceptions.DBError: If the database operation fails.
            '''
            try:
                # Check if the supplied room_type is available in DB. If not, raise ValueError.
                stmt = Select(models.RoomType.room_type).where(models.RoomType.room_type == room_type)
                result: Row = self.db.execute(stmt).fetchone()
                if result is None:
                    raise ValueError(f"{room_type} doesn't exist in the database.")
                
                stmt = update(models.RoomType).where(models.RoomType.room_type == room_type).values(room_type=new_room_type)
                self.db.execute(stmt)
                self.db.commit()
                return 0
            except Exception as e:
                match e.__class__.__name__:
                    case "ValueError":
                        raise ValueError(f"{room_type} doesn't exist in the database.")
                    case _:
                        raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}: DB operation failed.")

    # Public methods
    def get_supported_room_types(self) -> schemas.RoomTypeBase:
            """
            Returns the supported room types.

            Returns:
                list: A list of supported room types.
            """
            stmt = select(models.RoomType.id, models.RoomType.room_type)
            result: list[Row] = self.db.execute(stmt).fetchall()
            supported_room_types: list[str] = {"room_types":[row.room_type for row in result]}
            return supported_room_types

    def get_supported_room_states(self) -> schemas.RoomStateBase:
        """
        Returns the supported room status.

        Returns:
            list: A list of room status.
        """
        stmt = select(models.RoomState.id, models.RoomState.room_state)
        result: list[Row] = self.db.execute(stmt).fetchall()
        room_status: list[str] = {"room_states":[row.room_state for row in result]}
        return room_status

    def manage_room_types(self, action: str, room_type: str, new_room_type: str|None = None) -> schemas.GenericMessage:
        """
        Manages the room_types in the models.room_type table.

        Args:
            action: (str) The action to be performed. It can be either "add", "update", or "delete".
            room_type: (str) The room type to be added, updated, or deleted.
            new_room_type: (str) The new room type to replace the current room type when updating.

        Returns:
            schemas.GenericMessage: A message indicating the success or failure of the operation.

        Raises:
            InvalidArgument: If the action is not valid. 
            ValueError: 
                *   If the room type already exists when adding.
                *   If the room type doesn't exist when updating or removing.
            DBError: If the operation fails due to an unknown error.
        """
        result:int
        if action == "add":
            result = self.__add_room_type(room_type)
        elif action == "delete":
            result = self.__delete_room_type(room_type)
        elif action == "update":
            result = self.__update_room_type(room_type, new_room_type)
        else:
            raise cloudbeds_exceptions.InvalidArgument("Invalid action. It should be either 'add', 'remove' or 'delete'.")
        if result == 0:
            return {"msg":"Success"}
            

