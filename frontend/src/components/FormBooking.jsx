import React, { useEffect, useState } from 'react';
import {
    FormControl,
    FormLabel,
    Input,
    Box,
    Grid,
    Button,
    Textarea,
    NumberInput,
    NumberInputField,
    Select,
    Stack,
    Heading,
    RadioGroup,
    Radio,
    Flex
} from '@chakra-ui/react'


const FormBooking = () => {

    //Fetch the list of supported government ID types from the backend
    const [idTypes, setIdTypes] = useState([]);
    const [roomList, setRoomList] = useState([]);
    const authToken = localStorage.getItem('jwt');


    const fetchIdTypes = async () => {
        const response = await fetch('http://127.0.0.1:8000/gov_id/list/', {
            method: 'GET',
            headers: {
                'accept': 'application/json',
                'Authorization': `Bearer ${authToken}`
            }
        });
        const data = await response.json();
        const idTypes = data.map(item => ({ value: item.name, label: item.name }));
        setIdTypes(idTypes);
    };
    
    useEffect(() => {
        fetchIdTypes();
    }, []);

    //Fetch the list of available rooms from the backend


    const fetchRoomList = async () => {
        const response = await fetch('http://127.0.0.1:8000/room/list/?room_state=Available', {
            method: 'GET',
            headers: {
                'accept': 'application/json',
                'Authorization': `Bearer ${authToken}`
            }
        });
        const data = await response.json();
        const rooms = data.map(item => ({ value: item.room_number, label: `Room ${item.room_number} - ${item.room_type}` }));
        setRoomList(rooms);
    };

    return (
        <Box  
            borderRadius="lg" 
            border="1px" 
            borderColor="gray.200"         
            p={4}  
            pl={64}
            ml={40} 
            pt="10"
            m={4}>
            <Grid templateColumns="repeat(2, 1fr)" gap={3}>
                <Box>
                    <Heading as="h2" size="md">Customer Details</Heading>
                    <Stack spacing={1}>
                        <FormControl id="first_name" isRequired>
                            <FormLabel>First Name</FormLabel>
                            <Input type="text" />
                        </FormControl>
                        <FormControl id="middle_name" defaultValue="">
                            <FormLabel>Middle Name</FormLabel>
                            <Input type="text" />
                        </FormControl>
                        <FormControl id="last_name" isRequired>
                            <FormLabel>Last Name</FormLabel>
                            <Input type="text" />
                        </FormControl>
                        <FormControl id="email" isRequired>
                            <FormLabel>Email</FormLabel>
                            <Input type="email" />
                        </FormControl>
                        <FormControl id="phone" isRequired>
                            <FormLabel>Phone</FormLabel>
                            <Input type="text" />
                        </FormControl>
                    </Stack>
                </Box>
                <Box>
                    <Heading as="h2" size="md">Customer's address</Heading>
                    <Stack spacing={1}>
                        <FormControl id="first_line" isRequired>
                            <FormLabel>First Line</FormLabel>
                            <Input type="text" />
                        </FormControl>
                        <FormControl id="second_line" defaultValue="">
                            <FormLabel>Second Line</FormLabel>
                            <Input type="text" />
                        </FormControl>
                        <FormControl id="landmark" isRequired>
                            <FormLabel>Landmark</FormLabel>
                            <Input type="text" />
                        </FormControl>
                        <FormControl id="district" isRequired>
                            <FormLabel>District</FormLabel>
                            <Input type="text" />
                        </FormControl>
                        <FormControl id="state" isRequired>
                            <FormLabel>State</FormLabel>
                            <Input type="text" />
                        </FormControl>
                        <FormControl id="pin" isRequired>
                            <FormLabel>Pin</FormLabel>
                            <Input type="text" />
                        </FormControl>
                        <FormControl id="address_type" isRequired>
                            <FormLabel>Address Type</FormLabel>
                                <RadioGroup defaultValue="Permanent">
                                    <Stack direction="row">
                                        <Radio value="Permanent">Permanent</Radio>
                                        <Radio value="Correspondence">Correspondence</Radio>
                                    </Stack>
                                </RadioGroup>
                            </FormControl>
                    </Stack>
                </Box>
            </Grid>
            <Box pt={10}>
                <Heading as="h2" size="md">Booking Details</Heading>
                <Stack spacing={2} pt={10}>
                    <Flex direction="row">
                        <Box width="22%" mr="5%">
                            <FormControl id="checkIn" isRequired>
                                <FormLabel>Check-In date</FormLabel>
                                <Input type="date" />
                            </FormControl>
                        </Box>
                        <Box width="22%">
                            <FormControl id="checkOut" isRequired>
                                <FormLabel>Check-Out date</FormLabel>
                                <Input type="date" />
                            </FormControl>
                        </Box>
                    </Flex>
                    <Flex direction="row">
                        <Box width="22%" mr="5%">
                            <FormControl id="govtID" isRequired>
                                    <FormLabel onClick={fetchIdTypes}>Government ID Type</FormLabel>
                                    <Select placeholder="Select ID Type">
                                        {idTypes.map((idType, index) => (
                                            <option key={index} value={idType.value}>{idType.label}</option>
                                        ))}
                                    </Select>                        
                            </FormControl>
                        </Box>
                        <Box width="22%">
                            <FormControl id="roomNum" isRequired>
                                <FormLabel>Room number</FormLabel>
                                <Select placeholder="Select room number" onClick={fetchRoomList}>                                   
                                    {roomList.map((room, index) => (
                                        <option key={index} value={room.value}>{room.label}</option>
                                    ))}
                                </Select>
                            </FormControl>        
                        </Box>                                        
                    </Flex>                   
                    <Flex direction="row">
                        <Box width="22%" mr="5%">
                            <FormControl id="governmentIDNumber" isRequired>
                                <FormLabel>Government ID Number</FormLabel>
                                <Input type="text" />
                            </FormControl>
                        </Box>
                        <Box width="22%">
                            <FormControl id="expDate">
                                <FormLabel>Govt ID Expiry</FormLabel>
                                <Input 
                                    type="text" 
                                    placeholder="MM-YY" 
                                    pattern="(0[1-9]|1[0-2])-[0-9]{2}" />
                            </FormControl>
                        </Box>
                    </Flex>
                    <Box>
                        <FormControl id="comments">
                            <FormLabel>Comments</FormLabel>
                            <Textarea placeholder="Enter comments here" />
                        </FormControl>
                    </Box>
                </Stack>
            </Box>
            <Button mt={4} colorScheme="teal" type="submit">
                Submit
            </Button>
        </Box>
    )
}

export default FormBooking;