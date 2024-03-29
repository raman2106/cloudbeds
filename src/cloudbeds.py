
from fastapi import FastAPI, Depends, HTTPException
from typing import List
from utils import models, schemas, crud
from utils.database import SessionLocal, engine
from sqlalchemy.orm.session import Session
from werkzeug.security import generate_password_hash

#Used in Test endpoints
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



#==========================
# Admin endpoints
#==========================

#==========================
# Employee endpoints
#==========================

# Create operations
@api.post("/emp/add/", 
          name="Add Employee",
          response_model=schemas.EmployeePasswordOut,
          tags=["Employee"],
          description='''Creates an employee record in the database.
          If the provided email exists in the database, returns HTTP 404.''')
#FIXME: Implement multiple addresses support (correspondence and permanent)
#FIXME: Implement callback URL
async def add_employee(payload: schemas.EmployeeIn, db: Session = Depends(get_db)):
    employee: schemas.EmployeeOut|None = crud.get_employee(payload.emp_details.email, db)
    if employee:
        raise HTTPException(status_code=400, detail="Email already registered.")
    result: schemas.EmployeePasswordOut = crud.create_employee(payload, db)
    return result
# Read operations
@api.get("/get_emp/",
         name="Get Employee",
         response_model=schemas.EmployeeOut,
         tags=["Employee"],
         description= '''Returns the details of an employee for the provided employee id or email. 
         If employee isn't found in the database, it returns HTTP 404.'''
         )
async def get_employee(id: int|EmailStr,  db: Session = Depends(get_db)):
    employee: schemas.Employee|None = crud.get_employee(id, db)
    if employee:
        return employee
    else:
        if type(id) == int:
            raise HTTPException(status_code=404, detail="Invalid employee ID.")
        else:
            raise HTTPException(status_code=404, detail="Email isn't registered.")

@api.get("/emp/list/",
         name="List Employees",
         response_model=List[schemas.EmployeeOut],
         tags=["Employee"],
         description= '''Returns the list of all employees from the database.
         If the database is empty, it returns HTTP 404.'''
         )
async def list_employee(db: Session = Depends(get_db), skip: int = 0, limit: int = 20):
    employees: List[schemas.EmployeeOut]|None = crud.list_employees(db, skip, limit)
    if employees:
        return employees
    else:
        raise HTTPException(status_code=404, detail="There are no employees in the database.")        

# Update operations
@api.put("/emp/password_reset/{emp_id}",
         name="Reset Employee Password",
         response_model=schemas.EmployeePasswordOut,
         tags=["Employee"],
         description= '''Resets the password of the specified employee. 
         If employee ID isn't found in the database, it returns HTTP 404.'''
         )
async def reset_password(emp_id: int, db: Session = Depends(get_db)):
    employee: schemas.EmployeeOut|None = crud.get_employee(emp_id, db)
    if employee:
        result: schemas.EmployeePasswordOut = crud.reset_password(emp_id, db)        
        return result
    else:
        raise HTTPException(status_code=400, detail="Provided employee ID doesn't exist.")

@api.put("/emp/manage/{emp_id}",
         name="Manage employee",
         response_model=schemas.ManageEmployeeOut,
         tags=["Employee"],
         description= '''Sets the activation status of the specified employee. 
         If employee ID isn't found in the database, it returns HTTP 404.'''
         )
async def manage_employee(emp_id: int, is_active: bool, db: Session = Depends(get_db)):
    employee: schemas.EmployeeOut|None = crud.get_employee(emp_id, db)
    if employee:
        result: schemas.ManageEmployeeOut = crud.manage_employee(emp_id, is_active, db)        
        return result
    else:
        raise HTTPException(status_code=400, detail="Provided employee ID doesn't exist.")





#==========================
# Room endpoints
#==========================

@api.delete("/room_types/delete/{room_type}",
            name="Delete Room Type",
            response_model=schemas.GenericMessage,
            description='''Deletes the specified room type from the database.
            If the room type isn't found in the database, it returns HTTP 400.''',
            tags=["Room"]
            )
async def delete_room_type(room_type: str, db: Session = Depends(get_db)):
    room: crud.Room = crud.Room(db)
    try:
        result: schemas.GenericMessage = room.manage_room_types("delete", room_type)
        return result
    except Exception as e:
        match e.__class__.__name__:
            case "ValueError":
                raise HTTPException(status_code=400, detail=str(e.__str__()))
            case _:
                raise HTTPException(status_code=500, detail=str(e.__str__()))

@api.delete("/room_states/delete/{room_state}",
            name="Delete Room State",
            response_model=schemas.GenericMessage,
            description='''Deletes the specified room state from the database.
            If the room state isn't found in the database, it returns HTTP 400.''',
            tags=["Room"]
            )
async def delete_room_state(room_state: str, db: Session = Depends(get_db)):
    room: crud.Room = crud.Room(db)
    try:
        result: schemas.GenericMessage = room.manage_room_states("delete", room_state)
        return result
    except Exception as e:
        match e.__class__.__name__:
            case "ValueError":
                raise HTTPException(status_code=400, detail=str(e.__str__()))
            case _:
                raise HTTPException(status_code=500, detail=str(e.__str__()))            

@api.delete("/room/delete/{room_number}",
            name="Delete Room",
            response_model=schemas.GenericMessage,
            tags=["Room"],
            description='''Deletes the specified room from the database.
            If the room isn't found in the database, it returns HTTP 400.''',
            )
async def delete_room(room_number: str, db: Session = Depends(get_db)):
    room: crud.Room = crud.Room(db)
    try:
        result: schemas.GenericMessage = room.delete_room(room_number)
        return result
    except Exception as e:
        match e.__class__.__name__:
            case "ValueError":
                raise HTTPException(status_code=400, detail=str(e.__str__()))
            case _:
                raise HTTPException(status_code=500, detail=str(e.__str__()))

@api.get("/room/list/",
    name="List Rooms",
    response_model=List[schemas.RoomBase],
    tags=["Room"],
    description= '''Returns the list of rooms from the database that match the criteria specified in the payload.
    If the database is empty, it returns HTTP 404.'''
    )
async def list_rooms(db: Session = Depends(get_db), \
                     room_number: str | None = None, \
                     room_type: str | None = None, \
                     room_state: str | None = None, \
                     skip: int | None = None, \
                     limit: int | None = None):
    """
    Retrieve the list of all rooms from the database.

    Parameters:
    - db (Session): The database session.
    - skip (int, optional): The number of rooms to skip. Defaults to 0.
    - limit (int, optional): The maximum number of rooms to retrieve. Defaults to 20.
    - room_number (str, optional): The room number filter. Defaults to None. 
                                    -   If room_number is None, it returns all rooms.
                                    -   If room_number is a string, it returns all other optional parameters 
                                        are ignored and the endpoint returns the room with the specified room number.
    - room_type (str, optional): The room type filter. Defaults to None.
    - room_state (str, optional): The room state filter. Defaults to None.

    Returns:
    - List[schemas.RoomBase] | None: A list of rooms matching the specified filters.

    Raises:
    - HTTPException with status code 404 if there are no rooms in the database.
    - HTTPException with status code 400 if a ValueError occurs.
    - HTTPException with status code 500 for any other exception.
    """
    room: crud.Room = crud.Room(db)
    try:
        rooms: List[schemas.RoomBase] = room.list_rooms(skip, limit, room_number, room_type, room_state)
        return rooms
    except Exception as e:
        match e.__class__.__name__:
            case "ValueError":
                    raise HTTPException(status_code=400, detail=str(e.__str__()))
            case _:
                    raise HTTPException(status_code=500, detail=str(e.__str__()))
            
@api.get("/room_types/list",
         name="List Room Types",
         response_model=schemas.RoomTypeBase,
         tags=["Room"],
         description= '''Returns the list of all room types from the database.
         If the database is empty, it returns HTTP 404.'''
         )
async def list_room_types(db: Session = Depends(get_db)):
    room: crud.Room = crud.Room(db)
    room_types: schemas.RoomTypeBase|None = room.get_supported_room_types()
    if room_types:
        return room_types
    else:
        raise HTTPException(status_code=404, detail="There are no room types in the database.")

@api.get("/room_states/list/",
            name="List Room States",
            response_model=schemas.RoomStateBase,
            tags=["Room"],
            description= '''Returns the list of all room states from the database.
            If the database is empty, it returns HTTP 404.'''
            )
async def list_room_states(db: Session = Depends(get_db)):
    room: crud.Room = crud.Room(db)
    room_states: schemas.RoomStateBase|None = room.get_supported_room_states()
    if room_states:
        return room_states
    else:
        raise HTTPException(status_code=404, detail="There are no room states in the database.")

@api.post("/room/add/",
          name="Add Room",
          response_model=schemas.GenericMessage,
          tags=["Room"],
          description='''Adds a new room to the database. 
          If the room number already exists, it returns HTTP 400.'''
          )
async def add_room(payload: schemas.RoomBase, db: Session = Depends(get_db)):
    room: crud.Room = crud.Room(db)
    try:
        result: schemas.GenericMessage = room.add_room(room_number=payload.room_number, room_type=payload.room_type, room_state=payload.room_state)
        return result
    except Exception as e:
        match e.__class__.__name__:
            case "ValueError":
                raise HTTPException(status_code=400, detail=str(e.__str__()))
            case _:
                raise HTTPException(status_code=500, detail=str(e.__str__()))

@api.post("/room_types/add/",
          name="Add Room Type",
          response_model=schemas.GenericMessage,
          tags=["Room"],
          description='''Adds a new room type to the database. 
          If the room type already exists, it returns HTTP 400.'''
          )
async def add_room_type(payload: schemas.RoomTypeIn, db: Session = Depends(get_db)):
    room: crud.Room = crud.Room(db)
    try:
        result: schemas.GenericMessage = room.manage_room_types("add", payload.room_type)
        return result
    except Exception as e:
        match e.__class__.__name__:
            case "ValueError":
                raise HTTPException(status_code=400, detail=str(e.__str__()))
            case _:
                raise HTTPException(status_code=500, detail=str(e.__str__()))

@api.post("/room_states/add/",
          name="Add Room State",
          response_model=schemas.GenericMessage,
          tags=["Room"],
          description='''Adds a new room state to the database. 
          If the room state already exists, it returns HTTP 400.'''
          )
async def add_room_state(payload: schemas.RoomTypeIn, db: Session = Depends(get_db)):
    room: crud.Room = crud.Room(db)
    try:
        result: schemas.GenericMessage = room.manage_room_states("add", payload.room_type)
        return result
    except Exception as e:
        match e.__class__.__name__:
            case "ValueError":
                raise HTTPException(status_code=400, detail=str(e.__str__()))
            case _:
                raise HTTPException(status_code=500, detail=str(e.__str__()))

@api.put("/room/update/",
            name="Update Room",
            response_model=schemas.GenericMessage,
            tags=["Room"],
            description='''Updates the specified room.
            If the room number doesn't exists, it returns HTTP 400.'''
            )
async def update_room(payload: schemas.RoomBase, db: Session = Depends(get_db)):
    room: crud.Room = crud.Room(db)
    try:
        result: schemas.GenericMessage = room.update_room(payload.room_number, payload.room_type, payload.room_state)
        return result
    except Exception as e:
        match e.__class__.__name__:
            case "ValueError":
                raise HTTPException(status_code=400, detail=str(e.__str__()))
            case _:
                raise HTTPException(status_code=500, detail=str(e.__str__()))   

@api.put("/room_types/update/",
         name="Update Room Type",
         response_model=schemas.GenericMessage,
         tags=["Room"],
         description='''Updates the specified room type.
         If the room state doesn't exists, it returns HTTP 400.'''
         ) 
async def update_room_type(room_type: str, new_room_type: str, db: Session = Depends(get_db)):
    room: crud.Room = crud.Room(db)
    try:
        result: schemas.GenericMessage = room.manage_room_types("update", room_type, new_room_type)
        return result
    except Exception as e:
        match e.__class__.__name__:
            case "ValueError":
                raise HTTPException(status_code=400, detail=str(e.__str__()))
            case _:
                raise HTTPException(status_code=500, detail=str(e.__str__()))

@api.put("/room_states/update/",
            name="Update Room State",
            response_model=schemas.GenericMessage,
            tags=["Room"],
            description='''Updates the specified room state.
            If the room state doesn't exists, it returns HTTP 400.'''
            )
async def update_room_state(room_state: str, new_room_state: str, db: Session = Depends(get_db)):
    room: crud.Room = crud.Room(db)
    try:
        result: schemas.GenericMessage = room.manage_room_states("update", room_state, new_room_state)
        return result
    except Exception as e:
        match e.__class__.__name__:
            case "ValueError":
                raise HTTPException(status_code=400, detail=str(e.__str__()))
            case _:
                raise HTTPException(status_code=500, detail=str(e.__str__()))

#=============================
# Front-desk Manager endpoints
#=============================


if __name__ == "__main__":
    # USed to run the code in debug mode.
    uvicorn.run(api, host="0.0.0.0", port=8000)