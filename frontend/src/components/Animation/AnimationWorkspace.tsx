import React, { useState, useEffect } from 'react';
import { Box, Grid, Paper, Typography } from '@mui/material';
import { CharacterPanel } from './CharacterPanel';
import { EffectsPanel } from './EffectsPanel';
import { EnvironmentPanel } from './EnvironmentPanel';
import { SoundPanel } from './SoundPanel';
import { Timeline } from './Timeline';
import { PreviewWindow } from './PreviewWindow';
import { useAnimation } from '../../hooks/useAnimation';

export const AnimationWorkspace: React.FC = () => {
    const { currentAnimation, saveAnimation } = useAnimation();
    const [isDirty, setIsDirty] = useState(false);

    useEffect(() => {
        const handleBeforeUnload = (e: BeforeUnloadEvent) => {
            if (isDirty) {
                e.preventDefault();
                e.returnValue = '';
            }
        };

        window.addEventListener('beforeunload', handleBeforeUnload);
        return () => window.removeEventListener('beforeunload', handleBeforeUnload);
    }, [isDirty]);

    return (
        <Box sx={{ flexGrow: 1, height: '100vh', overflow: 'hidden' }}>
            <Grid container spacing={2} sx={{ height: '100%' }}>
                {/* Left Panel - Asset Library */}
                <Grid item xs={3}>
                    <Paper sx={{ height: '100%', overflow: 'auto' }}>
                        <Typography variant="h6" sx={{ p: 2 }}>
                            Assets
                        </Typography>
                        <CharacterPanel />
                        <EffectsPanel />
                        <EnvironmentPanel />
                        <SoundPanel />
                    </Paper>
                </Grid>

                {/* Center Panel - Preview Window */}
                <Grid item xs={6}>
                    <Paper sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                        <PreviewWindow />
                        <Timeline />
                    </Paper>
                </Grid>

                {/* Right Panel - Properties */}
                <Grid item xs={3}>
                    <Paper sx={{ height: '100%', overflow: 'auto' }}>
                        <Typography variant="h6" sx={{ p: 2 }}>
                            Properties
                        </Typography>
                        {/* Properties panel content */}
                    </Paper>
                </Grid>
            </Grid>
        </Box>
    );
};
