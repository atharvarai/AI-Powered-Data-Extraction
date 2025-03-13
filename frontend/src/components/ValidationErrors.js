import React from 'react';
import { Alert, List, ListItem, ListItemText, Typography } from '@mui/material';

const ValidationErrors = ({ errors }) => {
  if (!errors || errors.length === 0) {
    return null;
  }

  return (
    <Alert severity="warning" sx={{ mt: 2, mb: 2 }}>
      <Typography variant="subtitle1">Data Validation Issues:</Typography>
      <List dense>
        {errors.map((error, index) => (
          <ListItem key={index}>
            <ListItemText primary={error} />
          </ListItem>
        ))}
      </List>
    </Alert>
  );
};

export default ValidationErrors; 