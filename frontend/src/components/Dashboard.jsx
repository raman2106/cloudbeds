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
    TableContainer} from '@chakra-ui/react'


const Dashboard = () => {
    return (
        <Flex justifyContent="center" alignItems="start" height="100vh">
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
    );
  };

export default Dashboard;