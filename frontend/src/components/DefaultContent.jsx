import React from 'react';
import { Flex } from '@chakra-ui/react';
import { Card, CardHeader, CardBody, CardFooter } from '@chakra-ui/react';

const DefaultContent = () => {
  return (
    <Flex direction="row" justify="space-between">
      <Card bg="teal.300" h="200px" p={5} m={2}>
        <CardHeader>Header 1</CardHeader>
        <CardBody>Card 1</CardBody>
        <CardFooter>Footer 1</CardFooter>
      </Card>
      <Card bg="teal.300" h="200px" p={5} m={2}>
        <CardHeader>Header 2</CardHeader>
        <CardBody>Card 2</CardBody>
        <CardFooter>Footer 2</CardFooter>
      </Card>
      <Card bg="teal.300" h="200px" p={5} m={2}>
        <CardHeader>Header 3</CardHeader>
        <CardBody>Card 3</CardBody>
        <CardFooter>Footer 3</CardFooter>
      </Card>
    </Flex>
  );
};

export default DefaultContent;