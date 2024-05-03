import React, { useEffect, useState, useRef } from 'react';
import {
    FormControl,
    FormLabel,
    Input,
    Box,
    Grid,
    Button,
    Switch,
    Stack,
    Heading,
    RadioGroup,
    Radio,
    Flex,
    ButtonGroup,
    Spacer,
    AlertDialog, 
    AlertDialogBody, 
    AlertDialogFooter, 
    AlertDialogHeader, 
    AlertDialogContent, 
    AlertDialogOverlay,
} from '@chakra-ui/react'

const FormEmployee = () => {
    const authToken = localStorage.getItem('jwt');
    const [employee, setEmployee] = useState({
        emp_details: {
            first_name: "",
            middle_name: "",
            last_name: "",
            email: "",
            phone: "",
            is_active: false
        },
        emp_address: {
            first_line: "",
            second_line: "",
            landmark: "",
            district: "",
            state: "",
            pin: "",
            address_type: "Permanent"
        }
    });

    const [isOpen, setIsOpen] = useState(false);
    const onClose = () => setIsOpen(false);
    const cancelRef = useRef();
    const [dialogMessage, setDialogMessage] = useState("");
    const [dialogTitle, setDialogTitle] = useState("");    

    const handleChange = (e) => {
        const { name, value } = e.target;
        const [section, key] = name.split('.');
        setEmployee(prevState => ({
            ...prevState,
            [section]: {
                ...prevState[section],
                [key]: value
            }
        }));
    };

    const handleSwitchChange = (e) => {
        setEmployee(prevState => ({
            ...prevState,
            emp_details: {
                ...prevState.emp_details,
                is_active: e.target.checked
            }
        }));
    };

    const handleRadioChange = (value) => {
        setEmployee(prevState => ({
            ...prevState,
            emp_address: {
                ...prevState.emp_address,
                address_type: value
            }
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const response = await fetch('http://127.0.0.1:8000/emp/add', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                },
                body: JSON.stringify(employee)
            });
            const data = await response.json();
            if (response.ok) {
                setDialogTitle("Success");
                setDialogMessage(`The employee was created successfully. Notedown the ID and password of the employee. You can't view the password after closing this dialog. \n\nEmployee ID: ${data.emp_id}, \nPassword: ${data.password}`);
            } else {
                throw new Error(data.detail);
            }
        } catch (error) {
            setDialogTitle("Error");
            setDialogMessage(error.message);
        }
        setIsOpen(true);
    };

    return(
        <form onSubmit={handleSubmit}>
            <Box  
                borderRadius="lg" 
                border="1px" 
                borderColor="gray.200"         
                p={4}  
                pl={64}
                ml={40} 
                pt="10"
                m={4}>
                <Flex mb={4}>
                    <Spacer />
                    <FormLabel htmlFor="is_active" mb="0">
                        Is Active
                    </FormLabel>
                    <Switch id="is_active" colorScheme="teal" isChecked={employee.emp_details.is_active} onChange={handleSwitchChange} />
                </Flex>
                <Grid templateColumns="repeat(2, 1fr)" gap={3}>
                    <Box>
                        <Heading as="h2" size="md">Employee Details</Heading>
                        <Stack spacing={1}>
                            <FormControl id="first_name" isRequired>
                                <FormLabel>First Name</FormLabel>
                                <Input type="text" name="emp_details.first_name" value={employee.emp_details.first_name} onChange={handleChange} />
                            </FormControl>
                            <FormControl id="middle_name" defaultValue="">
                                <FormLabel>Middle Name</FormLabel>
                                <Input type="text" name="emp_details.middle_name" value={employee.emp_details.middle_name} onChange={handleChange} />
                            </FormControl>
                            <FormControl id="last_name" isRequired>
                                <FormLabel>Last Name</FormLabel>
                                <Input type="text" name="emp_details.last_name" value={employee.emp_details.last_name} onChange={handleChange} />
                            </FormControl>
                            <FormControl id="email" isRequired>
                                <FormLabel>Email</FormLabel>
                                <Input type="email" name="emp_details.email" value={employee.emp_details.email} onChange={handleChange} />
                            </FormControl>
                            <FormControl id="phone" isRequired>
                                <FormLabel>Phone</FormLabel>
                                <Input type="text" name="emp_details.phone" value={employee.emp_details.phone} onChange={handleChange} />
                            </FormControl>
                        </Stack>
                    </Box>
                    <Box>
                        <Heading as="h2" size="md">Employee's address</Heading>
                        <Stack spacing={1}>
                            <FormControl id="first_line" isRequired>
                                <FormLabel>First Line</FormLabel>
                                <Input type="text" name="emp_address.first_line" value={employee.emp_address.first_line} onChange={handleChange} />
                            </FormControl>
                            <FormControl id="second_line" defaultValue="">
                                <FormLabel>Second Line</FormLabel>
                                <Input type="text" name="emp_address.second_line" value={employee.emp_address.second_line} onChange={handleChange} />
                            </FormControl>
                            <FormControl id="landmark" isRequired>
                                <FormLabel>Landmark</FormLabel>
                                <Input type="text" name="emp_address.landmark" value={employee.emp_address.landmark} onChange={handleChange} />
                            </FormControl>
                            <FormControl id="district" isRequired>
                                <FormLabel>District</FormLabel>
                                <Input type="text" name="emp_address.district" value={employee.emp_address.district} onChange={handleChange} />
                            </FormControl>
                            <FormControl id="state" isRequired>
                                <FormLabel>State</FormLabel>
                                <Input type="text" name="emp_address.state" value={employee.emp_address.state} onChange={handleChange} />
                            </FormControl>
                            <FormControl id="pin" isRequired>
                                <FormLabel>Pin</FormLabel>
                                <Input type="text" name="emp_address.pin" value={employee.emp_address.pin} onChange={handleChange} />
                            </FormControl>
                            <FormControl id="address_type" isRequired>
                                <FormLabel>Address Type</FormLabel>
                                <RadioGroup defaultValue="Permanent" value={employee.emp_address.address_type} onChange={handleRadioChange}>
                                    <Stack direction="row">
                                        <Radio value="Permanent">Permanent</Radio>
                                        <Radio value="Correspondence">Correspondence</Radio>
                                    </Stack>
                                </RadioGroup>
                            </FormControl>
                        </Stack>
                    </Box>
                </Grid>
                <Flex justify="flex-end">
                    <ButtonGroup mt={4}>
                        <Button colorScheme="teal" type="submit">
                            Submit
                        </Button>
                        <Button type="reset">
                            Cancel
                        </Button>
                    </ButtonGroup>            
                </Flex>
            </Box>        
            <AlertDialog
            isOpen={isOpen}
            leastDestructiveRef={cancelRef}
            onClose={onClose}
        >
            <AlertDialogOverlay>
                <AlertDialogContent>
                    <AlertDialogHeader fontSize="lg" fontWeight="bold">
                        {dialogTitle}
                    </AlertDialogHeader>

                    <AlertDialogBody>
                        {dialogMessage}
                    </AlertDialogBody>

                    <AlertDialogFooter>
                        <Button ref={cancelRef} onClick={onClose}>
                            Close
                        </Button>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialogOverlay>
        </AlertDialog>        
        </form>
    )
}

export default FormEmployee;