import React from 'react';
import { Paper, Typography } from '@mui/material';

export const SoundPanel: React.FC = () => {
  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Typography variant="h6" gutterBottom>
        Sound
      </Typography>
      {/* Add sound controls here */}
    </Paper>
  );
};
