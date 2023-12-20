from sqlalchemy import Boolean, ForeignKey, Integer, String, DateTime, CheckConstraint, and_
from sqlalchemy.orm import relationship, Mapped, mapped_column
from .database import Base
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash


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
    #address_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("AddressTypes.address_type_id"))    

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
    room_num: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    # Foreign keys
    r_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("RoomTypes.id"))
    state_id: Mapped[int] = mapped_column(Integer, ForeignKey("RoomStates.id"))

    # Define the back-reference to the RoomType and RoomState models
    room_type: Mapped[RoomType] = relationship('RoomType', back_populates='rooms', foreign_keys=[r_type_id])
    room_state: Mapped[RoomState] = relationship('RoomState', back_populates='rooms', foreign_keys=[state_id])
