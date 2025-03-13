import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  invoices: [],
  loading: false,
  error: null,
};

const invoiceSlice = createSlice({
  name: 'invoices',
  initialState,
  reducers: {
    setInvoices: (state, action) => {
      state.invoices = action.payload;
    },
    addInvoice: (state, action) => {
      state.invoices.push(action.payload);
    },
    updateInvoice: (state, action) => {
      const index = state.invoices.findIndex(invoice => invoice.id === action.payload.id);
      if (index !== -1) {
        state.invoices[index] = action.payload;
      }
    },
    deleteInvoice: (state, action) => {
      state.invoices = state.invoices.filter(invoice => invoice.id !== action.payload);
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    updateInvoiceByProductId: (state, action) => {
      const { productId, productName } = action.payload;
      state.invoices = state.invoices.map(invoice => {
        if (invoice.product_id === productId) {
          return { ...invoice, product_name: productName };
        }
        return invoice;
      });
    },
    updateInvoiceByCustomerId: (state, action) => {
      const { customerId, customerName } = action.payload;
      state.invoices = state.invoices.map(invoice => {
        if (invoice.customer_id === customerId) {
          return { ...invoice, customer_name: customerName };
        }
        return invoice;
      });
    }
  },
});

export const { 
  setInvoices, 
  addInvoice, 
  updateInvoice, 
  deleteInvoice, 
  setLoading, 
  setError,
  updateInvoiceByProductId,
  updateInvoiceByCustomerId
} = invoiceSlice.actions;

export default invoiceSlice.reducer; 