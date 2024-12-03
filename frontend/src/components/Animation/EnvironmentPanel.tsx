import React from 'react';
import { Paper, Typography } from '@mui/material';

export const EnvironmentPanel: React.FC = () => {
  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Environment
      </Typography>
      {/* Add environment controls here */}
    </Paper>
  );
};
