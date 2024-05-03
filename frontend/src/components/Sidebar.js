import { Box, Accordion, AccordionItem, AccordionButton, AccordionPanel, AccordionIcon, VStack } from "@chakra-ui/react";
import { Link as RouterLink } from "react-router-dom";

const Sidebar = ({ onClose }) => {
  return (
    <Box
    as="nav"
    pos="fixed"
    top="0"
    left="0"
    zIndex="1"
    h="full"
    w="60"
    pt="24"
    bg="gray.800"
    color="white"
    overflowY="auto"
    px="8"
    >
    <Accordion allowToggle>
        <AccordionItem>
        <h2>
            <AccordionButton>
            <Box flex="1" textAlign="left" p={0}>
                <RouterLink to="/dashboard" onClick={onClose}>
                    Dashboard
                </RouterLink>
            </Box>
            </AccordionButton>
        </h2>
        {/* <AccordionPanel pb={4}>
            <RouterLink to="/dashboard" onClick={onClose}>
            Dashboard
            </RouterLink>
        </AccordionPanel> */}
        </AccordionItem>
        <AccordionItem>
        <h2>
            <AccordionButton>
            <Box flex="1" textAlign="left">
                Bookings
            </Box>
            <AccordionIcon />
            </AccordionButton>
        </h2>
        <AccordionPanel pb={4}>
            <VStack align="start" spacing={2}>
            <RouterLink to="/create-booking" onClick={onClose}>
                Create Booking
            </RouterLink>
            <RouterLink to="/update-booking" onClick={onClose}>
                Update Booking
            </RouterLink>
            <RouterLink to="/manage-booking" onClick={onClose}>
                Manage Booking
            </RouterLink>
            </VStack>
        </AccordionPanel>
        </AccordionItem>
        <AccordionItem>
        <h2>
            <AccordionButton>
            <Box flex="1" textAlign="left">
                Settings
            </Box>
            </AccordionButton>
        </h2>
        <AccordionPanel pb={4}>
            <RouterLink to="/settings" onClick={onClose}>
            Settings
            </RouterLink>
        </AccordionPanel>
        </AccordionItem>
        {/* Add more AccordionItems as needed */}
    </Accordion>
    </Box>
  );
};

export default Sidebar;