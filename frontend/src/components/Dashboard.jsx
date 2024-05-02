import React, { useEffect, useState } from 'react';
import { 
    Card, 
    CardHeader, 
    CardBody,  
    SimpleGrid, 
    Flex, 
    Heading, 
    Text, 
    Button,
    Table,
    Thead,
    Tbody,
    Tfoot,
    Tr,
    Th,
    Td,
    TableCaption,
    TableContainer,
    Box} from '@chakra-ui/react'


const Dashboard = () => {
    const [bookings, setBookings] = useState([]);

    useEffect(() => {
        const fetchBookings = async () => {
            const authToken = localStorage.getItem('jwt');
            const response = await fetch('http://127.0.0.1:8000/booking/list/?skip=0&limit=20', {
                method: 'GET',
                headers: {
                    'accept': 'application/json',
                    'Authorization': `Bearer ${authToken}`
                }
            });

            if (response.ok) {
                const data = await response.json();
                setBookings(data);
            } else {
                console.error('Failed to fetch bookings');
            }
        };

        fetchBookings();
    }, []);
    
    // Parse the returned payload and extract the required data
    const upcomingBookings = bookings.filter(booking => 
        new Date(booking.booking.checkin) > new Date() && booking.booking.status === 'Booked'
    );
    const ongoingBookings = bookings.filter(booking => booking.booking.status === 'Ongoing');
    const cancelledBookings = bookings.filter(booking => booking.booking.status === 'Cancelled');
    const upcomingBookingsTable = bookings.filter(booking => {
        const checkinDate = new Date(booking.booking.checkin);
        const currentDate = new Date();
        const futureDate = new Date();
        futureDate.setDate(currentDate.getDate() + 15);
        return checkinDate > currentDate && checkinDate <= futureDate && booking.booking.status === 'booked';
    });    

    return (
        <Flex direction="column">
            <Box pt="5">
            <Flex justifyContent="center" alignItems="start">
                    <SimpleGrid spacing={4} templateColumns='repeat(3, 1fr)'  pl={64}>
                        <Card  
                            w="300px" 
                            h="150px" 
                            boxShadow="lg" 
                            borderRadius="md" 
                            border="1px solid" 
                            borderColor="gray.200" 
                            backgroundColor="gray.85">
                            <CardHeader p={0}>
                            <Heading size='sm' pl={4} pt={4}>Booked</Heading>
                            </CardHeader>
                            <CardBody p={0} textAlign="center">
                            <Text fontFamily="mono" fontSize="7xl" fontWeight="bold">{upcomingBookings.length}</Text>
                            </CardBody>
                        </Card>
                        <Card
                            w="300px" 
                            h="150px" 
                            boxShadow="lg" 
                            borderRadius="md" 
                            border="1px solid" 
                            borderColor="gray.200" 
                            backgroundColor="gray.85">
                            <CardHeader p={0}>
                                <Heading size='sm' pl={4} pt={4}>Ongoing</Heading>
                            </CardHeader>
                            <CardBody p={0} textAlign="center">
                                <Text fontFamily="mono" fontSize="7xl" fontWeight="bold">{ongoingBookings.length}</Text>
                            </CardBody>
                        </Card>
                        <Card
                            w="300px" 
                            h="150px" 
                            boxShadow="lg" 
                            borderRadius="md" 
                            border="1px solid" 
                            borderColor="gray.200" 
                            backgroundColor="gray.85">
                            <CardHeader p={0}>
                                <Heading size='sm' pl={4} pt={4}>Cancelled</Heading>
                            </CardHeader>
                            <CardBody p={0} textAlign="center">
                                <Text fontFamily="mono" fontSize="7xl" fontWeight="bold">{cancelledBookings.length}</Text>
                            </CardBody>
                        </Card>
                    </SimpleGrid>
                </Flex>
            </Box>
            <Box pl={64} pt="10">
            <Flex overflowY="auto">
                <TableContainer width="99%">
                <Text mb={4} fontSize="lg" fontWeight="bold">Upcoming bookings</Text>
                    <Table variant='striped' colorScheme='teal'>
                        <Thead>
                        <Tr>
                            <Th>Booking ID</Th>
                            <Th>Customer Name</Th>
                            <Th>Checkin date</Th>
                            <Th>Checkout date</Th>
                            <Th isNumeric>Room number</Th>
                            <Th>Room Type</Th>
                            <Th>Comments</Th>
                        </Tr>
                        </Thead>
                        <Tbody>
                            {upcomingBookingsTable.map((booking) => (
                            <Tr key={booking.booking_id}>
                                <Td>{booking.booking_id}</Td>
                                <Td>{booking.customer.customer_details.first_name} {booking.customer.customer_details.last_name}</Td>
                                <Td>{booking.booking.checkin}</Td>
                                <Td>{booking.booking.checkout}</Td>
                                <Td isNumeric>{booking.booking.room_num}</Td>
                                <Td>{booking.booking.status}</Td>
                                <Td>{booking.booking.comments}</Td>
                            </Tr>
                            ))}
                        </Tbody>
                    </Table>
                </TableContainer>
            </Flex>            
        </Box>
        </Flex>
    );
  };

export default Dashboard;