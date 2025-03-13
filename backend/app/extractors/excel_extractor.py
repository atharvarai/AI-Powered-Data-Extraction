import pandas as pd
import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv
from ..models import ExtractedData
from .base_extractor import BaseExtractor

load_dotenv()

class ExcelExtractor(BaseExtractor):
    """Extract data from Excel files using pandas and Google Gemini for complex cases"""
    
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    def clean_json_response(self, response_text):
        """Clean up the JSON response to make it valid"""
        # Remove markdown code block indicators if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        # Remove comments (both // and /* */ style)
        response_text = re.sub(r'//.*?(\n|$)', '', response_text)
        response_text = re.sub(r'/\*.*?\*/', '', response_text, flags=re.DOTALL)
        
        # Fix trailing commas in arrays and objects
        response_text = re.sub(r',\s*]', ']', response_text)
        response_text = re.sub(r',\s*}', '}', response_text)
        
        # Fix missing commas between objects in arrays
        response_text = re.sub(r'}\s*{', '},{', response_text)
        
        # Replace any null values with appropriate JSON null
        response_text = re.sub(r':\s*null\s*,', ': null,', response_text)
        response_text = re.sub(r':\s*null\s*}', ': null}', response_text)
        
        return response_text
    
    def create_default_products(self, invoices):
        """Create default products from invoice data"""
        products = []
        seen_products = set()
        
        for invoice in invoices:
            product_name = invoice.get('product_name', 'Unknown Product')
            if product_name not in seen_products:
                seen_products.add(product_name)
                
                # Calculate unit price from total and tax
                total = invoice.get('total_amount', 0)
                tax = invoice.get('tax', 0)
                quantity = invoice.get('quantity', 1)
                
                # Avoid division by zero
                if quantity == 0:
                    quantity = 1
                
                unit_price = round((total - tax) / quantity, 2)
                
                products.append({
                    'name': product_name,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'tax': tax,
                    'price_with_tax': total,
                    'discount': 0
                })
        
        return products
    
    def extract_from_dataframe(self, df):
        """Extract structured data directly from the pandas DataFrame"""
        invoices = []
        products = {}
        
        # Check if the DataFrame has the expected columns for invoice summary format
        invoice_summary_columns = ['Serial Number', 'Party Name', 'Net Amount', 'Tax Amount', 'Total Amount', 'Date']
        product_detail_columns = ['Serial Number', 'Invoice Date', 'Product Name', 'Qty', 'Price with Tax', 'Unit Price', 'Tax (%)']
        
        column_mapping = {}
        
        # Try to find matching columns (case-insensitive)
        for expected in invoice_summary_columns + product_detail_columns:
            for col in df.columns:
                if expected.lower() in col.lower():
                    column_mapping[expected] = col
                    break
        
        # Determine which format we're dealing with
        if all(col in column_mapping for col in ['Serial Number', 'Party Name', 'Net Amount', 'Tax Amount', 'Total Amount']):
            # This is an invoice summary format
            print("Processing invoice summary format")
            return self.process_invoice_summary(df, column_mapping)
        elif all(col in column_mapping for col in ['Serial Number', 'Product Name']):
            # This is a product detail format
            print("Processing product detail format")
            return self.process_product_detail(df, column_mapping)
        else:
            # Unknown format, try a more generic approach
            print("Unknown Excel format, using generic approach")
            return self.process_generic_format(df)

    def process_invoice_summary(self, df, column_mapping):
        """Process Excel file in invoice summary format"""
        invoices = []
        products = []
        customer_objects = []
        customer_totals = {}
        
        # Process each row
        for _, row in df.iterrows():
            # Skip rows with missing serial numbers or empty rows
            if pd.isna(row.get(column_mapping.get('Serial Number', ''))) or \
               str(row.get(column_mapping.get('Serial Number', ''))).strip() == '':
                continue
            
            # Extract invoice data
            serial_number = str(row.get(column_mapping.get('Serial Number', ''))).strip()
            
            # Get customer name - try Party Name first, then Party Company Name if available
            customer_name = ""
            if 'Party Name' in column_mapping and not pd.isna(row.get(column_mapping['Party Name'])):
                customer_name = str(row.get(column_mapping['Party Name'])).strip()
            
            if (not customer_name or customer_name == "") and 'Party Company Name' in column_mapping:
                company_name = row.get(column_mapping['Party Company Name'])
                if not pd.isna(company_name) and str(company_name).strip() != "":
                    customer_name = str(company_name).strip()
            
            # If still empty, use a default
            if not customer_name or customer_name == "":
                customer_name = f"Customer for {serial_number}"
            
            # Handle numeric values
            net_amount = 0
            tax_amount = 0
            total_amount = 0
            
            if 'Net Amount' in column_mapping:
                net_amount_val = row.get(column_mapping['Net Amount'])
                if not pd.isna(net_amount_val):
                    net_amount = float(net_amount_val)
            
            if 'Tax Amount' in column_mapping:
                tax_amount_val = row.get(column_mapping['Tax Amount'])
                if not pd.isna(tax_amount_val):
                    tax_amount = float(tax_amount_val)
            
            if 'Total Amount' in column_mapping:
                total_amount_val = row.get(column_mapping['Total Amount'])
                if not pd.isna(total_amount_val):
                    total_amount = float(total_amount_val)
            
            # Get date
            date = "Unknown Date"
            if 'Date' in column_mapping:
                date_val = row.get(column_mapping['Date'])
                if not pd.isna(date_val):
                    date = str(date_val)
            
            # Create a product name for this invoice that doesn't include "Invoice" prefix
            # This will make it clearer in the UI
            product_name = f"{serial_number} - Summary"
            
            # Add invoice
            invoices.append({
                "serial_number": serial_number,
                "customer_name": customer_name,
                "product_name": product_name,
                "quantity": 1.0,
                "tax": tax_amount,  # Use the actual tax amount from the Excel file
                "total_amount": total_amount,
                "date": date
            })
            
            # Add product
            products.append({
                "name": product_name,
                "quantity": 1.0,
                "unit_price": net_amount,
                "tax": tax_amount,  # Use the actual tax amount from the Excel file
                "price_with_tax": total_amount,
                "discount": 0
            })
            
            # Track customer totals
            if customer_name in customer_totals:
                customer_totals[customer_name] += total_amount
            else:
                customer_totals[customer_name] = total_amount
        
        # Create customer objects
        for customer_name, total_amount in customer_totals.items():
            customer_objects.append({
                "name": customer_name,
                "phone_number": None,
                "total_purchase_amount": total_amount,
                "address": None,
                "email": None
            })
        
        return {
            "invoices": invoices,
            "products": products,
            "customers": customer_objects
        }
    
    def process_product_detail(self, df, column_mapping):
        """Process Excel file in product detail format with line items"""
        invoices = []
        products = {}
        invoice_totals = {}
        customer_totals = {}
        
        # Process each row
        for _, row in df.iterrows():
            # Skip rows with missing serial numbers or empty rows
            if pd.isna(row.get(column_mapping.get('Serial Number', ''))) or \
               str(row.get(column_mapping.get('Serial Number', ''))).strip() == '':
                continue
            
            # Skip totals row if present
            serial_number = str(row.get(column_mapping.get('Serial Number', ''))).strip()
            if serial_number.lower() in ['total', 'totals', 'sum']:
                continue
            
            # Get date
            date = "Unknown Date"
            if 'Invoice Date' in column_mapping:
                date_val = row.get(column_mapping['Invoice Date'])
                if not pd.isna(date_val):
                    date = str(date_val)
            
            # Extract product data
            product_name = "Unknown Product"
            if 'Product Name' in column_mapping:
                product_name_val = row.get(column_mapping['Product Name'])
                if not pd.isna(product_name_val):
                    product_name = str(product_name_val).strip()
            
            # Extract quantity
            quantity = 1.0
            if 'Qty' in column_mapping:
                qty_val = row.get(column_mapping['Qty'])
                if not pd.isna(qty_val):
                    quantity = float(qty_val)
            
            # Extract price with tax
            price_with_tax = 0.0
            if 'Price with Tax' in column_mapping:
                price_val = row.get(column_mapping['Price with Tax'])
                if not pd.isna(price_val):
                    price_with_tax = float(price_val)
            
            # Extract unit price
            unit_price = 0.0
            if 'Unit Price' in column_mapping:
                unit_price_val = row.get(column_mapping['Unit Price'])
                if not pd.isna(unit_price_val):
                    unit_price = float(unit_price_val)
            
            # Extract tax percentage
            tax_percentage = 0.0
            if 'Tax (%)' in column_mapping:
                tax_val = row.get(column_mapping['Tax (%)'])
                if not pd.isna(tax_val):
                    tax_percentage = float(tax_val)
            
            # Calculate tax amount based on tax percentage
            tax_amount = 0.0
            if tax_percentage > 0:
                # Calculate tax amount from the unit price and tax percentage
                tax_amount = (unit_price * quantity * tax_percentage) / 100
            else:
                # If no tax percentage, calculate from price difference
                tax_amount = price_with_tax - (unit_price * quantity)
                if tax_amount < 0:
                    tax_amount = 0
            
            # Create a unique customer name for this invoice
            customer_name = f"Customer for {serial_number}"
            
            # Create or update product
            product_id = f"{product_name}-{unit_price}"
            if product_id not in products:
                products[product_id] = {
                    "name": product_name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "tax": tax_amount,
                    "price_with_tax": price_with_tax,
                    "discount": 0
                }
            else:
                # Update existing product
                products[product_id]["quantity"] += quantity
                products[product_id]["tax"] += tax_amount
                products[product_id]["price_with_tax"] += price_with_tax
            
            # Track invoice totals
            if serial_number not in invoice_totals:
                invoice_totals[serial_number] = {
                    "serial_number": serial_number,
                    "customer_name": customer_name,
                    "date": date,
                    "total_amount": 0,
                    "products": []
                }
            
            # Add product to invoice
            invoice_totals[serial_number]["products"].append({
                "product_name": product_name,
                "quantity": quantity,
                "tax": tax_amount,
                "total_amount": price_with_tax
            })
            
            # Update invoice total
            invoice_totals[serial_number]["total_amount"] += price_with_tax
            
            # Track customer totals
            if customer_name not in customer_totals:
                customer_totals[customer_name] = 0
            customer_totals[customer_name] += price_with_tax
        
        # Create invoice objects
        for serial_number, invoice_data in invoice_totals.items():
            for product in invoice_data["products"]:
                invoices.append({
                    'serial_number': serial_number,
                    'customer_name': invoice_data['customer_name'],
                    'product_name': product['product_name'],
                    'quantity': product['quantity'],
                    'tax': product['tax'],
                    'total_amount': product['total_amount'],
                    'date': invoice_data['date']
                })
        
        # Create customer objects
        customer_objects = []
        for customer_name, total_amount in customer_totals.items():
            customer_objects.append({
                "name": customer_name,
                "phone_number": None,
                "total_purchase_amount": total_amount,
                "address": None,
                "email": None
            })
        
        return {
            "invoices": invoices,
            "products": list(products.values()),
            "customers": customer_objects
        }
    
    def process_generic_format(self, df):
        """Process Excel file with unknown format"""
        invoices = []
        products = {}
        customers = set()
        
        # Try to identify key columns
        potential_serial_columns = []
        potential_product_columns = []
        potential_customer_columns = []
        potential_amount_columns = []
        potential_date_columns = []
        
        # Look for column names that might contain relevant data
        for col in df.columns:
            col_lower = col.lower()
            if any(term in col_lower for term in ['serial', 'invoice', 'bill', 'number']):
                potential_serial_columns.append(col)
            if any(term in col_lower for term in ['product', 'item', 'description', 'service']):
                potential_product_columns.append(col)
            if any(term in col_lower for term in ['customer', 'client', 'party', 'buyer', 'name']):
                potential_customer_columns.append(col)
            if any(term in col_lower for term in ['amount', 'total', 'price', 'value']):
                potential_amount_columns.append(col)
            if any(term in col_lower for term in ['date', 'time']):
                potential_date_columns.append(col)
        
        # Select the most likely columns
        serial_col = potential_serial_columns[0] if potential_serial_columns else None
        product_col = potential_product_columns[0] if potential_product_columns else None
        customer_col = potential_customer_columns[0] if potential_customer_columns else None
        amount_col = potential_amount_columns[0] if potential_amount_columns else None
        date_col = potential_date_columns[0] if potential_date_columns else None
        
        # Process each row if we have at least a serial number column
        if serial_col:
            for _, row in df.iterrows():
                # Skip rows with missing serial numbers or empty rows
                if pd.isna(row.get(serial_col)) or str(row.get(serial_col)).strip() == '':
                    continue
                
                # Extract data
                serial_number = str(row.get(serial_col)).strip()
                
                # Get product name
                product_name = "Unknown Product"
                if product_col and not pd.isna(row.get(product_col)):
                    product_name = str(row.get(product_col)).strip()
                
                # Get customer name
                customer_name = f"Customer for {serial_number}"
                if customer_col and not pd.isna(row.get(customer_col)):
                    customer_name = str(row.get(customer_col)).strip()
                
                # Get amount
                total_amount = 0.0
                if amount_col and not pd.isna(row.get(amount_col)):
                    try:
                        total_amount = float(row.get(amount_col))
                    except:
                        total_amount = 0.0
                
                # Get date
                date = "Unknown Date"
                if date_col and not pd.isna(row.get(date_col)):
                    date = str(row.get(date_col))
                
                # Create invoice
                invoices.append({
                    'serial_number': serial_number,
                    'customer_name': customer_name,
                    'product_name': product_name,
                    'quantity': 1.0,
                    'tax': 0.0,  # No tax info in generic format
                    'total_amount': total_amount,
                    'date': date
                })
                
                # Add customer
                if customer_name:
                    customers.add((customer_name, total_amount))
                
                # Add product
                product_key = f"{product_name}_{serial_number}"
                products[product_key] = {
                    'name': product_name,
                    'quantity': 1.0,
                    'unit_price': total_amount,  # Assume no tax in generic format
                    'tax': 0.0,
                    'price_with_tax': total_amount,
                    'discount': 0
                }
        
        # Create customer objects
        customer_objects = []
        customer_totals = {}
        
        # Calculate total purchase amount per customer
        for customer_name, total_amount in customers:
            if customer_name in customer_totals:
                customer_totals[customer_name] += total_amount
            else:
                customer_totals[customer_name] = total_amount
        
        # Create customer objects with total purchase amounts
        for customer_name, total_amount in customer_totals.items():
            customer_objects.append({
                "name": customer_name,
                "phone_number": None,
                "total_purchase_amount": total_amount,
                "address": None,
                "email": None
            })
        
        return {
            "invoices": invoices,
            "products": list(products.values()),
            "customers": customer_objects
        }
    
    async def extract(self, file_path: str) -> ExtractedData:
        try:
            # First try to read with pandas
            df = pd.read_excel(file_path)
            
            # Print column names for debugging
            print(f"Excel columns: {df.columns.tolist()}")
            
            # Try direct extraction from DataFrame first
            try:
                extracted_data = self.extract_from_dataframe(df)
                
                # Check if we got any data
                if (not extracted_data.get('invoices') and 
                    not extracted_data.get('products') and 
                    not extracted_data.get('customers')):
                    raise ValueError("No data extracted from DataFrame")
                
                # Preprocess the data
                extracted_data = self.preprocess_data(extracted_data)
                
                # Validate the data
                validation_errors = self.validate_data(extracted_data)
                
                return ExtractedData(
                    invoices=extracted_data.get('invoices', []),
                    products=extracted_data.get('products', []),
                    customers=extracted_data.get('customers', []),
                    validation_errors=validation_errors
                )
            except Exception as df_err:
                print(f"Direct DataFrame extraction failed: {str(df_err)}")
                print(f"Trying fallback method...")
                
                # Try a simpler approach - just extract what we can directly from the DataFrame
                try:
                    # Create a simple extraction based on column names
                    invoices = []
                    customers = set()
                    
                    # Check for key columns
                    if 'Serial Number' in df.columns and 'Party Name' in df.columns:
                        for _, row in df.iterrows():
                            # Skip rows with missing serial numbers or empty rows
                            if pd.isna(row.get('Serial Number')) or str(row.get('Serial Number')).strip() == '':
                                continue
                            
                            serial_number = str(row.get('Serial Number')).strip()
                            customer_name = str(row.get('Party Name')).strip()
                            
                            # Get other fields if available
                            tax_amount = float(row.get('Tax Amount', 0)) if not pd.isna(row.get('Tax Amount', 0)) else 0
                            total_amount = float(row.get('Total Amount', 0)) if not pd.isna(row.get('Total Amount', 0)) else 0
                            date = str(row.get('Date')) if not pd.isna(row.get('Date')) else "Unknown Date"
                            
                            # Create invoice
                            invoices.append({
                                "serial_number": serial_number,
                                "customer_name": customer_name if customer_name else f"Customer for {serial_number}",
                                "product_name": f"Invoice {serial_number} Items",
                                "quantity": 1.0,
                                "tax": tax_amount,
                                "total_amount": total_amount,
                                "date": date
                            })
                            
                            # Add customer
                            if customer_name:
                                customers.add((customer_name, total_amount))
                    
                    # Create products from invoices
                    products = []
                    for invoice in invoices:
                        products.append({
                            'name': invoice.get('product_name'),
                            'quantity': 1.0,
                            'unit_price': invoice.get('total_amount', 0) - invoice.get('tax', 0),
                            'tax': invoice.get('tax', 0),
                            'price_with_tax': invoice.get('total_amount', 0),
                            'discount': 0
                        })
                    
                    # Create customer objects
                    customer_objects = []
                    for customer_name, total_amount in customers:
                        customer_objects.append({
                            "name": customer_name,
                            "phone_number": None,
                            "total_purchase_amount": total_amount,
                            "address": None,
                            "email": None
                        })
                    
                    # Return the extracted data
                    return ExtractedData(
                        invoices=invoices,
                        products=products,
                        customers=customer_objects,
                        validation_errors=["Used simplified extraction due to format issues"]
                    )
                except Exception as simple_err:
                    print(f"Simple extraction failed: {str(simple_err)}")
        except Exception as e:
            print(f"Excel file reading error: {str(e)}")
            return ExtractedData(
                invoices=[],
                products=[],
                customers=[],
                validation_errors=[f"Error reading Excel file: {str(e)}"]
            )

    def detect_format(self, df):
        """Detect the format of the Excel file"""
        columns = df.columns.tolist()
        print(f"Excel columns: {columns}")
        
        # Check for product detail format (has Product Name, Qty, etc.)
        if 'Product Name' in columns and 'Qty' in columns:
            print("Processing product detail format")
            return 'product_detail', {
                'Serial Number': 'Serial Number',
                'Invoice Date': 'Invoice Date',
                'Product Name': 'Product Name',
                'Qty': 'Qty',
                'Price with Tax': 'Price with Tax',
                'Unit Price': 'Unit Price',
                'Tax (%)': 'Tax (%)'
            }
        
        # Check for invoice summary format (has Party Name, Net Amount, etc.)
        elif 'Serial Number' in columns and ('Party Name' in columns or 'Party Company Name' in columns):
            print("Processing invoice summary format")
            mapping = {
                'Serial Number': 'Serial Number',
                'Date': 'Date',
                'Net Amount': 'Net Amount',
                'Tax Amount': 'Tax Amount',
                'Total Amount': 'Total Amount'
            }
            
            if 'Party Name' in columns:
                mapping['Party Name'] = 'Party Name'
            
            if 'Party Company Name' in columns:
                mapping['Party Company Name'] = 'Party Company Name'
                
            return 'invoice_summary', mapping
        
        # Default to generic format
        else:
            print("Processing generic format")
            return 'generic', {} 