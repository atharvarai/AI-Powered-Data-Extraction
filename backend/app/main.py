import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uuid
import logging
import traceback

from .models import ExtractedData
from .extractors import PDFExtractor, ImageExtractor, ExcelExtractor
from .utils import save_upload_file, get_file_type

app = FastAPI(title="Invoice Data Extraction API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

# Create upload directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.post("/api/extract", response_model=ExtractedData)
async def extract_data(file: UploadFile = File(...)):
    """
    Extract data from an uploaded file (PDF, image, or Excel)
    """
    # Save the uploaded file
    file_path = await save_upload_file(file, UPLOAD_DIR)
    logger.info(f"File saved to {file_path}")
    
    try:
        # Determine file type and use appropriate extractor
        file_type = get_file_type(file.filename)
        logger.info(f"Detected file type: {file_type}")
        
        if file_type == 'pdf':
            extractor = PDFExtractor()
            logger.info("Using PDF extractor")
        elif file_type == 'image':
            extractor = ImageExtractor()
            logger.info("Using Image extractor")
        elif file_type == 'excel':
            extractor = ExcelExtractor()
            logger.info("Using Excel extractor")
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_type}")
        
        # Extract data
        logger.info("Starting data extraction")
        extracted_data = await extractor.extract(file_path)
        
        # If we have validation errors but still have some data, continue processing
        if extracted_data.validation_errors and (extracted_data.invoices or extracted_data.products or extracted_data.customers):
            logger.warning(f"Extraction completed with warnings: {extracted_data.validation_errors}")
        elif extracted_data.validation_errors:
            logger.error(f"Extraction failed: {extracted_data.validation_errors}")
            return extracted_data
        
        # Add IDs to the extracted data
        for invoice in extracted_data.invoices:
            if not invoice.id:
                invoice.id = str(uuid.uuid4())
        
        for product in extracted_data.products:
            if not product.id:
                product.id = str(uuid.uuid4())
        
        for customer in extracted_data.customers:
            if not customer.id:
                customer.id = str(uuid.uuid4())
        
        # Link invoices to products and customers
        for invoice in extracted_data.invoices:
            # Find matching product
            for product in extracted_data.products:
                if product.name == invoice.product_name:
                    invoice.product_id = product.id
                    break
            
            # Find matching customer
            for customer in extracted_data.customers:
                if customer.name == invoice.customer_name:
                    invoice.customer_id = customer.id
                    break
        
        return extracted_data
    
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
        # Clean up the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 