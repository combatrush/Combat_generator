import React, { Component, ErrorInfo, ReactNode } from 'react';
import Box from '@mui/material/Box';
import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Paper from '@mui/material/Paper';

interface Props {
    children: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null,
        errorInfo: null
    };

    public static getDerivedStateFromError(error: Error): State {
        return {
            hasError: true,
            error,
            errorInfo: null
        };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Error caught by boundary:', error, errorInfo);
        this.setState({
            error,
            errorInfo
        });
    }

    private handleReset = () => {
        this.setState({
            hasError: false,
            error: null,
            errorInfo: null
        });
    };

    public render() {
        if (this.state.hasError) {
            return (
                <Box component={Paper} sx={{ p: 3, m: 2 }}>
                    <Alert severity="error" sx={{ mb: 2 }}>
                        <Typography variant="h6" gutterBottom>
                            Something went wrong
                        </Typography>
                        <Typography variant="body2" gutterBottom>
                            {this.state.error?.message}
                        </Typography>
                    </Alert>
                    
                    {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
                        <Box sx={{ mt: 2, mb: 2 }}>
                            <Typography variant="subtitle2" color="text.secondary">
                                Component Stack:
                            </Typography>
                            <pre style={{ 
                                whiteSpace: 'pre-wrap',
                                fontSize: '0.875rem',
                                color: 'text.secondary'
                            }}>
                                {this.state.errorInfo.componentStack}
                            </pre>
                        </Box>
                    )}
                    
                    <Button 
                        variant="contained" 
                        color="primary"
                        onClick={this.handleReset}
                        sx={{ mt: 2 }}
                    >
                        Try Again
                    </Button>
                </Box>
            );
        }

        return this.props.children;
    }
}
