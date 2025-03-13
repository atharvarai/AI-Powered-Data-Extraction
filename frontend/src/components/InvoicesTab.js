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
import { updateInvoice } from '../redux/slices/invoiceSlice';

const InvoicesTab = () => {
  const { invoices, loading, error } = useSelector((state) => state.invoices);
  const dispatch = useDispatch();
  const [searchTerm, setSearchTerm] = useState('');
  const [editInvoice, setEditInvoice] = useState(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);

  // Filter invoices based on search term
  const filteredInvoices = invoices.filter((invoice) => {
    const searchTermLower = searchTerm.toLowerCase();
    return (
      invoice.serial_number.toLowerCase().includes(searchTermLower) ||
      invoice.customer_name.toLowerCase().includes(searchTermLower) ||
      invoice.product_name.toLowerCase().includes(searchTermLower)
    );
  });

  const handleEditClick = (invoice) => {
    setEditInvoice({ ...invoice });
    setEditDialogOpen(true);
  };

  const handleEditDialogClose = () => {
    setEditDialogOpen(false);
    setEditInvoice(null);
  };

  const handleEditSave = () => {
    dispatch(updateInvoice(editInvoice));
    setEditDialogOpen(false);
    setEditInvoice(null);
  };

  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditInvoice({
      ...editInvoice,
      [name]: name === 'quantity' || name === 'tax' || name === 'total_amount' 
        ? parseFloat(value) 
        : value
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
          placeholder="Search invoices..."
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

      {invoices.length === 0 ? (
        <Typography variant="body1" sx={{ textAlign: 'center', p: 3 }}>
          No invoices found. Upload an invoice file to get started.
        </Typography>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Serial Number</TableCell>
                <TableCell>Customer Name</TableCell>
                <TableCell>Product Name</TableCell>
                <TableCell>Quantity</TableCell>
                <TableCell>Tax</TableCell>
                <TableCell>Total Amount</TableCell>
                <TableCell>Date</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredInvoices.map((invoice) => (
                <TableRow key={invoice.id}>
                  <TableCell>{invoice.serial_number}</TableCell>
                  <TableCell>{invoice.customer_name}</TableCell>
                  <TableCell>{invoice.product_name}</TableCell>
                  <TableCell>{invoice.quantity}</TableCell>
                  <TableCell>{invoice.tax}</TableCell>
                  <TableCell>{invoice.total_amount}</TableCell>
                  <TableCell>{invoice.date}</TableCell>
                  <TableCell>
                    <IconButton 
                      size="small" 
                      color="primary"
                      onClick={() => handleEditClick(invoice)}
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
        <DialogTitle>Edit Invoice</DialogTitle>
        <DialogContent>
          {editInvoice && (
            <Box sx={{ pt: 2 }}>
              <TextField
                fullWidth
                margin="dense"
                label="Serial Number"
                name="serial_number"
                value={editInvoice.serial_number}
                onChange={handleEditChange}
              />
              <TextField
                fullWidth
                margin="dense"
                label="Customer Name"
                name="customer_name"
                value={editInvoice.customer_name}
                onChange={handleEditChange}
              />
              <TextField
                fullWidth
                margin="dense"
                label="Product Name"
                name="product_name"
                value={editInvoice.product_name}
                onChange={handleEditChange}
              />
              <TextField
                fullWidth
                margin="dense"
                label="Quantity"
                name="quantity"
                type="number"
                value={editInvoice.quantity}
                onChange={handleEditChange}
              />
              <TextField
                fullWidth
                margin="dense"
                label="Tax"
                name="tax"
                type="number"
                value={editInvoice.tax}
                onChange={handleEditChange}
              />
              <TextField
                fullWidth
                margin="dense"
                label="Total Amount"
                name="total_amount"
                type="number"
                value={editInvoice.total_amount}
                onChange={handleEditChange}
              />
              <TextField
                fullWidth
                margin="dense"
                label="Date"
                name="date"
                value={editInvoice.date}
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

export default InvoicesTab; 