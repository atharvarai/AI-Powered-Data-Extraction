# Invoice Data Extraction System

A modern web application that extracts and organizes invoice data from various file formats (PDF, images, Excel) using AI-powered data extraction.

## Features

- **Multi-format Support**: Extract data from PDF, image (JPG, PNG), and Excel (XLSX, XLS) files
- **AI-powered Extraction**: Uses Google's Gemini AI for complex document understanding
- **Data Organization**: Automatically categorizes extracted data into invoices, products, and customers
- **Search Functionality**: Easily search through extracted data
- **Data Editing**: Edit extracted information directly in the UI
- **Validation**: Automatic validation of extracted data with error reporting
- **Responsive UI**: Modern, user-friendly interface built with Material UI

## Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **Google Gemini AI**: For advanced document understanding and data extraction
- **Pandas**: For Excel file processing
- **PyPDF2**: For PDF file handling
- **Pillow**: For image processing

### Frontend
- **React**: UI library for building the user interface
- **Redux Toolkit**: For state management
- **Material UI**: Component library for consistent design
- **React Dropzone**: For file upload functionality
- **Axios**: For API requests
- **React Toastify**: For notifications

## How It Works

1. **File Upload**: Users upload invoice files through the drag-and-drop interface
2. **Data Extraction**: 
   - PDF and image files are processed using Google Gemini AI
   - Excel files are processed using Pandas with format detection
3. **Data Organization**: Extracted data is organized into three categories:
   - Invoices: Contains invoice details like serial number, date, amount
   - Products: Contains product details like name, quantity, price
   - Customers: Contains customer information
4. **Data Display**: Information is displayed in searchable, editable tables
5. **Data Editing**: Users can edit any extracted information if needed

## Setup and Installation

### Prerequisites
- Python 3.8+
- Node.js 14+
- Google Gemini API key

### Backend Setup

1. Clone the repository
   ```bash
   git clone <repository-url>
   cd invoice-data-extraction
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install backend dependencies
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the backend directory with your Gemini API key
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. Test your Gemini API key
   ```bash
   python test_gemini.py
   ```

### Frontend Setup

1. Install frontend dependencies
   ```bash
   cd frontend
   npm install
   ```

## Running the Application

### Start the Backend Server
```bash
cd backend
uvicorn app.main:app --reload
```

The backend server will run at http://localhost:8000

### Start the Frontend Development Server
```bash
cd frontend
npm start
```

The frontend will run at http://localhost:3000

## Getting a Gemini API Key


- Go to [Google AI Studio] and create a new API key
- Copy the key and add it to your `.env` file