import React, { useEffect, useState, useRef, useCallback } from 'react';
import axios from 'axios';
import {
    Box,
    Flex,
    Table,
    Thead,
    Tbody,
    Tr,
    Th,
    Td,
    Text,
    Switch,
    TableContainer,
    Button,
    IconButton
} from '@chakra-ui/react';
import { ArrowForwardIcon, ArrowBackIcon } from '@chakra-ui/icons';

const ManageEmployee = () => {
    const authToken = localStorage.getItem('jwt');
    const [employees, setEmployees] = useState([]);
    const [page, setPage] = useState(0);
    const [loading, setLoading] = useState(true);
    const [hasMore, setHasMore] = useState(false);

    const handlePrevious = () => {
        if (page > 0) {
            setPage(prevPage => prevPage - 1);
        }
    };
    
    const handleNext = () => {
        setPage(prevPage => prevPage + 1);
    };

    useEffect(() => {
        setLoading(true);
        axios.get(`http://127.0.0.1:8000/emp/list/?skip=${page * 20}&limit=20`, {
            headers: {
                'accept': 'application/json',
                'Authorization': `Bearer ${authToken}`
            }
        }).then(res => {
            setEmployees(res.data);
            setHasMore(res.data.length > 0);
            setLoading(false);
        }).catch(error => {
            if (error.response && error.response.status === 404) {
                setHasMore(false);
            }
            setLoading(false);
        });
    }, [page]);

    const toggleIsActive = (emp_id, isActive) => {
        axios.put(`http://127.0.0.1:8000/emp/manage/${emp_id}?is_active=${!isActive}`, {}, {
            headers: {
                'accept': 'application/json',
                'Authorization': `Bearer ${authToken}`
            }
        }).then(res => {
            if (res.data.is_active === !isActive) {
                setEmployees(employees.map(employee => 
                    employee.emp_id === emp_id ? {...employee, emp_details: {...employee.emp_details, is_active: !isActive}} : employee
                ));
            }
        });
    };

    return (
        <Box borderRadius="lg" border="1px" borderColor="gray.200" p={4} pl={64} ml={40} pt="10" m={4}>
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
                        <Th>Employee ID</Th>
                        <Th>Name</Th>
                        <Th>Email</Th>
                        <Th>Phone</Th>
                        <Th>Is Active</Th>
                    </Tr>
                </Thead>
                <Tbody>
                    {employees.map((employee, index) => (
                        <Tr key={employee.emp_id}>
                            <Td>{employee.emp_id}</Td>
                            <Td>{`${employee.emp_details.first_name} ${employee.emp_details.middle_name} ${employee.emp_details.last_name}`}</Td>
                            <Td>{employee.emp_details.email}</Td>
                            <Td>{employee.emp_details.phone}</Td>
                            <Td>
                                <Switch 
                                    isChecked={employee.emp_details.is_active} 
                                    onChange={() => toggleIsActive(employee.emp_id, employee.emp_details.is_active)}
                                />
                            </Td>
                        </Tr>
                    ))}
                </Tbody>
            </Table>
        </Box>
    );
};

export default ManageEmployee;