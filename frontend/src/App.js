import React, { useState } from 'react';
import { Provider } from 'react-redux';
import { 
  Container, 
  Box, 
  Typography, 
  Tabs, 
  Tab, 
  AppBar, 
  Toolbar,
  CssBaseline,
  ThemeProvider,
  createTheme
} from '@mui/material';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import store from './redux/store';
import FileUpload from './components/FileUpload';
import InvoicesTab from './components/InvoicesTab';
import ProductsTab from './components/ProductsTab';
import CustomersTab from './components/CustomersTab';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  return (
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Box sx={{ flexGrow: 1 }}>
          <AppBar position="static">
            <Toolbar>
              <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                Invoice Data Extraction System
              </Typography>
            </Toolbar>
          </AppBar>
          <Container maxWidth="lg" sx={{ mt: 4 }}>
            <FileUpload />
            
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs 
                value={tabValue} 
                onChange={handleTabChange} 
                aria-label="invoice data tabs"
                variant="fullWidth"
              >
                <Tab label="Invoices" />
                <Tab label="Products" />
                <Tab label="Customers" />
              </Tabs>
            </Box>
            
            <Box sx={{ py: 3 }}>
              {tabValue === 0 && <InvoicesTab />}
              {tabValue === 1 && <ProductsTab />}
              {tabValue === 2 && <CustomersTab />}
            </Box>
          </Container>
        </Box>
        <ToastContainer position="bottom-right" />
      </ThemeProvider>
    </Provider>
  );
}

export default App; 