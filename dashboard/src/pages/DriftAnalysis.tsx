import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, Button, Divider } from '@mui/material';
import { styled } from '@mui/material/styles';
import WarningIcon from '@mui/icons-material/Warning';
import DownloadIcon from '@mui/icons-material/Download';
import TimelineIcon from '@mui/icons-material/Timeline';
import { getDriftLogs } from '../services/api';

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
  const [driftData, setDriftData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDrift = async () => {
      try {
        const data = await getDriftLogs();
        const formatted = Array.isArray(data) ? data.map((d: any, idx: number) => {
          const ports = (d.bad_ports || []).filter((p: number) => p > 0);
          return {
            id: idx,
            container: d.container || 'unknown',
            timestamp: d.time || new Date().toISOString(),
            type: 'Undeclared Port',
            details: ports.length > 0 ? `Ports: ${ports.join(', ')}` : 'No drift detected',
            status: ports.length > 3 ? 'high' : ports.length > 0 ? 'medium' : 'low',
          };
        }) : [];
        setDriftData(formatted);
      } catch (e) {
        console.error('Failed to fetch drift:', e);
        setDriftData([]);
      } finally {
        setLoading(false);
      }
    };
    fetchDrift();
    const interval = setInterval(fetchDrift, 10000);
    return () => clearInterval(interval);
  }, []);

  const driftStats = {
    totalDrifts: driftData.length,
    highSeverity: driftData.filter(d => d.status === 'high').length,
    mediumSeverity: driftData.filter(d => d.status === 'medium').length,
    lowSeverity: driftData.filter(d => d.status === 'low').length,
    containersAffected: new Set(driftData.map(d => d.container)).size,
    lastUpdated: new Date().toISOString(),
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
