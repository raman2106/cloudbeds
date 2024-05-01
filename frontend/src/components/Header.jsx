import React from "react";
import {Heading, Flex, Box} from "@chakra-ui/react";

const Header = ({ onOpen, btnRef }) => {
  return (
    <Box as="header" pos="relative" zIndex="2" bg="gray.800" p="2">
        <Flex
            as="nav"
            align="center"
            justify="space-between"
            wrap="wrap"
            paddingY="1rem"
            paddingX="1rem"
            bg="twitter.500"
            color="white"
            boxShadow="0px 2px 4px rgba(0, 0, 0, 0.2)">
                <Flex align="left" mr={1}>
                    <Heading
                        as="h1"
                        size="lg"
                        fontWeight="bold"
                        >
                        CloudBeds
                    </Heading>
                </Flex>
        </Flex>
    </Box>
  );
};

export default Header;