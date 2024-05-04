import React, { useState, useEffect } from 'react';
import { ButtonGroup, Box, Text, Flex, IconButton, Table, Thead, Tbody, Tr, Th, Td, Button, FormControl, FormLabel, Input, AlertDialog, AlertDialogOverlay, AlertDialogContent, AlertDialogHeader, AlertDialogBody, AlertDialogFooter, useDisclosure } from '@chakra-ui/react';
import { ArrowBackIcon, ArrowForwardIcon } from '@chakra-ui/icons';
import axios from 'axios';

const ManageRooms = () => {
    const authToken = localStorage.getItem('jwt');
    const [rooms, setRooms] = useState([]);
    const [page, setPage] = useState(0);
    const [loading, setLoading] = useState(true);
    const [hasMore, setHasMore] = useState(false);
    const [roomNumber, setRoomNumber] = useState('');
    const [roomType, setRoomType] = useState('');
    const [roomState, setRoomState] = useState('');
    const [dialogMessage, setDialogMessage] = useState('');
    const { isOpen, onOpen, onClose } = useDisclosure();

    useEffect(() => {
        setLoading(true);
        axios.get(`http://127.0.0.1:8000/room/list/?skip=${page * 20}&limit=20`, {
            headers: {
                'accept': 'application/json',
                'Authorization': `Bearer ${authToken}`
            }
        }).then(res => {
            setRooms(res.data);
            setHasMore(res.data.length === 20);
            setLoading(false);
        });
    }, [page]);

    const handlePrevious = () => {
        setPage(prevPage => prevPage - 1);
    }

    const handleNext = () => {
        setPage(prevPage => prevPage + 1);
    }

    const onSubmit = () => {
        const data = {
            room_number: roomNumber,
            room_type: roomType,
            room_state: roomState,
        };

        axios.post(`http://127.0.0.1:8000/room/add/`, data, {
            headers: {
                'accept': 'application/json',
                'Authorization': `Bearer ${authToken}`,
                'Content-Type': 'application/json'
            }
        }).then(res => {
            setDialogMessage('Room created successfully');
            onOpen();
            setRoomNumber('');
            setRoomType('');
            setRoomState('');
            setPage(0);
        }).catch(error => {
            setDialogMessage(error.response.data.detail);
            onOpen();
        });
    };

    return (
        <Box borderRadius="lg" border="1px" borderColor="gray.200" p={4} pl={64} ml={40} pt="10" m={4}>
            <Text fontSize="xl" fontWeight="bold">Create Room</Text>
            <Flex justifyContent="space-between" alignItems="center">
                <form onSubmit={(e) => { e.preventDefault(); onSubmit(); }}>
                    <Flex>
                        <FormControl mr={4}>
                            <FormLabel>Room Number</FormLabel>
                            <Input type="number" value={roomNumber} onChange={(e) => setRoomNumber(e.target.value)} required />
                        </FormControl>
                        <FormControl mr={4}>
                            <FormLabel>Room Type</FormLabel>
                            <Input type="text" value={roomType} onChange={(e) => setRoomType(e.target.value)} required />
                        </FormControl>
                        <FormControl mr={4}>
                            <FormLabel>Room State</FormLabel>
                            <Input type="text" value={roomState} onChange={(e) => setRoomState(e.target.value)} required />
                        </FormControl>
                        <Flex justify="flex-end">
                    <ButtonGroup mt={8}>
                        <Button colorScheme="teal" type="submit">
                            Submit
                        </Button>
                        <Button type="reset">
                            Cancel
                        </Button>
                    </ButtonGroup>            
                </Flex>
                    </Flex>
                </form>
            </Flex>
            <Box pt={10}>
            <Flex justifyContent="space-between" alignItems="center">
            <Text mb={4} fontSize="lg" fontWeight="bold">Employees</Text>
                <Flex>
                    <IconButton
                        aria-label="Previous page"
                        icon={<ArrowBackIcon />}
                        isDisabled={page === 0}
                        onClick={handlePrevious}
                    />
                    <IconButton
                        aria-label="Next page"
                        icon={<ArrowForwardIcon />}
                        isDisabled={!hasMore}
                        onClick={handleNext}
                    />
                </Flex>
            </Flex>
            <Table variant='striped' colorScheme='teal'>
                <Thead>
                    <Tr>
                        <Th>Room Number</Th>
                        <Th>Room Type</Th>
                        <Th>Room State</Th>
                    </Tr>
                </Thead>
                <Tbody>
                    {rooms.map(room => (
                        <Tr key={room.id}>
                            <Td>{room.room_number}</Td>
                            <Td>{room.room_type}</Td>
                            <Td>{room.room_state}</Td>
                        </Tr>
                    ))}
                </Tbody>
            </Table>
            <AlertDialog isOpen={isOpen} onClose={onClose}>
                <AlertDialogOverlay>
                    <AlertDialogContent>
                        <AlertDialogHeader fontSize="lg" fontWeight="bold">
                            Operation Status
                        </AlertDialogHeader>
                        <AlertDialogBody>
                            {dialogMessage}
                        </AlertDialogBody>
                        <AlertDialogFooter>
                            <Button onClick={onClose}>
                                Close
                            </Button>
                        </AlertDialogFooter>
                    </AlertDialogContent>
                </AlertDialogOverlay>
            </AlertDialog>
        </Box>
    </Box>
    );
};

export default ManageRooms;