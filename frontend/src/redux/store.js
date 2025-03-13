import { configureStore } from '@reduxjs/toolkit';
import invoiceReducer from './slices/invoiceSlice';
import productReducer from './slices/productSlice';
import customerReducer from './slices/customerSlice';

export const store = configureStore({
  reducer: {
    invoices: invoiceReducer,
    products: productReducer,
    customers: customerReducer,
  },
});

export default store; 