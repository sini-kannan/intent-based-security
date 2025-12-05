import React from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, Button, Divider } from '@mui/material';
import { styled } from '@mui/material/styles';
import WarningIcon from '@mui/icons-material/Warning';
import DownloadIcon from '@mui/icons-material/Download';
import TimelineIcon from '@mui/icons-material/Timeline';

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(3),
  color: theme.palette.text.secondary,
  borderRadius: '10px',
  boxShadow: '0 4px 20px 0 rgba(0,0,0,0.05)',
  marginBottom: theme.spacing(3),
}));

const StyledTable = styled(Table)({
  minWidth: 650,
  '& .MuiTableCell-head': {
    fontWeight: 600,
    backgroundColor: '#f5f5f5',
  },
});

const DriftStatus = ({ status }: { status: 'high' | 'medium' | 'low' }) => {
  const statusConfig = {
    high: { label: 'High', color: 'error' },
    medium: { label: 'Medium', color: 'warning' },
    low: { label: 'Low', color: 'info' },
  };

  return (
    <Chip
      label={statusConfig[status].label}
      color={statusConfig[status].color as any}
      size="small"
      variant="outlined"
    />
  );
};

const DriftAnalysis = () => {
  // Mock data - replace with actual data from your backend
  const driftData = [
    {
      id: 1,
      container: 'frontend-app',
      timestamp: '2025-12-05T14:30:00Z',
      type: 'Undeclared Port',
      details: 'Port 22 (SSH) detected but not declared',
      status: 'high',
    },
    {
      id: 2,
      container: 'api-service',
      timestamp: '2025-12-05T13:15:00Z',
      type: 'Unexpected Domain',
      details: 'Connection to external-api.unknown.com',
      status: 'medium',
    },
    {
      id: 3,
      container: 'database',
      timestamp: '2025-12-05T12:00:00Z',
      type: 'Excessive Access',
      details: 'Multiple connections from non-whitelisted IPs',
      status: 'high',
    },
  ];

  const driftStats = {
    totalDrifts: 12,
    highSeverity: 5,
    mediumSeverity: 4,
    lowSeverity: 3,
    containersAffected: 4,
    lastUpdated: '2025-12-05T15:45:00Z',
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight={600}>
          Drift Analysis
        </Typography>
        <Button
          variant="outlined"
          startIcon={<DownloadIcon />}
          sx={{ textTransform: 'none', borderRadius: '20px' }}
        >
          Export Report
        </Button>
      </Box>

      <Item>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Box>
            <Typography variant="h6" fontWeight={600}>
              Drift Overview
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Last updated: {new Date(driftStats.lastUpdated).toLocaleString()}
            </Typography>
          </Box>
          <Box display="flex" gap={2}>
            <Box textAlign="center">
              <Typography variant="h4" color="error.main">
                {driftStats.highSeverity}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                High Severity
              </Typography>
            </Box>
            <Box textAlign="center">
              <Typography variant="h4" color="warning.main">
                {driftStats.mediumSeverity}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Medium
              </Typography>
            </Box>
            <Box textAlign="center">
              <Typography variant="h4" color="info.main">
                {driftStats.lowSeverity}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Low
              </Typography>
            </Box>
          </Box>
        </Box>

        <Divider sx={{ my: 2 }} />

        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="subtitle1" fontWeight={600}>
            Recent Drift Events
          </Typography>
          <Button
            variant="text"
            size="small"
            endIcon={<TimelineIcon />}
            sx={{ textTransform: 'none' }}
          >
            View All ({driftStats.totalDrifts})
          </Button>
        </Box>

        <TableContainer component={Paper} elevation={0} sx={{ borderRadius: '8px', border: '1px solid rgba(0,0,0,0.12)' }}>
          <StyledTable>
            <TableHead>
              <TableRow>
                <TableCell>Container</TableCell>
                <TableCell>Type</TableCell>
                <TableCell>Details</TableCell>
                <TableCell>Timestamp</TableCell>
                <TableCell>Severity</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {driftData.map((row) => (
                <TableRow key={row.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight={500}>
                      {row.container}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={row.type}
                      size="small"
                      variant="outlined"
                      color="default"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">{row.details}</Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {new Date(row.timestamp).toLocaleString()}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <DriftStatus status={row.status as any} />
                  </TableCell>
                  <TableCell>
                    <Button size="small" color="primary" sx={{ textTransform: 'none' }}>
                      View
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </StyledTable>
        </TableContainer>
      </Item>

      <Item>
        <Typography variant="h6" fontWeight={600} mb={2}>
          Drift Over Time
        </Typography>
        <Box height={300} display="flex" alignItems="center" justifyContent="center" bgcolor="#f9f9f9" borderRadius={2}>
          <Box textAlign="center">
            <TimelineIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
            <Typography color="text.secondary">Drift trend visualization will appear here</Typography>
            <Typography variant="caption" color="text.secondary">
              (This would show the number of drifts detected over time)
            </Typography>
          </Box>
        </Box>
      </Item>

      <Item>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" fontWeight={600}>
            Container Drift Summary
          </Typography>
          <Button size="small" color="primary" sx={{ textTransform: 'none' }}>
            View All Containers
          </Button>
        </Box>
        <Box display="flex" gap={2} flexWrap="wrap">
          {Array.from({ length: 4 }).map((_, index) => (
            <Paper
              key={index}
              sx={{
                p: 2,
                flex: 1,
                minWidth: 200,
                borderLeft: '4px solid',
                borderColor: index % 3 === 0 ? 'error.main' : index % 3 === 1 ? 'warning.main' : 'info.main',
              }}
              elevation={0}
            >
              <Typography variant="subtitle2" color="text.secondary">
                container-{index + 1}
              </Typography>
              <Box display="flex" alignItems="center" mt={1}>
                <WarningIcon
                  color={index % 3 === 0 ? 'error' : index % 3 === 1 ? 'warning' : 'info'}
                  fontSize="small"
                  sx={{ mr: 1 }}
                />
                <Typography variant="h6">
                  {index * 2 + 3} drifts
                </Typography>
              </Box>
              <Typography variant="caption" color="text.secondary">
                Last detected: 2h ago
              </Typography>
            </Paper>
          ))}
        </Box>
      </Item>
    </Box>
  );
};

export default DriftAnalysis;
