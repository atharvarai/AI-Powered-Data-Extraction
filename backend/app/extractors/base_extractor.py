from abc import ABC, abstractmethod
from typing import Dict, Any, List
from ..models import ExtractedData

class BaseExtractor(ABC):
    """Base class for all data extractors"""
    
    @abstractmethod
    async def extract(self, file_path: str) -> ExtractedData:
        """Extract data from a file and return structured data"""
        pass
    
    def preprocess_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess the extracted data to ensure it matches our model requirements"""
        processed_data = {
            'invoices': [],
            'products': data.get('products', []),
            'customers': data.get('customers', [])
        }
        
        # First, process products to ensure consistent tax values
        for product in processed_data['products']:
            # Check if tax is a percentage (typically less than 100)
            if product.get('tax') is not None and product.get('tax') <= 100 and product.get('unit_price') is not None:
                # Convert tax percentage to amount
                tax_percentage = product['tax']
                tax_amount = round((product['unit_price'] * product['quantity'] * tax_percentage / 100), 2)
                product['tax'] = tax_amount
            elif product.get('tax') is None:
                # Calculate tax based on price_with_tax and unit_price if available
                if 'price_with_tax' in product and 'unit_price' in product:
                    product['tax'] = round(product['price_with_tax'] - (product['unit_price'] * product['quantity']), 2)
                    if product['tax'] < 0:  # Handle case where price_with_tax is less than unit_price (due to discount)
                        product['tax'] = 0
                else:
                    product['tax'] = 0
            else:
                # Round existing tax values
                product['tax'] = round(product['tax'], 2)
            
            # Round other numeric values
            if 'price_with_tax' in product:
                product['price_with_tax'] = round(product['price_with_tax'], 2)
            if 'unit_price' in product:
                product['unit_price'] = round(product['unit_price'], 2)
            if 'discount' in product and product['discount'] is not None:
                product['discount'] = round(product['discount'], 2)
        
        # Process invoices
        for invoice in data.get('invoices', []):
            # Handle case where product_name is a list
            if isinstance(invoice.get('product_name'), list):
                product_names = invoice['product_name']
                quantities = invoice['quantity'] if isinstance(invoice.get('quantity'), list) else [1] * len(product_names)
                
                # Create a product name to product mapping
                product_map = {p['name']: p for p in processed_data['products']}
                
                # Create separate invoice for each product
                for i, product_name in enumerate(product_names):
                    if i < len(quantities):
                        quantity = quantities[i]
                        
                        # Find the matching product
                        if product_name in product_map:
                            product = product_map[product_name]
                            
                            # Use product data for tax and total amount
                            tax = product['tax']
                            total_amount = round(product['price_with_tax'], 2)
                            
                            new_invoice = {
                                **invoice,
                                'product_name': product_name,
                                'quantity': quantity,
                                'tax': tax,
                                'total_amount': total_amount
                            }
                        else:
                            # If product not found, use equal distribution
                            new_invoice = {
                                **invoice,
                                'product_name': product_name,
                                'quantity': quantity,
                                'tax': round(invoice.get('tax', 0) / len(product_names), 2),
                                'total_amount': round(invoice.get('total_amount', 0) / len(product_names), 2)
                            }
                        
                        processed_data['invoices'].append(new_invoice)
            else:
                # For single product invoices
                product_name = invoice.get('product_name')
                quantity = invoice.get('quantity', 1)
                
                # Find the matching product
                matching_product = next((p for p in processed_data['products'] if p['name'] == product_name), None)
                
                if matching_product:
                    # Use product data for tax and total amount
                    tax = matching_product['tax']
                    total_amount = round(matching_product['price_with_tax'], 2)
                    
                    new_invoice = {
                        **invoice,
                        'tax': tax,
                        'total_amount': total_amount
                    }
                    processed_data['invoices'].append(new_invoice)
                else:
                    # If product not found, just round the values
                    invoice_copy = invoice.copy()
                    if 'tax' in invoice_copy:
                        invoice_copy['tax'] = round(invoice_copy['tax'], 2)
                    if 'total_amount' in invoice_copy:
                        invoice_copy['total_amount'] = round(invoice_copy['total_amount'], 2)
                    processed_data['invoices'].append(invoice_copy)
        
        # Round customer total purchase amounts
        for customer in processed_data['customers']:
            if 'total_purchase_amount' in customer:
                customer['total_purchase_amount'] = round(customer['total_purchase_amount'], 2)
        
        return processed_data
    
    def validate_data(self, data):
        """Validate the extracted data and return any validation errors"""
        validation_errors = []
        
        # Check invoices
        for i, invoice in enumerate(data.get('invoices', [])):
            if not invoice.get('serial_number'):
                validation_errors.append(f"Invoice {i+1} is missing serial number")
            
            # Only validate total_amount if it's explicitly zero, not if it's missing
            if 'total_amount' in invoice and invoice['total_amount'] == 0:
                validation_errors.append(f"Invoice {i+1} has zero total amount")
        
        # Check products
        for i, product in enumerate(data.get('products', [])):
            if not product.get('name'):
                validation_errors.append(f"Product {i+1} is missing name")
            
            # Only validate unit_price if it's explicitly zero, not if it's missing
            if 'unit_price' in product and product['unit_price'] == 0:
                validation_errors.append(f"Product {i+1} has zero unit price")
        
        return validation_errors 