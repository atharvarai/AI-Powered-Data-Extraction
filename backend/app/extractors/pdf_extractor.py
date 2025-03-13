import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from ..models import ExtractedData
from .base_extractor import BaseExtractor

load_dotenv()

class PDFExtractor(BaseExtractor):
    """Extract data from PDF files using Google Gemini"""
    
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    async def extract(self, file_path: str) -> ExtractedData:
        # Read the PDF file
        with open(file_path, 'rb') as f:
            data = f.read()
        
        # Process with Gemini
        prompt = """
        Extract the following information from this invoice PDF in JSON format:
        1. Invoice details: serial number, date, total amount, tax
        2. Customer details: name, phone number, address (if available)
        3. Product details: name, quantity, unit price, tax, price with tax
        
        Format the response as a valid JSON with three arrays: 'invoices', 'products', and 'customers'.
        Each invoice should have: serial_number, customer_name, product_name, quantity, tax, total_amount, date
        Each product should have: name, quantity, unit_price, tax, price_with_tax, discount (optional)
        Each customer should have: name, phone_number, total_purchase_amount, address (optional), email (optional)
        
        IMPORTANT: Return ONLY the JSON object, no other text.
        """
        
        try:
            response = self.model.generate_content([
                prompt,
                {"mime_type": "application/pdf", "data": data}
            ])
            
            # Extract JSON from the response
            response_text = response.text
            
            # Clean up the response to get valid JSON
            # Remove markdown code block indicators if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Parse the JSON
            extracted_json = json.loads(response_text)
            
            # Preprocess the data
            extracted_json = self.preprocess_data(extracted_json)
            
            # Validate the data
            validation_errors = self.validate_data(extracted_json)
            
            # Create the ExtractedData object
            return ExtractedData(
                invoices=extracted_json.get('invoices', []),
                products=extracted_json.get('products', []),
                customers=extracted_json.get('customers', []),
                validation_errors=validation_errors
            )
        except Exception as e:
            print(f"PDF extraction error: {str(e)}")
            print(f"Response text: {response.text if 'response' in locals() else 'No response'}")
            return ExtractedData(
                invoices=[],
                products=[],
                customers=[],
                validation_errors=[f"Error extracting data from PDF: {str(e)}"]
            ) 