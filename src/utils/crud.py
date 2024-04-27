from sqlalchemy.orm.session import Session
from . import models, schemas, cloudbeds_exceptions
from pydantic import EmailStr, SecretStr
from sqlalchemy import select, Row, or_, update, Delete, Insert, Select, and_, ResultProxy, Update
from itertools import islice
from typing import List, Dict
import secrets, string
from werkzeug.security import generate_password_hash
import traceback
from datetime import datetime, date, timedelta
from dateutil import tz

def generate_password(length=10) -> str:
    '''
    Generates secured default password. Default length of the generated password record is 10.
    '''
    characters: str = string.ascii_letters + string.digits + string.punctuation
    password: SecretStr = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def build_emp_out_payload(result:Row)->schemas.EmployeeOut:
    '''Builds the EmployeeOut payload'''
    employee_data: dict[str, str] = result.Employee.__dict__
    employee_data = dict(islice(employee_data.items(), 1, len(employee_data.items())))
    emp_id: int = employee_data.pop("emp_id")
    # We don't want to expose the password hash through this method
    del employee_data["password_hash"]
    # EmployeeOut payload doesn't accept the following attributes: current_login_at, current_login_ip, last_login_at, last_login_ip, login_count
    del employee_data["current_login_at"]
    del employee_data["current_login_ip"]
    del employee_data["last_login_at"]
    del employee_data["last_login_ip"]
    del employee_data["login_count"]

    # Use the backref to get the employee's address
    employee_address: dict[str, str] = result.Employee.addresses[0].__dict__
    employee_address = dict(islice(employee_address.items(), 1, len(employee_address.items())))
    # Remove unnecessary attributes from the employee address
    del employee_address["emp_id"]
    del employee_address["address_id"]
    
    # Generate the EmployeeOut payload
    employee: schemas.EmployeeOut = schemas.EmployeeOut(emp_id=emp_id, emp_details=employee_data, emp_address=employee_address)
    return employee

def get_employee(query_value: int|EmailStr, db: Session) -> schemas.EmployeeOut|None:
    '''
    Returns the details of an employee. If Employee isn't found in the database, it returns None.
    Args:
        * query_value: Employee ID (int) or Employee email (EmailString)
        * db: SQL Alchemy session object
    '''
    try:
        if isinstance(query_value, int):
            stmt: Select = Select(models.Employee).where(models.Employee.emp_id == query_value)
        elif EmailStr._validate(query_value):
            stmt: Select = Select(models.Employee).where(models.Employee.email == query_value)
        else:
            raise ValueError("Invalid query value. It should be either an integer or an email string.")
        result: Row|None = db.execute(stmt).fetchone()
        if result:
            employee: schemas.EmployeeOut = build_emp_out_payload(result)
        else:
            employee = None
        return employee
    
    except Exception as e:
        raise ValueError(f"{e.__class__.__name__}: {e}")

def list_employees(db: Session, skip: int = 0, limit: int = 10) -> List[schemas.EmployeeOut]|None:
    '''
    Returns the list of all employees from the database. If the database is empty, it returns [None].
    By default, it returns 10 records at a time.
    Args:
        * db: SQL Alchemy session object
        * skip: (int) Starting record number
        * limit: (int) End record number
    '''
    try:
        stmt: Select = Select(models.Employee).limit(limit).offset(skip)
        result: List[Row]|None = db.execute(stmt).fetchall()
        # If there are no employee records in the database, raise an error.
        if result == None:
            raise ValueError("No employee records found in the database.")
        # Build the EmployeeOut payload 
        employees:List[schemas.EmployeeOut] = [build_emp_out_payload(employee) for employee in result]
        return employees
    except Exception as e:
        traceback(traceback.print_exc())
        match e.__class__.__name__:
            case "ValueError":
                raise ValueError(f"{e.__class__.__name__}: {e}")
            case _:
                raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}:DB operation failed.")

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

class RoomType():
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

    def _get_supported_room_types_with_id(self) -> List[Row]:
        '''
        Returns the supported room types with their IDs.

        Returns:
            list: A list of supported room types with their IDs.
        '''
        stmt = select(models.RoomType.id, models.RoomType.room_type)
        result: list[Row] = self.db.execute(stmt).fetchall()
        return result

    def _verify_room_type(self, room_type: str) -> bool:
        '''
        Verifies if the supplied room type exists in the database.

        Returns:
            bool: True if the room type exists in the database.
        '''
        stmt = select(models.RoomType.room_type).where(models.RoomType.room_type == room_type)
        result: Row = self.db.execute(stmt).fetchone()
        if result:
            return True
        return False

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
            
class RoomState():
    
    def __init__(self, db: Session):
        self.db = db

    def __add_room_state(self, room_state: str) -> int:
        '''
        Adds a room state to the database.

        Returns:
            0 (int): If the operation is successful.

        Raises:
            ValueError: If the room_state exists in the database.
            DBError: If the operation fails to add the room state to the database.
        '''
        try:
            # Check if the supplied room_state is available in DB. If yes, raise ValueError
            stmt = Select(models.RoomState.room_state).where(models.RoomState.room_state == room_state)
            result: Row = self.db.execute(stmt).fetchone()
            if result:
                raise ValueError
            stmt =  Insert(models.RoomState).values(room_state=room_state)
            self.db.execute(stmt)
            self.db.commit()
            return 0
        except Exception as e:
            match e.__class__.__name__:
                case "ValueError":
                    raise ValueError(f"{room_state} exists in the database.")
                case _:
                    raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}:DB operation failed.")
        
    def __delete_room_state(self, room_state: str) -> int:
        '''
        Removes a room state from the database.

        Returns:
            0 (int): If the operation is successful.

        Raises:
            ValueError: If the room_state doesn't exist in the database.
        '''
        try:
            # Check if the supplied room_state is available in DB. If no, raise ValueError
            stmt = Select(models.RoomState.room_state).where(models.RoomState.room_state == room_state)
            result: Row = self.db.execute(stmt).fetchone()
            if result == None:
                raise ValueError            
            stmt = Delete(models.RoomState).where(models.RoomState.room_state == room_state)
            self.db.execute(stmt)
            self.db.commit()
            return 0
        except Exception as e:
            match e.__class__.__name__:
                case "ValueError":
                    raise ValueError(f"{room_state} doesn't exist in the database.")
                case _:
                    raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}:DB operation failed.")
                
    def __update_room_state(self, room_state: str, new_room_state: str) -> int:
            '''
            Updates a room  state in the database.
            Returns:
                0 if the operation is successful.
            Raises:
                ValueError: If the room_state doesn't exist in the database.
                cloudbeds_exceptions.DBError: If the database operation fails.
            '''
            try:
                # Check if the supplied room_state is available in DB. If not, raise ValueError.
                stmt = Select(models.RoomState.room_state).where(models.RoomState.room_state == room_state)
                result: Row = self.db.execute(stmt).fetchone()
                if result is None:
                    raise ValueError(f"{room_state} doesn't exist in the database.")
                
                stmt = update(models.RoomState).where(models.RoomState.room_state == room_state).values(room_state=new_room_state)
                self.db.execute(stmt)
                self.db.commit()
                return 0
            except Exception as e:
                match e.__class__.__name__:
                    case "ValueError":
                        raise ValueError(f"{room_state} doesn't exist in the database.")
                    case _:
                        raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}: DB operation failed.")

    def _verify_room_state(self, room_state: str) -> bool:
        '''
        Verifies if the supplied room state exists in the database.

        Returns:
            bool: True if the room state exists in the database.
        '''
        stmt = select(models.RoomState.room_state).where(models.RoomState.room_state == room_state)
        result: Row = self.db.execute(stmt).fetchone()
        if result:
            return True
        return False

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

    def manage_room_states(self, action: str, room_state: str, new_room_state: str|None = None) -> schemas.GenericMessage:
        """
        Manages the room_states in the models.room_state table.

        Args:
            action: (str) The action to be performed. It can be either "add", "update", or "delete".
            room_state: (str) The room state to be added, updated, or deleted.
            new_room_state: (str) The new room state to replace the current room state when updating.

        Returns:
            schemas.GenericMessage: A message indicating the success or failure of the operation.

        Raises:
            InvalidArgument: If the action is not valid. 
            ValueError: 
                *   If the room state already exists when adding.
                *   If the room state doesn't exist when updating or removing.
            DBError: If the operation fails due to an unknown error.
        """
        result:int
        if action == "add":
            result = self.__add_room_state(room_state)
        elif action == "delete":
            result = self.__delete_room_state(room_state)
        elif action == "update":
            result = self.__update_room_state(room_state, new_room_state)
        else:
            raise cloudbeds_exceptions.InvalidArgument("Invalid action. It should be either 'add', 'remove' or 'delete'.")
        if result == 0:
            return {"msg":"Success"}

class Room(RoomType, RoomState):
    def __init__(self, db: Session):
        self.db = db
        RoomType.__init__(self, db)
        RoomState.__init__(self, db)

    def add_room(self, room_number: int, room_type: str, room_state: str) -> schemas.GenericMessage:
        '''
        Adds a room to the database.

        Args:
            room_number: (int) The room number.
            room_type: (str) The room type.
            room_state: (str) The room state.

        Returns:
            schemas.GenericMessage: A message indicating the success or failure of the operation.

        Raises:
            ValueError: 
                *   If the room type or room state doesn't exist in the database.
                *   If the room number already exists in the database.
            DBError: If the operation fails due to an unknown error.
        '''
        if not self._verify_room_type(room_type):
            raise ValueError(f"Invalid room_type: {room_type}")
        if not self._verify_room_state(room_state):
            raise ValueError(f"Invalid room_state: {room_state}")
        try:
            # Check if the supplied room_number is available in DB. If yes, raise ValueError
            stmt = Select(models.Room.room_number).where(models.Room.room_number == room_number)
            result: Row = self.db.execute(stmt).fetchone()
            if result:
                raise ValueError
            # Get room_type_id by using the room_type
            room_types: list[Row] = self._get_supported_room_types_with_id()
            r_type_id: int = [row.id for row in room_types if row.room_type == room_type][0]
            # Get state_id by using the room_state
            room_states: list[Row] = self.__get_supported_booking_statuses_with_id()
            state_id: int = [row.id for row in room_states if row.room_state == room_state][0]
            # Insert the room record
            stmt = Insert(models.Room).values(room_number=room_number, r_type_id=r_type_id, state_id=state_id)
            self.db.execute(stmt)
            self.db.commit()
            return {"msg":"Success"}
        except Exception as e:
            match e.__class__.__name__:
                case "ValueError":
                    raise ValueError(f"{room_number} exists in the database.")
                case _:
                    raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}:DB operation failed.")
                
    def delete_room(self, room_number: str) -> schemas.GenericMessage:
        '''
        Removes a room from the database.

        Args:
            room_number: (str) The room number.

        Returns:
            schemas.GenericMessage: A message indicating the success or failure of the operation.

        Raises:
            *   ValueError: If the room number doesn't exist in the database.
            *   DBError: If the operation fails due to an unknown error.
        '''
        try:
            # Check if the supplied room_number is available in DB. If no, raise ValueError
            room_number: int = int(room_number)
            stmt = Select(models.Room.room_number).where(models.Room.room_number == room_number)
            result: Row = self.db.execute(stmt).fetchone()
            if result == None:
                raise ValueError
            # [FIXME] Add a check to see if the room is occupied. If yes, raise an error.
            stmt = Delete(models.Room).where(models.Room.room_number == room_number)
            self.db.execute(stmt)
            self.db.commit()
            return {"msg":"Success"}
        except Exception as e:
            match e.__class__.__name__:
                case "ValueError":
                    raise ValueError(f"{room_number} doesn't exist in the database.")
                case _:
                    raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}:DB operation failed.")

    def list_rooms(self, skip: int, limit: int, room_number: str | None = None, room_type: str|None = None, room_state: str|None = None) -> List[schemas.RoomBase]:
        '''
        Returns the list of rooms from the database.

        Args:
            skip (int): The number of records to skip.
            limit (int): The maximum number of rooms to return.
            room_type (str, optional): The room type to filter by. Defaults to None.
            room_state (str, optional): The room state to filter by. Defaults to None.

        Returns:
            List[schemas.RoomBase]: A list of rooms.

        Raises:
            ValueError: If the room type or room state doesn't exist in the database.
            DBError: If the operation fails due to an unknown error.
        '''
        if room_number:
            room_number: int = int(room_number)
            try:
                # Query to get the list of rooms that match the specified room_number
                stmt = select(models.Room.room_number, \
                            models.RoomType.room_type, \
                            models.RoomState.room_state).\
                    select_from(models.Room,
                                models.RoomType,
                                models.RoomState).\
                    where(\
                        and_(\
                            models.Room.r_type_id == models.RoomType.id, \
                            models.Room.state_id ==  models.RoomState.id,\
                            models.Room.room_number == room_number\
                        )\
                    )
                result: list[Row] = self.db.execute(stmt).fetchall()
                if result == []:
                    raise ValueError
                rooms: List[schemas.RoomBase] = [schemas.RoomBase.model_validate(row._asdict()) for row in result]
                return rooms
            except Exception as e:
                match e.__class__.__name__:
                    case "ValueError":
                        raise ValueError(f"Couldn't find any rooms that match the specified criteria.")
                    case _:
                        raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}:DB operation failed.")
        
        else:
            # Check if the supplied room_type or room_state is available in DB. If not, raise ValueError.
            # If room_type and room_state is available in DB, get the room_type_id and state_id.
            if room_type:
                if self._verify_room_type(room_type):
                    room_type: (int) = [row.id for row in self._get_supported_room_types_with_id() \
                                        if row.room_type.lower() == room_type.lower()][0]
                else:
                    raise ValueError(f"{room_type} doesn't exist in the database.")
            if room_state:
                if self._verify_room_state(room_state):
                    room_state: (int) = [row.id for row in self.__get_supported_booking_statuses_with_id() \
                                        if row.room_state.lower() == room_state.lower()][0]
                else:
                    raise ValueError(f"{room_state} doesn't exist in the database.")

            try:
                if room_type and room_state:
                    # Query to get the list of rooms that match the specified room_type and room_state
                    stmt = select(models.Room.room_number, \
                                models.RoomType.room_type, \
                                models.RoomState.room_state).\
                        select_from(models.Room,
                                    models.RoomType,
                                    models.RoomState).\
                        where(\
                            and_(\
                                models.Room.r_type_id == models.RoomType.id, \
                                models.Room.state_id ==  models.RoomState.id,\
                                models.Room.r_type_id == room_type, \
                                models.Room.state_id == room_state\
                            )\
                        ).\
                        limit(limit).offset(skip)
                elif room_type:
                    # Query to get the list of rooms that match the specified room_type and any room_state
                    stmt = select(models.Room.room_number, \
                                models.RoomType.room_type, \
                                models.RoomState.room_state).\
                        select_from(models.Room,
                                    models.RoomType,
                                    models.RoomState).\
                        where(\
                            and_(\
                                models.Room.r_type_id == models.RoomType.id, \
                                models.Room.state_id ==  models.RoomState.id,\
                                models.Room.r_type_id == room_type \
                            )\
                        ).\
                        limit(limit).offset(skip)
                elif room_state:
                    # Query to get the list of rooms that match any room_type and the specified room_state
                    stmt = select(models.Room.room_number, \
                                models.RoomType.room_type, \
                                models.RoomState.room_state).\
                        select_from(models.Room,
                                    models.RoomType,
                                    models.RoomState).\
                        where(\
                            and_(\
                                models.Room.r_type_id == models.RoomType.id, \
                                models.Room.state_id ==  models.RoomState.id,\
                                models.Room.state_id == room_state\
                            )\
                        ).\
                        limit(limit).offset(skip)
                else:
                    # Query to get the list of all rooms
                    stmt = select(models.Room.room_number, \
                                models.RoomType.room_type, \
                                models.RoomState.room_state).\
                        select_from(models.Room,
                                    models.RoomType,
                                    models.RoomState).\
                        where(\
                            and_(\
                                models.Room.r_type_id == models.RoomType.id, \
                                models.Room.state_id ==  models.RoomState.id \
                            )\
                        ).\
                        limit(limit).offset(skip)
                    
                result: list[Row] = self.db.execute(stmt).fetchall()
                if result == []:
                    raise ValueError
                rooms: List[schemas.RoomBase] = [schemas.RoomBase.model_validate(row._asdict()) for row in result]
                return rooms
            except Exception as e:
                match e.__class__.__name__:
                    case "ValueError":
                        raise ValueError(f"Couldn't find any rooms that match the specified criteria.")
                    case _:
                        raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}:DB operation failed.")
            
    def update_room(self, room_number: int, room_type: str, room_state: str) -> schemas.GenericMessage:
        '''
        Updates a room in the database.

        Args:
            room_number: (int) The room number.
            room_type: (str) The room type.
            room_state: (str) The room state.

        Returns:
            schemas.GenericMessage: A message indicating the success or failure of the operation.

        Raises:
            ValueError: 
                *   If the room type or room state doesn't exist in the database.
                *   If the room number doesn't exist in the database.
            DBError: If the operation fails due to an unknown error.
        '''
        if not self._verify_room_type(room_type):
            raise ValueError(f"{room_type} doesn't exist in the database.")
        if not self._verify_room_state(room_state):
            raise ValueError(f"{room_state} doesn't exist in the database.")
        try:
            # Check if the supplied room_number is available in DB. If no, raise ValueError
            stmt = Select(models.Room.room_number).where(models.Room.room_number == room_number)
            result: Row = self.db.execute(stmt).fetchone()
            if result == None:
                raise ValueError
            # Get room_type_id by using the room_type
            room_types: list[Row] = self._get_supported_room_types_with_id()
            r_type_id: int = [row.id for row in room_types if row.room_type.lower() == room_type.lower()][0]
            # Get state_id by using the room_state
            room_states: list[Row] = self.__get_supported_booking_statuses_with_id()
            state_id: int = [row.id for row in room_states if row.room_state.lower() == room_state.lower()][0]
            # Update the room record
            stmt = update(models.Room).where(models.Room.room_number == room_number).values(r_type_id=r_type_id, state_id=state_id)
            self.db.execute(stmt)
            self.db.commit()
            return {"msg":"Success"}
        except Exception as e:
            match e.__class__.__name__:
                case "ValueError":
                    raise ValueError(f"{room_number} doesn't exist in the database.")
                case _:
                    raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}:DB operation failed.")
                        
class Customer:
    def __init__(self, db: Session):
        self.db = db

    def __build_customer_out_payload(self, result:Row)->schemas.CustomerOut:
        '''Builds the CustomerOut payload'''
        # The result object is a rwo that contains an instance of the customer table with just on record.
        customer_data: dict[str, str] = result.Customer.__dict__
        # Remove unnecessary attributes from the customer data
        customer_data = dict(islice(customer_data.items(), 1, len(customer_data.items())))
        customer_id: int = customer_data.pop("customer_id")

        # Use the backref to get the customer's address
        customer_address: dict[str, str] = result.Customer.addresses[0].__dict__
        # Remove unnecessary attributes from the customer address
        customer_address = dict(islice(customer_address.items(), 1, len(customer_address.items())))
        del customer_address["customer_id"]

        # Build the CustomerOut payload
        result: schemas.CustomerOut = schemas.CustomerOut(customer_id=customer_id, customer_details=customer_data, customer_address=customer_address)
        return result

    # Add customer
    def add_customer(self, customer: schemas.CustomerIn) -> schemas.CreateCustomerResult:
            """
            Adds a new customer to the database.

            Args:
                customer (schemas.CustomerIn): The customer data to be added.

            Returns:
                schemas.CustomerOut: The added customer data.

            Raises:
                cloudbeds_exceptions.DBError: If the database operation fails.
            """
            
            try:
                # Check wheteht the customer exists in DB. 
                # Use cutomer's email or phone to check if the customer exists in the DB.
                stmt = Select("*").where(
                        or_(
                            models.Customer.email == customer.customer_details.email,
                            models.Customer.phone == customer.customer_details.phone
                            )
                        )
                result: Row| None = self.db.execute(stmt).fetchone()
                if result:
                    raise ValueError()
                
                # Add the customer to the database
                stmt: Insert = Insert(models.Customer).values(**customer.customer_details.model_dump())
                customer_result: ResultProxy = self.db.execute(stmt)
                customer_id: int = customer_result.inserted_primary_key[0]

                # Add the customer Address to teh DB
                stmt:Insert = Insert(models.CustomerAddress).values(**customer.customer_address.model_dump(), customer_id=customer_id)
                customer_address_result: ResultProxy = self.db.execute(stmt)

                # Commit the transaction
                self.db.commit()

                # Form the output payload
                result: schemas.CreateCustomerResult = schemas.CreateCustomerResult(msg="success", customer_id=customer_id)
                return result

            except Exception as e:
                traceback.print_exc()
                match e.__class__.__name__:
                    case "ValueError":
                        raise ValueError(f"{customer.customer_details.email} or {customer.customer_details.phone} exists in the database.")
                    case _:
                        raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}:DB operation failed.")

    # Get customer
    def get_customer(self, query_string: str) -> schemas.CustomerOut | None:
        """
        Retrieves a customer from the database based on the provided query string.

        Args:
            query_string (str): The query string to search for a customer. It can be either the customer_id, customer's phone number or customer's email.

        Returns:
            schemas.CustomerOut: The customer information as a `CustomerOut` object.

        Raises:
            ValueError: If the customer doesn't exist in the database.

        """
        try:
            # Check if the customer exists in the DB.
            stmt: Select = Select(models.Customer).where(
                or_(
                    models.Customer.customer_id == query_string,
                    models.Customer.phone == query_string,
                    models.Customer.email == query_string
                )
            )
            result: Row|None = self.db.execute(stmt).fetchone()

            if result == None:
                return None

            # Build return payload
            result: schemas.CustomerOut = self.__build_customer_out_payload(result)
            return result

        except Exception as e:
            traceback.print_exc()
            match e.__class__.__name__:
                case _:
                    raise ValueError("Customer doesn't exist in the database.")

    # List customers
    def list_customers(self, skip: int, limit: int) -> List[schemas.CustomerOut]:
        """
        Retrieves a list of customers from the database.

        Args:
            skip (int): The number of records to skip.
            limit (int): The maximum number of records to return.

        Returns:
            List[schemas.CustomerOut]: A list of customers.

        """
        try:
            # Get the list of customers
            stmt: Select = Select(models.Customer).limit(limit).offset(skip)
            result: List[Row] = self.db.execute(stmt).fetchall()

            # Build the return payload
            customers: List[schemas.CustomerOut] = [self.__build_customer_out_payload(row) for row in result]
            return customers

        except Exception as e:
            traceback.print_exc()
            raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}:DB operation failed.")
    
    # Update customer
    def update_customer(self, payload: schemas.CustomerOut) -> schemas.GenericMessage:
        """
        Updates a customer in the database.

        Args:
            payload (schemas.CustomerOut): The customer data to be updated.

        Returns:
            schemas.GenericMessage: A message indicating the success or failure of the operation.

        Raises:
            ValueError: If the customer doesn't exist in the database.
            cloudbeds_exceptions.DBError: If the database operation fails.
        """
        try:
            # Check if the customer exists in the DB.
            stmt: Select = Select(models.Customer).where(models.Customer.customer_id == payload.customer_id)
            result: Row|None = self.db.execute(stmt).fetchone()
            if result == None:
                raise ValueError()

            # Update the customer data
            stmt: Update = Update(models.Customer). \
                where(models.Customer.customer_id == payload.customer_id).  \
                values(**payload.customer_details.model_dump())
            self.db.execute(stmt)

            # Update the customer address
            stmt: Update = Update(models.CustomerAddress).  \
                where(models.CustomerAddress.customer_id == payload.customer_id).   \
                values(**payload.customer_address.model_dump())
            self.db.execute(stmt)

            # Commit the transaction
            self.db.commit()

            return {"msg":"Success"}

        except Exception as e:
            traceback.print_exc()
            match e.__class__.__name__:
                case "ValueError":
                    raise ValueError("Customer doesn't exist in the database.")
                case _:
                    raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}:DB operation failed.")
                
class Booking:
    def __build_booking_base_payload(self, booking: models.Booking) -> schemas.BookingBase:
        '''
        Builds the BookingBase payload.

        Args:
            result: (Row) The result object containing the booking data.
        '''
        booking_data: schemas.BookingBase = schemas.BookingBase(
            booked_on = booking.booked_on,
            status= booking.booking_status.name,
            checkin = booking.checkin,
            checkout = booking.checkout,
            government_id_type = booking.govt_id_type.name,
            government_id_number = booking.govt_id_num,
            exp_date = booking.exp_date,
            govt_id_image = None,
            room_num = booking.room.room_number,
            comments = booking.comments,
            emp_id = booking.emp_id,
        )

        return booking_data

    def __build_customer_out_payload(self, booking: Row)->schemas.CustomerOut:
        '''
        Builds the CustomerOut payload
        
        Args:
            booking: (models.Booking) The booking object containing the customer details.

        '''
        # Get the customer_id from the booking
        customer_id: int = booking._mapping["Booking"].customer_id
        # Use the get_customer method to get the customer details
        customer: Customer = Customer(self.db)
        result: schemas.CustomerOut = customer.get_customer(customer_id)

        return result

    def __init__(self, db: Session):
        self.db = db

    def __get_customer_id(self, phone: string, email: EmailStr) -> int | None:
            '''
            Check if a customer exists in the database based on their phone number or email.

            Args:
                phone (string): The phone number of the customer.
                email (EmailStr): The email address of the customer.

            Returns:
                int | None: The customer ID if the customer exists in the database, None otherwise.
            '''
            customer: Customer = Customer(self.db)
            # Try to locate the customer with phone number
            result: schemas.CustomerOut|None = customer.get_customer(phone)
            if result:
                return result.customer_id
            cust_id: schemas.CustomerOut|None = customer.get_customer(email)
            if result:
                return result.customer_id

    def __get_supported_booking_statuses_with_id(self) -> List[Row]:
        '''
        Returns the supported room states with their IDs.

        Returns:
            list: A list of supported room states with their IDs.
        '''
        stmt = select(models.BookingStatus)
        result: list[Row] = self.db.execute(stmt).fetchall()
        return result


    def __check_room_availability(self, Payload: schemas.BookingIn) -> int | None:
        """
        Check if the room is available for booking.

        Args:
            Payload (schemas.BookingIn): The booking payload containing room information.

        Returns:
            None

        Raises:
            valueError: If the room is not available for booking.
            cloudbeds_exceptions.DBError: If the database operation fails.
        """
        try:
            # Check if the room is availabel for booking.
            # The room availability information is calculated based on the Bookings table.
            # If the room is already booked for the specified dates, it is not available for booking.
            
            # Get the room_id from the rooms table
            stmt: Select = Select(models.Room)  \
                            .where(models.Room.room_number == Payload.booking.room_num)
            result: list[models.Room] = self.db.execute(stmt).fetchone()
            room_id: int = result[0].room_id

            # Check if the room is available for booking
            stmt: Select = Select(models.Booking)  \
                            .where(models.Booking.room_id == room_id)  \
                            .where(models.Booking.checkin <= Payload.booking.checkout)  \
                            .where(models.Booking.checkout >= Payload.booking.checkin) \
                            .where(
                                or_(models.Booking.booking_status_id == 2, 
                                    models.Booking.booking_status_id == 3
                                    )
                            )
            result: list[models.Booking] = self.db.execute(stmt).fetchone()
            if result:
                raise ValueError("The room is not available for booking.")
            return room_id
        except Exception as e:
            traceback.print_exc()
            match e.__class__.__name__:
                case "ValueError":
                    raise ValueError(e)
                case _:
                    raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}:DB operation failed.")

    def __validate_booking_dates(self, payload: schemas.BookingIn) -> None:
        """
        Validates the booking dates to ensure they are valid and ahead of the booked_on time.

        Args:
            payload (schemas.BookingIn): The booking payload containing booking details.

        Returns:
            None

        Raises:
            ValueError: If the booking dates are not valid or ahead of the booked_on date.
        """
        # Check if the booking_start and booking_end dates are ahead of the booked_on date.
        # booked_on: date = datetime.strptime(payload.booking.booked_on, "%Y-%m-%d").date()
        booked_on: datetime = payload.booking.booked_on
        checkin: date = payload.booking.checkin
        checkout: date = payload.booking.checkout
        if booked_on.date() > checkin or booked_on.date() > checkout:
            # Get system's local timezone
            local_timezone = tz.tzlocal()
            raise ValueError(f"The booking dates should be ahead of the booked on date ({booked_on.replace(tzinfo=local_timezone)}).")
        if checkin > checkout:
            raise ValueError("The booking start date should be ahead of the booking end date.")

    def __validate_govt_id(self, payload: schemas.BookingIn) -> int:
        """
        Validates the government ID type and expiry date of the provided governmtnt ID for a booking.

        Args:
            payload (schemas.BookingIn): The payload containing booking details.

        Returns:
            int: The government ID type ID.

        Raises:
            ValueError: If the supplied government ID type is not valid or if the government ID expiry date is not ahead of the booking start date.
        """
        # Check if the supplied govt_id_type is valid
        try:
            stmt: Select = Select(models.GovtIdType).where(models.GovtIdType.name == payload.booking.government_id_type)
            result: list[models.GovtIdType]|None = self.db.execute(stmt).fetchone()
            if result == None:
                raise ValueError(f"{payload.booking.government_id_type} is not a valid government ID type.")
            # Check if the govt_id_expiry_date is ahead of the booking_start date
            govt_id_expiry_date: date | None = payload.booking.exp_date
            # The government ID should have at least 6 months validity on checkout date
            if govt_id_expiry_date == None:
                return result[0].id
            if govt_id_expiry_date < payload.booking.checkout + timedelta(days=180):
                raise ValueError("The government ID should have at least 6 months validity on checkout date.")
            return result[0].id
        except Exception as e:
            traceback.print_exc()
            match e.__class__.__name__:
                case "ValueError":
                    raise ValueError(e)
                case _:
                    raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}:DB operation failed.")

    def add_supported_govt_id_type(self, payload: schemas.GovtIdTypeBase) -> schemas.GenericMessage:
        '''
        Adds a supported government ID type to the database.

        Args:
            payload: (schemas.GovtIdTypeIn) The government ID type to be added.

        Returns:
            schemas.GenericMessage: A message indicating the success or failure of the operation.

        Raises:
            ValueError: If the govt_id_type already exists in the database.
            CloudBedsError: If the operation fails due to an unknown error.
        '''
        try:
            # Check if the supplied govt_id_type is available in DB. If yes, raise ValueError
            stmt: Select = Select(models.GovtIdType).where(models.GovtIdType.name == payload.name)
            result: Row|None = self.db.execute(stmt).fetchone()
            if result:
                raise ValueError(f"GovtIdType: {payload.name} exists in the database.")
            stmt: Insert =  Insert(models.GovtIdType).values(name=payload.name)
            self.db.execute(stmt)
            self.db.commit()
            return {"msg":"Success"}
        except Exception as e:
            traceback.print_exc()
            match e.__class__.__name__:
                case "ValueError":
                    # Raise value error with same message as before
                    raise ValueError(e)
                case _:
                    raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}:DB operation failed.")

    def get_supported_govt_id_types(self) -> list[schemas.GovtIdTypeBase]:
        """
        Retrieves the supported government ID types from the database.

        Returns:
            A dictionary containing the supported government ID types.

        Raises:
            ValueError: If no supported government ID types are found in the database.
            cloudbeds_exceptions.DBError: If a database operation fails.
        """
        try:
            stmt: Select = Select(models.GovtIdType.name)
            result: List[Row]|None = self.db.execute(stmt).fetchall()
            if result == None:
                raise ValueError("No supported government ID types found in the database.")
            
            supported_ID_types: list[schemas.GovtIdTypeBase] = [schemas.GovtIdTypeBase(name=row.name) for row in result]
            return supported_ID_types
        except Exception as e:
            traceback.print_exc()
            match e.__class__.__name__:
                case "ValueError":
                    raise ValueError(e)
                case _:
                    raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}:DB operation failed.")

    def add_booking(self, payload: schemas.BookingIn) -> schemas.BookingResult:
        
        try:
            # Validate the booking dates
            self.__validate_booking_dates(payload)
            # Validate the government ID
            govt_id_type: int = self.__validate_govt_id(payload)
            # Check if the room is available for booking
            room_id: int = self.__check_room_availability(payload)
            
            # If customer exists in DB, get the customer_ID, else create customer
            cust_id: int|None = self.__get_customer_id(payload.customer.customer_details.phone, payload.customer.customer_details.email)

            if cust_id:
                # Check if the provided customer address available in DB. If not, add it.
                # [FIXME]: Implement support for multiple customer addresses
                pass

            if cust_id == None:
                # Customer doesn't exist in DB. Let's add the customer to DB.
                customer: Customer = Customer(self.db)
                result: schemas.CreateCustomerResult = customer.add_customer(payload.customer)
                cust_id = result.customer_id  

            # Verify employee_id
            employee: schemas.EmployeeOut|None = get_employee(payload.booking.emp_id,db=self.db)
            if employee == None:
                raise ValueError("Invalid employee ID.")
            
            # Check is the employee is active
            if employee.emp_details.is_active == False:
                raise ValueError("The employee is not active.")
            
            # Create booking in DB
            # booking_id is added through a trigger
            # If the booking was created successfully, set the booking_status == 2 (Confirmed)
            stmt: Insert = Insert(models.Booking) \
                            .values(customer_id= cust_id,   
                                    booked_on = payload.booking.booked_on,   
                                    checkin = payload.booking.checkin,
                                    checkout = payload.booking.checkout,
                                    govt_id_type_id = govt_id_type,
                                    govt_id_num = payload.booking.government_id_number,
                                    exp_date = payload.booking.exp_date,
                                    govt_id_img = payload.booking.govt_id_image,
                                    room_id = room_id,
                                    comments = payload.booking.comments,
                                    emp_id = payload.booking.emp_id
                                    )
            
            booking_result: ResultProxy = self.db.execute(stmt)
            # Retrieve the booking_id by refreshing the booking object
            id: int = booking_result.inserted_primary_key[0]
            self.db.commit()

            # Update the status of the Booking to Booked    
            booking_statuses: list[Row] = self.__get_supported_booking_statuses_with_id()
            booked_status_id: int = [row.BookingStatus.id for row in booking_statuses if row.BookingStatus.name.lower() == "booked"][0]
            
            stmt: Update = Update(models.Booking) \
                            .where(models.Booking.id == id) \
                            .values(booking_status_id=booked_status_id)
            self.db.execute(stmt)
            self.db.commit()

            # Use the id (primary key) to fetch the booking_id
            stmt: Select = Select(models.Booking).where(models.Booking.id == id)
            result: list[models.Booking] = self.db.execute(stmt).fetchone()
            booking_id: int = result[0].booking_id
            booking_result: schemas.BookingResult = schemas.BookingResult(booking_id=booking_id, msg="Success")  
            return booking_result
        except Exception as e:
            traceback.print_exc()
            match e.__class__.__name__:
                case "ValueError":
                    raise ValueError(e)
                case _:
                    raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}:DB operation failed.")

    def list_bookings(self, skip: int, limit: int, booking_id: int|None = None) -> List[schemas.BookingOut]:
        """
        Retrieves a list of bookings from the database.

        Args:
            skip (int): The number of records to skip.
            limit (int): The maximum number of records to return.
            booking_id (int, optional): The booking ID to filter by. Defaults to None.

        Returns:
            List[schemas.BookingOut]: A list of bookings.

        Raises:
            ValueError: If the booking ID doesn't exist in the database.
            cloudbeds_exceptions.DBError: If the database operation fails.
        """
        try:
            # Get the list of bookings
            if booking_id:
                stmt: Select = Select(models.Booking).where(models.Booking.booking_id == booking_id)
            else:
                stmt: Select = Select(models.Booking).limit(limit).offset(skip)
            
            result: List[Row] = self.db.execute(stmt).fetchall()
            
            if result == None:
                raise ValueError("No bookings found in the database.")

            # Build the BookingOut payload
            cb_booking: Row
            bookings: list[schemas.BookingOut] = []
            for cb_booking in result:
                customer: schemas.CustomerOut = self.__build_customer_out_payload(cb_booking)
                booking_data: schemas.BookingBase = self.__build_booking_base_payload(cb_booking.Booking)
                booking_id = cb_booking.Booking.booking_id
                bookings.append(schemas.BookingOut(booking_id=booking_id, customer=customer, booking=booking_data))

            return bookings

        except Exception as e:
            traceback.print_exc()
            match e.__class__.__name__:
                case "ValueError":
                    raise ValueError(e)
                case _:
                    raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}:DB operation failed.")            

    def update_booking(self, booking_id: str, payload: schemas.BookingIn) -> schemas.GenericMessage:
        """
        Updates a booking in the database.

        Note: This method doesn't updat the cuatomer details. If you want to update the customer details, use the update_customer method.

        Args:
            booking_id (str): The booking ID to update.
            payload (schemas.BookingIn): The booking data to be updated.

        Returns:
            schemas.GenericMessage: A message indicating the success or failure of the operation.

        Raises:
            ValueError: If the booking ID doesn't exist in the database.
            cloudbeds_exceptions.DBError: If the database operation fails.
        """
        try:
            # Check if the booking exists in the DB.
            stmt: Select = Select(models.Booking).where(models.Booking.booking_id == booking_id)
            result: Row|None = self.db.execute(stmt).fetchone()
            if result == None:
                raise ValueError("Booking doesn't exist in the database.")

            # Validate the booking dates
            self.__validate_booking_dates(payload)
            # Validate the government ID
            govt_id_type: int = self.__validate_govt_id(payload)
            # Check if the room is available for booking
            room_id: int = self.__check_room_availability(payload)
            
            # If customer exists in DB, get the customer_ID, else create customer
            cust_id: int|None = self.__get_customer_id(payload.customer.customer_details.phone, payload.customer.customer_details.email)

            # Verify employee_id
            employee: schemas.EmployeeOut|None = get_employee(payload.booking.emp_id,db=self.db)
            if employee == None:
                raise ValueError("Invalid employee ID.")
            
            # Check is the employee is active
            if employee.emp_details.is_active == False:
                raise ValueError("The employee is not active.")
            
            # Update booking in DB
            stmt: Update = Update(models.Booking) \
                            .where(models.Booking.booking_id == booking_id) \
                            .values(customer_id= cust_id,
                                    booked_on = payload.booking.booked_on,   
                                    checkin = payload.booking.checkin,
                                    checkout = payload.booking.checkout,
                                    govt_id_type_id = govt_id_type,
                                    govt_id_num = payload.booking.government_id_number,
                                    exp_date = payload.booking.exp_date,
                                    govt_id_img = payload.booking.govt_id_image,
                                    room_id = room_id,
                                    comments = payload.booking.comments,
                                    emp_id = payload.booking.emp_id
                                    )
                        
            booking_result: ResultProxy = self.db.execute(stmt)
            self.db.commit()
            return {"msg":"Success"}
        except Exception as e:
            traceback.print_exc()
            match e.__class__.__name__:
                case "ValueError":
                    raise ValueError(e)
                case _:
                    raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}:DB operation failed.")

    def cancel_booking(self, booking_id: str) -> schemas.GenericMessage:
        '''
        Cancels the specified booking.

        Args:
            booking_id (str): The booking ID to cancel.

        Returns:
            schemas.GenericMessage: A message indicating the success or failure of the operation.

        Raises:
            ValueError: If the booking ID doesn't exist in the database.
            cloudbeds_exceptions.DBError: If the database operation fails.
        '''
        try:
            # Check if the booking exists in the DB.
            booking: list[schemas.BookingOut] = self.list_bookings(skip=None, limit=None, booking_id=booking_id)

            if booking == []:
                raise ValueError("Booking doesn't exist in the database.") 
            
            # Update the booking status to cancelled
            stmt: Update = Update(models.Booking) \
                            .where(models.Booking.booking_id == booking_id) \
                            .values(booking_status_id = 5)
            #booking_result: ResultProxy =             
            self.db.execute(stmt)
            self.db.commit()
            return {"msg":"Success"}
        except Exception as e:
            traceback.print_exc()
            match e.__class__.__name__:
                case "ValueError":
                    raise ValueError(e)
                case _:
                    raise cloudbeds_exceptions.DBError(f"{e.__class__.__name__}:DB operation failed.")