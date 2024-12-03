import React from 'react';
import { Paper, Typography } from '@mui/material';

export const EffectsPanel: React.FC = () => {
  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Effects
      </Typography>
      {/* Add effects controls here */}
    </Paper>
  );
};
