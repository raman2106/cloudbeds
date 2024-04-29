# Cloudbeds creation DDL:../../create-tables-1.sql
from sqlalchemy import Boolean, ForeignKey, Integer, String, DateTime, CheckConstraint, Date, BLOB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .database import Base
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Customer(Base):
    __tablename__ = "Customers"        
    customer_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(20), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(20), nullable=True)
    last_name: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    
    # Define the relationship to the EmployeeAddress model
    addresses: Mapped[list["CustomerAddress"]] = relationship("CustomerAddress", back_populates="customer")

    # Define the relationship to the Booking model
    booking: Mapped[list["Booking"]] = relationship("Booking", back_populates="customer")

class CustomerAddress(Base):
    __tablename__ = "CustomerAddresses"
    address_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    address_type: Mapped[str] = mapped_column(String(20))
    first_line: Mapped[str] = mapped_column(String(30), nullable=False)
    second_line: Mapped[str] = mapped_column(String(30), nullable=False)
    landmark: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    district: Mapped[str] = mapped_column(String(30), nullable=False)
    state: Mapped[str] = mapped_column(String(20), nullable=False)
    pin: Mapped[str] = mapped_column(String(10), nullable=False)

    # Foreign keys
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("Customers.customer_id"))

    # Define the back-reference to the Employee model
    customer: Mapped[Customer] = relationship('Customer', back_populates='addresses')    

    # Constraint to check the address type
    __table_args__ = (
        CheckConstraint(
            address_type.in_(['Correspondence', 'Permanent']),
            name='chk_address_type'
        ),
    )    

class Employee(Base):
    __tablename__ = "Employees"
    # An employee can have many addresses (one permanent and one temporary)
    emp_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    first_name: Mapped[str] = mapped_column(String(20))
    middle_name: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    last_name: Mapped[str] = mapped_column(String(20))    
    email: Mapped[str] = mapped_column(String(40), unique=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    password_hash: Mapped[str] = mapped_column(String(255))
    last_login_at: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    current_login_at:Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    last_login_ip:Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    current_login_ip:Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    login_count: Mapped[Optional[str]] = mapped_column(Integer, nullable=True)
    
    # Attributes used in relationships
    addresses: Mapped[list["EmployeeAddress"]] = relationship("EmployeeAddress", back_populates="employee")
    roles: Mapped[list["EmployeeRole"]] = relationship("EmployeeRole", back_populates="employee")
    # Define the relationship to the Booking model
    booking: Mapped[list["Booking"]] = relationship("Booking", back_populates="employee")

    # Info on password hashing:
    # https://dev.to/kaelscion/authentication-hashing-in-sqlalchemy-1bem
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class EmployeeAddress(Base):
    __tablename__ = "EmployeeAddresses"
    # address_id holds a many-to-one relationship with AddressType.address_type_i
    address_id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)

    # Foreign keys
    emp_id: Mapped[int] = mapped_column(Integer, ForeignKey("Employees.emp_id"))

    first_line: Mapped[str] = mapped_column(String(60))
    second_line: Mapped[Optional[str]] = mapped_column(String(60))
    landmark: Mapped[Optional[str]] = mapped_column(String(30))
    district: Mapped[str] = mapped_column(String(30))
    state: Mapped[str] = mapped_column(String(20))
    pin: Mapped[str] = mapped_column(String(10))
    address_type: Mapped[str] = mapped_column(String(20))

    # Define the back-reference to the Employee model
    employee: Mapped[Employee] = relationship('Employee', back_populates='addresses')

    # Constraint to check the address type
    __table_args__ = (
        CheckConstraint(
            address_type.in_(['Correspondence', 'Permanent']),
            name='chk_address_type'
        ),
    )


class Role(Base):
    __tablename__ = "Roles"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(45), nullable=False)
    permissions: Mapped[str] = mapped_column(String(255), nullable=False)

    employees: Mapped[list["EmployeeRole"]] = relationship("EmployeeRole", back_populates="role")

class EmployeeRole(Base):
    __tablename__ = "EmployeeRoles"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    emp_id: Mapped[int] = mapped_column(Integer, ForeignKey("Employees.emp_id"))
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("Roles.id"))

    # Define the back-reference to the Employee model
    employee: Mapped[Employee] = relationship('Employee', back_populates='roles')
    # Define the back-reference to the Role model
    role: Mapped[Role] = relationship('Role', back_populates='employees')



class RoomType(Base):
    __tablename__ = "RoomTypes"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    room_type: Mapped[str] = mapped_column(String(45), nullable=False)

    # Attributes used in relationships
    rooms: Mapped[list["Room"]] = relationship("Room", back_populates="room_type")

class RoomState(Base):
    __tablename__ = "RoomStates"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    room_state: Mapped[str] = mapped_column(String(15), nullable=False)

    # Attributes used in relationships
    rooms: Mapped[list["Room"]] = relationship("Room", back_populates="room_state")

class Room(Base):
    __tablename__ = "Rooms"
    room_id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    room_number: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    # Foreign keys
    r_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("RoomTypes.id"))
    state_id: Mapped[int] = mapped_column(Integer, ForeignKey("RoomStates.id"))

    # Define the back-reference to the RoomType and RoomState models
    room_type: Mapped[RoomType] = relationship('RoomType', back_populates='rooms', foreign_keys=[r_type_id])
    room_state: Mapped[RoomState] = relationship('RoomState', back_populates='rooms', foreign_keys=[state_id])

    # Define the relationship to the Booking model
    booking: Mapped[list["Booking"]] = relationship("Booking", back_populates="room")

class GovtIdType(Base):
    __tablename__ = "GovtIdTypes"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)

    # Define the relationship to the Booking model
    booking: Mapped[list["Booking"]] = relationship("Booking", back_populates="govt_id_type")

class BookingStatus(Base):
    __tablename__ = "BookingStatuses"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)

    # Define the relationship to the Booking model
    booking: Mapped[list["Booking"]] = relationship("Booking", back_populates="booking_status")

class Booking(Base):
    __tablename__ = "Bookings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    booking_id: Mapped[str] = mapped_column(String(20), nullable=False, autoincrement=False)
    booked_on: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    checkin: Mapped[Date] = mapped_column(Date, nullable=False)
    checkout: Mapped[Date] = mapped_column(Date, nullable=False)
    govt_id_num: Mapped[str] = mapped_column(String(20), nullable=False)
    exp_date: Mapped[Optional[Date]] = mapped_column(Date, nullable=True)
    govt_id_img: Mapped[Optional[BLOB]] = mapped_column(BLOB, nullable=True)
    comments: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Foreign keys
    booking_status_id: Mapped[int] = mapped_column(Integer, ForeignKey("BookingStatuses.id"), nullable=False, default=1)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("Customers.customer_id"), nullable=False)
    room_id: Mapped[int] = mapped_column(Integer, ForeignKey("Rooms.room_id"))
    govt_id_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("GovtIdTypes.id"))
    emp_id: Mapped[int] = mapped_column(Integer, ForeignKey("Employees.emp_id"))

    # Define the back-reference to the BookingStatus model
    booking_status: Mapped[BookingStatus] = relationship('BookingStatus', back_populates='booking')

    # Define the back-reference to the Customer model
    customer: Mapped[Customer] = relationship('Customer', back_populates='booking')

    # Define the back-reference to the Room model
    room: Mapped[Room] = relationship('Room', back_populates='booking')

    # Define the back-reference to the GovtIdType model
    govt_id_type: Mapped[GovtIdType] = relationship('GovtIdType', back_populates='booking')

    # Define the back-reference to the Employee model
    employee: Mapped[Employee] = relationship('Employee', back_populates='booking')
