import axios from 'axios';
import { setInvoices, setLoading as setInvoicesLoading, setError as setInvoicesError } from './slices/invoiceSlice';
import { setProducts, setLoading as setProductsLoading, setError as setProductsError } from './slices/productSlice';
import { setCustomers, setLoading as setCustomersLoading, setError as setCustomersError } from './slices/customerSlice';

const API_URL = 'http://localhost:8000/api';

// Thunk for uploading and extracting data from files
export const uploadAndExtractData = (file) => async (dispatch) => {
  try {
    // Set loading state for all slices
    dispatch(setInvoicesLoading(true));
    dispatch(setProductsLoading(true));
    dispatch(setCustomersLoading(true));
    
    // Clear any previous errors
    dispatch(setInvoicesError(null));
    dispatch(setProductsError(null));
    dispatch(setCustomersError(null));
    
    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    
    // Make API request
    const response = await axios.post(`${API_URL}/extract`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    // Update state with extracted data
    dispatch(setInvoices(response.data.invoices));
    dispatch(setProducts(response.data.products));
    dispatch(setCustomers(response.data.customers));
    
    // Return validation errors if any
    return response.data.validation_errors;
  } catch (error) {
    // Handle errors
    const errorMessage = error.response?.data?.detail || 'Error extracting data from file';
    dispatch(setInvoicesError(errorMessage));
    dispatch(setProductsError(errorMessage));
    dispatch(setCustomersError(errorMessage));
    return [errorMessage];
  } finally {
    // Reset loading state
    dispatch(setInvoicesLoading(false));
    dispatch(setProductsLoading(false));
    dispatch(setCustomersLoading(false));
  }
}; 