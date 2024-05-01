import React from "react";
import {render} from "react-dom";
import {ChakraProvider} from "@chakra-ui/react";

import Header from "./components/Header";
import Login from "./components/Login";


function App() {
  return (
    <ChakraProvider>
      <Header />
      <Login />
    </ChakraProvider>
  )
}



const rootElement = document.getElementById("root");
render(<App />, rootElement);