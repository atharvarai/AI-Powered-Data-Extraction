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
import { updateProduct } from '../redux/slices/productSlice';
import { updateInvoiceByProductId } from '../redux/slices/invoiceSlice';

const ProductsTab = () => {
  const { products, loading, error } = useSelector((state) => state.products);
  const dispatch = useDispatch();
  const [searchTerm, setSearchTerm] = useState('');
  const [editProduct, setEditProduct] = useState(null);
  const [editDialogOpen, setEditDialogOpen] = useState(false);

  // Filter products based on search term
  const filteredProducts = products.filter((product) => {
    const searchTermLower = searchTerm.toLowerCase();
    return product.name.toLowerCase().includes(searchTermLower);
  });

  const handleEditClick = (product) => {
    setEditProduct({ ...product });
    setEditDialogOpen(true);
  };

  const handleEditDialogClose = () => {
    setEditDialogOpen(false);
    setEditProduct(null);
  };

  const handleEditSave = () => {
    dispatch(updateProduct(editProduct));
    
    // Update related invoices if product name changed
    if (editProduct.name !== products.find(p => p.id === editProduct.id).name) {
      dispatch(updateInvoiceByProductId({
        productId: editProduct.id,
        productName: editProduct.name
      }));
    }
    
    setEditDialogOpen(false);
    setEditProduct(null);
  };

  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditProduct({
      ...editProduct,
      [name]: ['quantity', 'unit_price', 'tax', 'price_with_tax', 'discount'].includes(name)
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
          placeholder="Search products..."
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

      {products.length === 0 ? (
        <Typography variant="body1" sx={{ textAlign: 'center', p: 3 }}>
          No products found. Upload an invoice file to get started.
        </Typography>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>Quantity</TableCell>
                <TableCell>Unit Price</TableCell>
                <TableCell>Tax</TableCell>
                <TableCell>Price with Tax</TableCell>
                <TableCell>Discount</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredProducts.map((product) => (
                <TableRow key={product.id}>
                  <TableCell>{product.name}</TableCell>
                  <TableCell>{product.quantity}</TableCell>
                  <TableCell>{product.unit_price}</TableCell>
                  <TableCell>{product.tax}</TableCell>
                  <TableCell>{product.price_with_tax}</TableCell>
                  <TableCell>{product.discount || 0}</TableCell>
                  <TableCell>
                    <IconButton 
                      size="small" 
                      color="primary"
                      onClick={() => handleEditClick(product)}
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
        <DialogTitle>Edit Product</DialogTitle>
        <DialogContent>
          {editProduct && (
            <Box sx={{ pt: 2 }}>
              <TextField
                fullWidth
                margin="dense"
                label="Name"
                name="name"
                value={editProduct.name}
                onChange={handleEditChange}
              />
              <TextField
                fullWidth
                margin="dense"
                label="Quantity"
                name="quantity"
                type="number"
                value={editProduct.quantity}
                onChange={handleEditChange}
              />
              <TextField
                fullWidth
                margin="dense"
                label="Unit Price"
                name="unit_price"
                type="number"
                value={editProduct.unit_price}
                onChange={handleEditChange}
              />
              <TextField
                fullWidth
                margin="dense"
                label="Tax"
                name="tax"
                type="number"
                value={editProduct.tax}
                onChange={handleEditChange}
              />
              <TextField
                fullWidth
                margin="dense"
                label="Price with Tax"
                name="price_with_tax"
                type="number"
                value={editProduct.price_with_tax}
                onChange={handleEditChange}
              />
              <TextField
                fullWidth
                margin="dense"
                label="Discount"
                name="discount"
                type="number"
                value={editProduct.discount || 0}
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

export default ProductsTab; 