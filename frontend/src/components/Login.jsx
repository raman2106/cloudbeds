import {
  Box,
  Button,
  Checkbox,
  Container,
  Divider,
  FormControl,
  FormLabel,
  Heading,
  HStack,
  Input,
  Link,
  Stack,
  Text,
} from '@chakra-ui/react'
import { Logo } from './Logo'
import { PasswordField } from './PasswordField'
import { useState } from 'react';

const Login = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();

    const response = await fetch('http://127.0.0.1:8000/auth/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        grant_type: '',
        username: email,
        password: password,
        scope: '',
        client_id: '',
        client_secret: '',
      }),
    });

    const data = await response.json();

    if (response.ok) {
      // Save the auth token. Save the auth token in local storage
      localStorage.setItem('jwt', data.access_token);
      // Set isLoggedIn to true after successful login
      onLogin();
    } else {
      // Handle error. You might want to set an error message in state and display it to the user.
      console.error(data.detail);
    }
  };

  return (
    <Container backgroundColor="Teal 100" maxW="lg" py={{ base: '12', md: '24' }} px={{ base: '0', sm: '8' }}>
      <Stack spacing="8">
        <Stack spacing="6">
          <Logo />
          <Stack spacing={{ base: '2', md: '3' }} textAlign="center">
            <Heading size={{ base: 'xs', md: 'sm' }}>Log in to your account</Heading>
          </Stack>
        </Stack>
        <Box
          py={{ base: '0', sm: '8' }}
          px={{ base: '4', sm: '10' }}
          bg={{ base: 'transparent', sm: 'bg.surface' }}
          boxShadow={{ base: 'none', sm: 'md' }}
          borderRadius={{ base: 'none', sm: 'xl' }}
        >
          <form onSubmit={handleSubmit}>
          <Stack spacing="6">
            <Stack spacing="5">
              <FormControl>
                <FormLabel htmlFor="email" >Email</FormLabel>
                <Input 
                  id="email" 
                  type="email" 
                  value={email} onChange={(e) => setEmail(e.target.value)} />
              </FormControl>
              <PasswordField 
                value={password} onChange={(e) => setPassword(e.target.value)} />
            </Stack>
            <Stack spacing="6">
              <Button type="submit">Sign in</Button>
            </Stack>
          </Stack>
          </form>
        </Box>
      </Stack>
    </Container>
  );
};

export default Login;
