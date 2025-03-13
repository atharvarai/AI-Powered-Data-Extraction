import React, { useState, useCallback } from 'react';
import { useDispatch } from 'react-redux';
import { useDropzone } from 'react-dropzone';
import { uploadAndExtractData } from '../redux/thunks';
import { 
  Box, 
  Typography, 
  Button, 
  Paper, 
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemText
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

const FileUpload = () => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState([]);
  
  const onDrop = useCallback(async (acceptedFiles) => {
    if (acceptedFiles.length === 0) return;
    
    setLoading(true);
    setErrors([]);
    
    try {
      const validationErrors = await dispatch(uploadAndExtractData(acceptedFiles[0]));
      if (validationErrors && validationErrors.length > 0) {
        setErrors(validationErrors);
      }
    } catch (error) {
      setErrors([error.message || 'Error uploading file']);
    } finally {
      setLoading(false);
    }
  }, [dispatch]);
  
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
      'application/vnd.ms-excel': ['.xls']
    },
    maxFiles: 1
  });
  
  return (
    <Box sx={{ mb: 4 }}>
      <Paper
        {...getRootProps()}
        sx={{
          p: 3,
          textAlign: 'center',
          cursor: 'pointer',
          backgroundColor: isDragActive ? '#f0f8ff' : 'white',
          border: '2px dashed #ccc',
          borderColor: isDragActive ? 'primary.main' : '#ccc',
          borderRadius: 2,
          mb: 2
        }}
      >
        <input {...getInputProps()} />
        <CloudUploadIcon sx={{ fontSize: 48, color: 'primary.main', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {isDragActive ? 'Drop the file here' : 'Drag & drop a file here, or click to select'}
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Supported formats: PDF, JPG, PNG, XLSX, XLS
        </Typography>
        {loading && (
          <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
            <CircularProgress size={24} />
          </Box>
        )}
      </Paper>
      
      {errors.length > 0 && (
        <Alert severity="warning" sx={{ mt: 2 }}>
          <Typography variant="subtitle1">Validation Issues:</Typography>
          <List dense>
            {errors.map((error, index) => (
              <ListItem key={index}>
                <ListItemText primary={error} />
              </ListItem>
            ))}
          </List>
        </Alert>
      )}
      
      <Box sx={{ mt: 2, textAlign: 'center' }}>
        <Button
          variant="contained"
          color="primary"
          {...getRootProps()}
          disabled={loading}
        >
          {loading ? 'Processing...' : 'Upload File'}
        </Button>
      </Box>
    </Box>
  );
};

export default FileUpload; 