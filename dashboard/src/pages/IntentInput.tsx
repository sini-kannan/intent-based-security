import React, { useState } from 'react';
import { Box, TextField, Button, Typography, Paper, Alert, CircularProgress, Divider } from '@mui/material';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import SaveIcon from '@mui/icons-material/Save';
import { createIntent } from '../services/api';

const IntentInput = () => {
    const [intentText, setIntentText] = useState('');
    const [containerName, setContainerName] = useState('my-container');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState('');

    const handleSubmit = async () => {
        if (!intentText.trim()) return;

        setLoading(true);
        setError('');
        setResult(null);

        try {
            const data = await createIntent(intentText, containerName);
            setResult(data);
        } catch (err: any) {
            setError(err.message || 'Failed to process intent');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Box maxWidth="800px" mx="auto">
            <Typography variant="h5" fontWeight={600} mb={3}>
                Define New Security Intent
            </Typography>

            <Paper sx={{ p: 4, mb: 4 }}>
                <Typography variant="subtitle1" mb={2} color="text.secondary">
                    Describe what your container needs to do in plain English.
                </Typography>

                <Box mb={3}>
                    <TextField
                        label="Container Name"
                        fullWidth
                        value={containerName}
                        onChange={(e) => setContainerName(e.target.value)}
                        variant="outlined"
                        size="small"
                        sx={{ mb: 2 }}
                    />

                    <TextField
                        label="Natural Language Intent"
                        multiline
                        rows={4}
                        fullWidth
                        placeholder="e.g. My container needs to use web services and connect to a postgres database."
                        value={intentText}
                        onChange={(e) => setIntentText(e.target.value)}
                        variant="outlined"
                    />
                </Box>

                <Button
                    variant="contained"
                    startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <AutoFixHighIcon />}
                    onClick={handleSubmit}
                    disabled={loading || !intentText.trim()}
                    size="large"
                >
                    {loading ? 'Processing...' : 'Generate Policy'}
                </Button>
            </Paper>

            {error && (
                <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>
            )}

            {result && (
                <Box>
                    <Typography variant="h6" mb={2}>Generated Policy</Typography>

                    {/* Warning Display */}
                    {result.yaml_content.includes("annotations") && result.yaml_content.includes("warnings") && (
                        <Alert severity="warning" sx={{ mb: 2 }}>
                            <strong>Security Warning Detected:</strong>
                            <pre style={{ whiteSpace: 'pre-wrap', margin: 0 }}>
                                {result.yaml_content.split('warnings:')[1]?.split('\n')[0].replace(/"/g, '')}
                            </pre>
                        </Alert>
                    )}

                    <Paper sx={{ p: 3, bgcolor: '#1e1e1e', color: '#d4d4d4', fontFamily: 'monospace' }}>
                        <pre style={{ margin: 0, overflowX: 'auto' }}>
                            {result.yaml_content}
                        </pre>
                    </Paper>

                    <Button
                        variant="contained"
                        color="success"
                        startIcon={<SaveIcon />}
                        sx={{ mt: 3 }}
                        onClick={() => alert('Policy saved to /policies/ directory!')}
                    >
                        Apply Policy
                    </Button>
                </Box>
            )}
        </Box>
    );
};

export default IntentInput;
