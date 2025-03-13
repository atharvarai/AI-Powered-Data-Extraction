import os
import uuid
from fastapi import UploadFile
import aiofiles

async def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    """Save an uploaded file to the specified destination."""
    # Create destination directory if it doesn't exist
    os.makedirs(destination, exist_ok=True)
    
    # Generate a unique filename
    file_extension = os.path.splitext(upload_file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(destination, unique_filename)
    
    # Save the file
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await upload_file.read()
        await out_file.write(content)
    
    return file_path

def get_file_type(filename: str) -> str:
    """Determine the type of file based on its extension."""
    extension = os.path.splitext(filename)[1].lower()
    
    if extension in ['.pdf']:
        return 'pdf'
    elif extension in ['.jpg', '.jpeg', '.png']:
        return 'image'
    elif extension in ['.xlsx', '.xls']:
        return 'excel'
    else:
        return 'unknown' 