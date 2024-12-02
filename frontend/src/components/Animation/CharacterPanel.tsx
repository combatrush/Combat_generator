import React from 'react';
import { FC, ChangeEvent, useCallback, useState } from 'react';
import {
    Box,
    Button,
    TextField,
    Select,
    MenuItem,
    FormControl,
    InputLabel,
    Typography,
    Paper,
    Alert,
    CircularProgress,
    Snackbar,
    AlertProps,
    SelectChangeEvent,
    AlertColor
} from '@mui/material';

import { useCharacterGenerator } from '../../hooks/useCharacterGenerator';
import { ErrorBoundary } from '../ErrorBoundary';
import type { CharacterStyle } from '../../types/animation';

interface CharacterPanelProps {
    onCharacterGenerated?: ((characterId: string) => void) | undefined;
}

interface SnackbarState {
    open: boolean;
    message: string;
    severity?: AlertColor;
}

export const CharacterPanel: FC<CharacterPanelProps> = ({ onCharacterGenerated }) => {
    const [prompt, setPrompt] = useState<string>('');
    const [style, setStyle] = useState<CharacterStyle>('modern');
    const [snackbar, setSnackbar] = useState<SnackbarState>({
        open: false,
        message: '',
        severity: 'info'
    });
    
    const { generateCharacter, loading, error, clearError } = useCharacterGenerator();

    const handlePromptChange = useCallback((e: ChangeEvent<HTMLInputElement>) => {
        setPrompt(e.target.value);
        if (error) clearError();
    }, [error, clearError]);

    const handleStyleChange = useCallback((event: SelectChangeEvent) => {
        setStyle(event.target.value as CharacterStyle);
        if (error) clearError();
    }, [error, clearError]);

    const handleCloseSnackbar = useCallback(() => {
        setSnackbar((prev: SnackbarState) => ({ ...prev, open: false }));
    }, []);

    const validateForm = useCallback((): boolean => {
        if (!prompt.trim()) {
            setSnackbar({
                open: true,
                message: 'Please enter a character description',
                severity: 'warning'
            });
            return false;
        }
        return true;
    }, [prompt]);

    const handleGenerate = useCallback(async () => {
        if (!validateForm()) return;
        
        try {
            const result = await generateCharacter(prompt, style);
            setSnackbar({
                open: true,
                message: `Character ${result.id} generated successfully!`,
                severity: 'success'
            });
            
            if (onCharacterGenerated) {
                onCharacterGenerated(result.id);
            }
            
            // Clear form after successful generation
            setPrompt('');
        } catch (err) {
            console.error('Failed to generate character:', err);
            setSnackbar({
                open: true,
                message: error || 'Failed to generate character. Please try again.',
                severity: 'error'
            });
        }
    }, [prompt, style, generateCharacter, validateForm, onCharacterGenerated, error]);

    const handleKeyPress = useCallback((e: React.KeyboardEvent<HTMLDivElement>) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            handleGenerate();
        }
    }, [handleGenerate]);

    return (
        <ErrorBoundary>
            <Box component={Paper} sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>
                    Character Generator
                </Typography>
                
                {error && (
                    <Alert 
                        severity="error" 
                        sx={{ mb: 2 }}
                        onClose={clearError}
                    >
                        {error}
                    </Alert>
                )}
                
                <TextField
                    fullWidth
                    label="Character Description"
                    multiline
                    rows={4}
                    value={prompt}
                    onChange={handlePromptChange}
                    onKeyPress={handleKeyPress}
                    margin="normal"
                    error={!prompt.trim() && prompt !== ''}
                    helperText={!prompt.trim() && prompt !== '' ? 'Description is required' : 'Press Ctrl+Enter to generate'}
                    disabled={loading}
                    placeholder="Describe your character's appearance, personality, and abilities..."
                />
                
                <FormControl fullWidth margin="normal">
                    <InputLabel id="style-select-label">Style</InputLabel>
                    <Select
                        labelId="style-select-label"
                        id="style-select"
                        value={style}
                        label="Style"
                        onChange={handleStyleChange}
                        disabled={loading}
                    >
                        <MenuItem value="modern">Modern</MenuItem>
                        <MenuItem value="fantasy">Fantasy</MenuItem>
                        <MenuItem value="sci-fi">Sci-Fi</MenuItem>
                        <MenuItem value="historical">Historical</MenuItem>
                    </Select>
                </FormControl>
                
                <Button
                    variant="contained"
                    onClick={handleGenerate}
                    disabled={!prompt.trim() || loading}
                    fullWidth
                    sx={{ mt: 2 }}
                >
                    {loading ? (
                        <>
                            <CircularProgress size={24} sx={{ mr: 1 }} color="inherit" />
                            Generating...
                        </>
                    ) : (
                        'Generate Character'
                    )}
                </Button>

                <Snackbar
                    open={snackbar.open}
                    autoHideDuration={6000}
                    onClose={handleCloseSnackbar}
                    anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
                >
                    <Alert 
                        onClose={handleCloseSnackbar} 
                        severity={snackbar.severity}
                        variant="filled"
                        sx={{ width: '100%' }}
                    >
                        {snackbar.message}
                    </Alert>
                </Snackbar>
            </Box>
        </ErrorBoundary>
    );
};
