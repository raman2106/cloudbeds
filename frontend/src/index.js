import React, {useState} from "react";
import {render} from "react-dom";
import {ChakraProvider, useDisclosure} from "@chakra-ui/react";
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'


import Header from "./components/Header";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard"; // Import Dashboard component
import Sidebar from "./components/Sidebar"; // Import Sidebar component
import FormBooking from "./components/FormBooking";
import FormEmployee from "./components/FormEmployee";
import ManageEmployee from "./components/ManageEmployee";
import ManageRooms from "./components/ManageRooms";

function App() {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const btnRef = React.useRef();  
  const [isLoggedIn, setIsLoggedIn] = useState(false); // State to track login status

  const handleLogin = () => { // Function to set login status to true
    setIsLoggedIn(true);
  };

  return (
    <ChakraProvider>
      <Header onOpen={onOpen} btnRef={btnRef} />
      <Router>
        {isLoggedIn && <Sidebar isOpen={isOpen} onClose={onClose} btnRef={btnRef} />}
        <Routes>
          <Route path="/" element={<Navigate to="/login" />} />
          <Route 
            path="/login" element={isLoggedIn ? <Navigate to="/dashboard" /> : <Login onLogin={handleLogin} />} />
          <Route 
            path="/dashboard" element={isLoggedIn ? <Dashboard /> : <Navigate to="/login" />} />
          <Route 
            path="/create-booking" 
            element={isLoggedIn ? <FormBooking /> : <Navigate to="/login" />} />
          <Route 
            path="/create-employee" 
            element={isLoggedIn ? <FormEmployee /> : <Navigate to="/login" />} />
          <Route 
            path="/manage-employee" 
            element={isLoggedIn ? <ManageEmployee /> : <Navigate to="/login" />} />
          <Route 
            path="/manage-rooms" 
            element={isLoggedIn ? <ManageRooms /> : <Navigate to="/login" />} />                                    
        </Routes>
      </Router>
    </ChakraProvider>
  )
}



const rootElement = document.getElementById("root");
render(<App />, rootElement);