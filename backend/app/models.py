from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

class Product(BaseModel):
    id: Optional[str] = None
    name: str
    quantity: float
    unit_price: float
    tax: Optional[float] = 0  # Make tax optional with default 0
    price_with_tax: float
    discount: Optional[float] = 0

class Customer(BaseModel):
    id: Optional[str] = None
    name: str
    phone_number: Optional[str] = None
    total_purchase_amount: float
    address: Optional[str] = None
    email: Optional[str] = None

class Invoice(BaseModel):
    id: Optional[str] = None
    serial_number: str
    customer_name: str
    product_name: Union[str, List[str]] = "Unknown Product"  # Default value
    quantity: Union[float, List[float]] = 1.0  # Default value
    tax: float
    total_amount: float
    date: str
    customer_id: Optional[str] = None
    product_id: Optional[str] = None
    
    # Add validators to convert lists to strings if needed
    @validator('product_name')
    def validate_product_name(cls, v):
        if isinstance(v, list):
            return ', '.join(v)  # Join list items with commas
        return v
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if isinstance(v, list):
            return sum(v)  # Sum the quantities if it's a list
        return v

class ExtractedData(BaseModel):
    invoices: List[Invoice]
    products: List[Product]
    customers: List[Customer]
    validation_errors: Optional[List[str]] = []

class ValidationResponse(BaseModel):
    success: bool
    errors: List[str]
    data: Optional[Dict[str, Any]] = None 