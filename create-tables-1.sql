/* 2023, Oct, 03: [RK]: 
Use this script to create the following tables in the content DB
* Employees
* EmployeeAddresses
* AddressTypes
* Roles
* EmployeeRoles
* Customers
* CustomerAddresses
* Bookings
* BookingStatuses
* GovtIdTypes
* Payments
* PaymentMethods
* PaymentStatuses
* Rooms
* RoomTypes
* RoomStates
*/

DROP DATABASE IF EXISTS cloudbeds;
CREATE DATABASE cloudbeds;
USE cloudbeds;

CREATE TABLE Employees (
	emp_id INT NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(20) NOT NULL,
    middle_name VARCHAR(20),
    last_name VARCHAR(20) NOT NULL,
    email VARCHAR(40) UNIQUE,
    phone VARCHAR(20) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT False,
    password_hash VARCHAR(255) NOT NULL,
    last_login_at DATETIME,
    current_login_at DATETIME,
    last_login_ip VARCHAR(45),
    current_login_ip VARCHAR(45),
    login_count INT,
    PRIMARY KEY(emp_id)
);

-- Set the starting value for Employees.emp_id to 1001
ALTER TABLE Employees AUTO_INCREMENT = 1001;
/*
CREATE TABLE AddressTypes(
    address_type_id INT NOT NULL AUTO_INCREMENT,
    description VARCHAR(45) NOT NULL,
    PRIMARY KEY(address_type_id),
    -- Defines the OOB address types
    CONSTRAINT `chk_description`
    CHECK (description IN ('Correspondence', 'Permanent'))
);
*/

CREATE TABLE EmployeeAddresses(
	address_id INT NOT NULL AUTO_INCREMENT,
    -- emp_id has a many-on-1 relationship with Employees.emp_id
    emp_id INT NOT NULL,
    -- address_type_id INT NOT NULL,
    address_type VARCHAR(20) NOT NULL,
    first_line VARCHAR(60) NOT NULL,
    second_line VARCHAR(60),
    landmark VARCHAR(30),
    district VARCHAR(30) NOT NULL,
    state VARCHAR(20) NOT NULL,
    pin VARCHAR(10) NOT NULL,
    PRIMARY KEY(address_id),
	CONSTRAINT `fk_employee_id`
	FOREIGN KEY (`emp_id`)
	REFERENCES `Employees` (`emp_id`),
    CONSTRAINT `chk_address_type`
	CHECK (address_type IN ('Correspondence', 'Permanent'))
);


CREATE TABLE Roles(
	id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(45) NOT NULL UNIQUE,
    -- Stores the tablewise permissions as JSON.
    permissions VARCHAR(255),
    PRIMARY KEY(id)
);

-- Add the OOB AddressTypes in the AddressTypes table
INSERT INTO Roles (name)
VALUES 
	("Admin"), 
	("Front-desk"),
    ("Shift-manager");

CREATE TABLE EmployeeRoles(
	id INT NOT NULL AUTO_INCREMENT,
    emp_id INT NOT NULL,
    role_id INT NOT NULL,
    PRIMARY KEY(id)
);

CREATE TABLE Customers (
	customer_id INT NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(20) NOT NULL,
    middle_name VARCHAR(20),
    last_name VARCHAR(20) NOT NULL,
    email VARCHAR(40),
    phone VARCHAR(20) NOT NULL,
    PRIMARY KEY(customer_id)
);    

CREATE TABLE CustomerAddresses(
	address_id INT NOT NULL AUTO_INCREMENT,
    -- type_id has 1-on-1 relationship with AddressTypes.address_type
    address_type VARCHAR(20) NOT NULL,
    -- customer_id has Customers.customer_id
    customer_id INT NOT NULL,
	first_line VARCHAR(30) NOT NULL,
    second_line VARCHAR(30) NOT NULL,
    landmark VARCHAR(30),
    district VARCHAR(30) NOT NULL,
    state VARCHAR(20) NOT NULL,
    pin VARCHAR(10) NOT NULL,
    PRIMARY KEY(address_id),
    KEY `fk_customer_id` (`customer_id`),
    CONSTRAINT `fk_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `Customers` (`customer_id`),
    CONSTRAINT `chk_customer_address_type` CHECK ((`address_type` IN ('Correspondence','Permanent')))    
);


CREATE TABLE Payments(
	id INT NOT NULL AUTO_INCREMENT,
    pmt_id VARCHAR(45) NOT NULL,
    -- Holds 1-to-1 relationship with Bookings.booking_id
    booking_id VARCHAR(20) NOT NULL,
    -- Holds 1-to-1 relationship with PaymentMethods.method_id
    method_id INT NOT NULL,
    amount FLOAT NOT NULL,
    -- Holds 1-to-1 relationship with PaymentStatuses.status_id
    pmt_status INT,
    PRIMARY KEY (id)
);

CREATE TABLE PaymentMethods(
	method_id INT NOT NULL AUTO_INCREMENT,
    methods VARCHAR(45) NOT NULL,
    PRIMARY KEY(method_id)
);

-- Add default payment methods in the PaymentMethods table
INSERT INTO PaymentMethods (methods)
VALUES 
	("Credit card"),
    ("Debit card"),
    ("UPI"),
    ("Cash");
    
CREATE TABLE PaymentStatuses(
	status_id INT NOT NULL AUTO_INCREMENT,
    pmt_status VARCHAR(10) NOT NULL,
    PRIMARY KEY(status_id)
);   

-- Add default payment statuses in the PaymentMethods table
INSERT INTO PaymentStatuses (pmt_status)
VALUES 
	("Successful"),
    ("Failed"),
    ("Reverted");
    
CREATE TABLE BookingStatuses(
	id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(20) NOT NULL,
    PRIMARY KEY(id)
);

-- Add default booking states in the BookingStatuses table
INSERT INTO BookingStatuses (name)
VALUES 
	("Unconfirmed"),
    ("Booked"),
    ("Ongoing"),
    ("Complete"),
    ("Cancelled");
    
CREATE TABLE GovtIdTypes(
	id INT NOT NULL AUTO_INCREMENT,
    name VARCHAR(45) NOT NULL,
    PRIMARY KEY(id)
);

-- Add default government ID types in the GovtIdTypes table
INSERT INTO GovtIdTypes (name)
VALUES 
	("AADHAR"),
    ("PAN"),
    ("Voter ID"),
    ("Driving License"),
    ("Passport");
    
CREATE TABLE RoomTypes(
	id INT NOT NULL AUTO_INCREMENT,
    room_type VARCHAR(45) NOT NULL,
    PRIMARY KEY(id),
    UNIQUE (`room_type`)
);

-- Add default room types in the RoomTypes table
INSERT INTO RoomTypes (room_type)
VALUES 
	("Standard"),
    ("Delux"),
    ("Club"),
    ("Suite");
    
CREATE TABLE RoomStates(
	id INT NOT NULL AUTO_INCREMENT,
    room_state VARCHAR(15) NOT NULL,
    PRIMARY KEY(id),
    UNIQUE (`room_state`)
);

-- Add default room states in the RoomStates table
INSERT INTO RoomStates (room_state)
VALUES 
	("Booked"),
    ("Available"),
    ("Maintenance");
    
CREATE TABLE Rooms(
    room_id INT NOT NULL AUTO_INCREMENT,
    room_number INT NOT NULL UNIQUE,
    r_type_id INT NOT NULL,
    state_id INT NOT NULL DEFAULT 1,
    PRIMARY KEY(room_id),
    KEY `fk_r_type_id` (`r_type_id`),
    CONSTRAINT `fk_r_type_id` FOREIGN KEY (`r_type_id`) REFERENCES `RoomTypes` (`id`),
    KEY `fk_state_id` (`state_id`),
    CONSTRAINT `fk_state_id` FOREIGN KEY (`state_id`) REFERENCES `RoomStates` (`id`)
);

CREATE TABLE Bookings(
	id INT NOT NULL AUTO_INCREMENT,
    -- Uses generate_booking_id trigger to generate the booking ID 
	booking_id varchar(20)NOT NULL,
	-- Holds 1-to-1 relationship with Customers.customer_id
	customer_id INT NOT NULL,
    KEY `fk_bk_customer_id` (`customer_id`),
    CONSTRAINT `fk_bk_customer_id` FOREIGN KEY (`customer_id`) REFERENCES `Customers` (`customer_id`),
    booked_on DATETIME NOT NULL,
    checkin DATE NOT NULL,
    checkout DATE NOT NULL,
    booking_status_id INT DEFAULT 1,
    KEY `fk_bk_booking_status_id` (`booking_status_id`),
    CONSTRAINT `fk_bk_booking_status_id` FOREIGN KEY (`booking_status_id`) REFERENCES `BookingStatuses` (`id`),
    govt_id_type INT NOT NULL,
    KEY `fk_bk_govt_id_type` (`govt_id_type`),
    CONSTRAINT `fk_bk_govt_id_type` FOREIGN KEY (`govt_id_type`) REFERENCES `GovtIdTypes` (`id`),    
    govt_id_num VARCHAR(45) NOT NULL,
    -- Government ID expirt date
    exp_date DATE,
    govt_id_img BLOB NULL,
    -- Holds 1-to-1 relationship with Rooms.room_num
    room_id INT NOT NULL,
    KEY `fk_bk_room_id` (`room_id`),
    CONSTRAINT `fk_room_id` FOREIGN KEY (`room_id`) REFERENCES `Rooms` (`room_id`),    
    comments VARCHAR(255),
    -- Holds 1-to-1 relationship with Employees.emp_id
    emp_id INT NOT NULL,
    KEY `fk_bk_emp_id` (`emp_id`),
    CONSTRAINT `fk_bk_emp_id` FOREIGN KEY (`emp_id`) REFERENCES `Employees` (`emp_id`),    
    -- Holds 1-to-1 relationship with CustomerAddresses.address_id
    -- customer_address INT NOT NULL,
    PRIMARY KEY (id)
);

-- Table to store the last used booking id. We need this table to generate realworkd booking IDs
CREATE TABLE BookingIDGenerator (
    last_booking_id INT
);

-- Set the starting value of the booking ID
INSERT INTO BookingIDGenerator (last_booking_id) VALUES (1001);

-- Trigger to generate custom booking IDs
DELIMITER //
CREATE TRIGGER generate_booking_id
BEFORE INSERT ON Bookings
FOR EACH ROW
BEGIN
    DECLARE new_booking_id INT;
    SET new_booking_id = (SELECT last_booking_id + 1 FROM BookingIDGenerator);
    SET NEW.booking_id = CONCAT('B', new_booking_id);
    UPDATE BookingIDGenerator SET last_booking_id = new_booking_id;
END;
//
DELIMITER ;
