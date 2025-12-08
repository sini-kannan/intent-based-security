import React, { useState, useEffect } from 'react';
import { createIntent, listIntents, Intent } from '../services/api';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  CircularProgress,
  Alert,
  Snackbar,
  TableContainer,
  Table,
  TableHead,
  TableRow,
  TableCell,
  TableBody,
  TablePagination,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';

const EnforcementRules: React.FC = () => {
  const [intentText, setIntentText] = useState('');
  const [containerName, setContainerName] = useState('my-container');
  const [intents, setIntents] = useState<Intent[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(5);

  const loadIntents = async () => {
    try {
      setIsLoading(true);
      const data = await listIntents();
      setIntents(data);
    } catch (err) {
      setError('Failed to load intents');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadIntents();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!intentText.trim()) return;

    try {
      setIsCreating(true);
      setError(null);
      await createIntent(intentText, containerName);
      setSuccess('Intent created successfully!');
      setIntentText('');
      await loadIntents();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create intent');
    } finally {
      setIsCreating(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this intent?')) {
      try {
        // In a real app, you would call deleteIntent(id) here
        setIntents(intents.filter(intent => intent.id !== id));
        setSuccess('Intent deleted successfully!');
      } catch (err) {
        setError('Failed to delete intent');
        console.error(err);
      }
    }
  };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Intent-Based Security Rules
      </Typography>

      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Create New Intent
        </Typography>
        <form onSubmit={handleSubmit}>
          <Box display="flex" gap={2} alignItems="flex-start">
            <TextField
              label="Container Name"
              value={containerName}
              onChange={(e) => setContainerName(e.target.value)}
              size="small"
              sx={{ width: 200 }}
              required
            />
            <TextField
              label="Intent Description"
              value={intentText}
              onChange={(e) => setIntentText(e.target.value)}
              fullWidth
              multiline
              rows={1}
              placeholder="e.g., My container needs to access web services and connect to PostgreSQL"
              required
              size="small"
            />
            <Button
              type="submit"
              variant="contained"
              color="primary"
              disabled={isCreating}
              startIcon={isCreating ? <CircularProgress size={20} /> : <AddIcon />}
              sx={{ height: 40 }}
            >
              {isCreating ? 'Creating...' : 'Create'}
            </Button>
          </Box>
        </form>
      </Paper>

      <Typography variant="h6" gutterBottom>
        Existing Intents
      </Typography>
      <Paper elevation={3} sx={{ width: '100%', overflow: 'hidden' }}>
        <TableContainer sx={{ maxHeight: 440 }}>
          <Table stickyHeader aria-label="intents table">
            <TableHead>
              <TableRow>
                <TableCell>Container</TableCell>
                <TableCell>Intent</TableCell>
                <TableCell>Generated YAML</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={4} align="center">
                    <CircularProgress />
                  </TableCell>
                </TableRow>
              ) : (
                intents
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((intent) => (
                    <TableRow key={intent.id}>
                      <TableCell>
                        <Chip 
                          label={intent.container_name} 
                          color="primary" 
                          variant="outlined" 
                          size="small" 
                        />
                      </TableCell>
                      <TableCell>{intent.text}</TableCell>
                      <TableCell>
                        <Box 
                          component="pre" 
                          sx={{ 
                            margin: 0, 
                            whiteSpace: 'pre-wrap',
                            fontFamily: 'monospace',
                            fontSize: '0.8rem',
                            maxHeight: '100px',
                            overflow: 'auto',
                            p: 1,
                            bgcolor: 'action.hover',
                            borderRadius: 1
                          }}
                        >
                          {intent.yaml_content}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Tooltip title="Delete intent">
                          <IconButton 
                            onClick={() => handleDelete(intent.id)}
                            color="error"
                            size="small"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={intents.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
      >
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!success}
        autoHideDuration={6000}
        onClose={() => setSuccess(null)}
      >
        <Alert severity="success" onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default EnforcementRules;
