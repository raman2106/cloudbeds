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
                            <Text fontFamily="mono" fontSize="7xl" fontWeight="bold">22</Text>
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
                                <Text fontFamily="mono" fontSize="7xl" fontWeight="bold">02</Text>
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
                                <Text fontFamily="mono" fontSize="7xl" fontWeight="bold">10</Text>
                            </CardBody>
                        </Card>
                    </SimpleGrid>
                </Flex>
            </Box>
            <Box pl={64} pt="10">
            <Flex>
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
                        <Tr>
                            <Td>B1001</Td>
                            <Td>Yogendra Yadav</Td>
                            <Td>10-05-2024</Td>
                            <Td>14-05-2024</Td>
                            <Td isNumeric>101</Td>
                            <Td>Standard</Td>
                            <Td></Td>
                        </Tr>
                        <Tr>
                            <Td>B1002</Td>
                            <Td>Murali M</Td>
                            <Td>06-05-2024</Td>
                            <Td>07-05-2024</Td>
                            <Td isNumeric>101</Td>
                            <Td>Standard</Td>
                            <Td>Need early checkin</Td>
                        </Tr>
                        <Tr>
                            <Td>B1003</Td>
                            <Td>John D'Souza</Td>
                            <Td>07-05-2024</Td>
                            <Td>07-05-2024</Td>
                            <Td isNumeric>405</Td>
                            <Td>Club</Td>
                            <Td>Need early checkin</Td>
                        </Tr>
                        </Tbody>
                    </Table>
                </TableContainer>
            </Flex>            
        </Box>
        </Flex>
    );
  };

export default Dashboard;