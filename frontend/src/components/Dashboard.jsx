import React from 'react';
import {
    Menu,
    MenuButton,
    MenuList,
    MenuItem,
    MenuItemOption,
    MenuGroup,
    MenuOptionGroup,
    MenuDivider, 
    IconButton
  } from '@chakra-ui/react'
import { AddIcon, HamburgerIcon, ExternalLinkIcon, RepeatIcon, EditIcon } from "@chakra-ui/icons";
import { Router, Route, Routes, Link as RouterLink, Navigate } from 'react-router-dom'; // Import Link as RouterLink

// import Content1 from './Content1';
// import Content2 from './Content2';
import DefaultContent from './DefaultContent'; // Import DefaultContent component

const Dashboard = () => {
    return (
            <Menu>
            <MenuButton
                as={IconButton}
                aria-label='Options'
                icon={<HamburgerIcon />}
                variant='outline'
                defaultIsOpen={true}
            />
            <MenuList>
                <MenuItem icon={<AddIcon />} command='⌘T'>
                New Tab
                </MenuItem>
                <MenuItem icon={<ExternalLinkIcon />} command='⌘N'>
                New Window
                </MenuItem>
                <MenuItem icon={<RepeatIcon />} command='⌘⇧N'>
                Open Closed Tab
                </MenuItem>
                <MenuItem icon={<EditIcon />} command='⌘O'>
                Open File...
                </MenuItem>
            </MenuList>
            </Menu>
        );
};

export default Dashboard;