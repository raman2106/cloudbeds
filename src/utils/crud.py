from sqlalchemy.orm.session import Session
from . import models, schemas, cloudbeds_exceptions
from pydantic import EmailStr, SecretStr
from sqlalchemy import select, Row, or_, update, Delete, Insert, Select, and_
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

    def _get_supported_room_states_with_id(self) -> List[Row]:
        '''
        Returns the supported room states with their IDs.

        Returns:
            list: A list of supported room states with their IDs.
        '''
        stmt = select(models.RoomState.id, models.RoomState.room_state)
        result: list[Row] = self.db.execute(stmt).fetchall()
        return result

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
            raise ValueError(f"{room_type} doesn't exist in the database.")
        if not self._verify_room_state(room_state):
            raise ValueError(f"{room_state} doesn't exist in the database.")
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
            room_states: list[Row] = self._get_supported_room_states_with_id()
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
                    room_state: (int) = [row.id for row in self._get_supported_room_states_with_id() \
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
            room_states: list[Row] = self._get_supported_room_states_with_id()
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
                        

class Customers:
    pass