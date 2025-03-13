import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Typography,
  Box,
  CircularProgress,
  Alert,
  TextField,
  InputAdornment,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import EditIcon from '@mui/icons-material/Edit';
import { updateCustomer } from '../redux/slices/customerSlice';
import { updateInvoiceByCustomerId } from '../redux/slices/invoiceSlice';

const CustomersTab = () => {
  const { customers, loading, error } = useSelector((state) => state.customers);
  const dispatch = useDispatch();
  const [searchTerm, setSearchTerm] = useState('');
  const [editCustomer, setEditCustomer] = useState(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);

  // Filter customers based on search term
  const filteredCustomers = customers.filter((customer) => {
    const searchTermLower = searchTerm.toLowerCase();
    return (
      customer.name.toLowerCase().includes(searchTermLower) ||
      (customer.phone_number && customer.phone_number.includes(searchTerm))
    );
  });

  const handleEditClick = (customer) => {
    setEditCustomer({ ...customer });
    setEditDialogOpen(true);
  };

  const handleEditDialogClose = () => {
    setEditDialogOpen(false);
    setEditCustomer(null);
  };

  const handleEditSave = () => {
    dispatch(updateCustomer(editCustomer));
    
    // Update related invoices if customer name changed
    if (editCustomer.name !== customers.find(c => c.id === editCustomer.id).name) {
      dispatch(updateInvoiceByCustomerId({
        customerId: editCustomer.id,
        customerName: editCustomer.name
      }));
    }
    
    setEditDialogOpen(false);
    setEditCustomer(null);
  };

  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditCustomer({
      ...editCustomer,
      [name]: name === 'total_purchase_amount' ? parseFloat(value) : value
    });
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 2 }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Search customers..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon />
              </InputAdornment>
            ),
          }}
        />
      </Box>

      {customers.length === 0 ? (
        <Typography variant="body1" sx={{ textAlign: 'center', p: 3 }}>
          No customers found. Upload an invoice file to get started.
        </Typography>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Phone Number</TableCell>
                <TableCell>Total Purchase Amount</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Address</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredCustomers.map((customer) => (
                <TableRow key={customer.id}>
                  <TableCell>{customer.name}</TableCell>
                  <TableCell>{customer.phone_number || 'N/A'}</TableCell>
                  <TableCell>{customer.total_purchase_amount}</TableCell>
                  <TableCell>{customer.email || 'N/A'}</TableCell>
                  <TableCell>{customer.address || 'N/A'}</TableCell>
                  <TableCell>
                    <IconButton 
                      size="small" 
                      color="primary"
                      onClick={() => handleEditClick(customer)}
                    >
                      <EditIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onClose={handleEditDialogClose}>
        <DialogTitle>Edit Customer</DialogTitle>
        <DialogContent>
          {editCustomer && (
            <Box sx={{ pt: 2 }}>
              <TextField
                fullWidth
                margin="dense"
                label="Name"
                name="name"
                value={editCustomer.name}
                onChange={handleEditChange}
              />
              <TextField
                fullWidth
                margin="dense"
                label="Phone Number"
                name="phone_number"
                value={editCustomer.phone_number || ''}
                onChange={handleEditChange}
              />
              <TextField
                fullWidth
                margin="dense"
                label="Total Purchase Amount"
                name="total_purchase_amount"
                type="number"
                value={editCustomer.total_purchase_amount}
                onChange={handleEditChange}
              />
              <TextField
                fullWidth
                margin="dense"
                label="Email"
                name="email"
                value={editCustomer.email || ''}
                onChange={handleEditChange}
              />
              <TextField
                fullWidth
                margin="dense"
                label="Address"
                name="address"
                value={editCustomer.address || ''}
                onChange={handleEditChange}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleEditDialogClose}>Cancel</Button>
          <Button onClick={handleEditSave} color="primary">Save</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CustomersTab; 