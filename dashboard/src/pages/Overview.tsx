import React from 'react';
import { Box, Grid, Paper, Typography, Card, CardContent, LinearProgress, Button, Chip, Stack, Divider } from '@mui/material';
import { styled } from '@mui/material/styles';
import SecurityIcon from '@mui/icons-material/Security';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import TimelineIcon from '@mui/icons-material/Timeline';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(3),
  color: theme.palette.text.secondary,
  height: '100%',
  borderRadius: '10px',
  boxShadow: '0 4px 20px 0 rgba(0,0,0,0.05)',
}));

const PipelineStep = ({ step, completed, active, last }: { step: string; completed: boolean; active: boolean; last?: boolean }) => (
  <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
    <Box
      sx={{
        width: 32,
        height: 32,
        borderRadius: '50%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: completed ? '#4caf50' : active ? '#1976d2' : '#e0e0e0',
        color: completed || active ? 'white' : 'rgba(0,0,0,0.6)',
        fontWeight: 'bold',
        mr: 1,
      }}
    >
      {completed ? '✓' : step}
    </Box>
    <Typography variant="body2" color={active ? 'primary' : 'text.secondary'} sx={{ fontWeight: active ? 600 : 400 }}>
      {step}
    </Typography>
    {!last && (
      <Box sx={{ flex: 1, mx: 1 }}>
        <Divider sx={{ borderColor: completed ? '#4caf50' : '#e0e0e0', borderWidth: 2 }} />
      </Box>
    )}
  </Box>
);

const PipelineStatus = () => {
  const steps = [
    { id: 1, name: 'Intent Validated', completed: true },
    { id: 2, name: 'Policies Compiled', completed: true },
    { id: 3, name: 'Traffic Captured', completed: true },
    { id: 4, name: 'Drift Detected', completed: true },
    { id: 5, name: 'Rules Enforced', completed: false },
  ];

  return (
    <Item>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" fontWeight={600}>
          Security Pipeline Status
        </Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<PlayArrowIcon />}
          size="small"
          sx={{ textTransform: 'none', borderRadius: '20px' }}
        >
          Run Full Pipeline
        </Button>
      </Box>
      
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        {steps.map((step, index) => (
          <PipelineStep
            key={step.id}
            step={(index + 1).toString()}
            completed={step.completed}
            active={!step.completed && (index === 0 || steps[index - 1]?.completed)}
            last={index === steps.length - 1}
          />
        ))}
      </Box>
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
        {steps.map((step) => (
          <Typography key={step.id} variant="caption" color={step.completed ? 'success.main' : 'text.secondary'}>
            {step.name}
          </Typography>
        ))}
      </Box>
    </Item>
  );
};

const SecurityScoreCard = () => {
  const score = 85; // This would come from your data
  const getColor = (score: number) => {
    if (score >= 90) return 'success.main';
    if (score >= 70) return 'info.main';
    if (score >= 50) return 'warning.main';
    return 'error.main';
  };

  return (
    <Item>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" fontWeight={600}>
          Security Score
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <SecurityIcon color={score >= 90 ? 'success' : score >= 70 ? 'info' : score >= 50 ? 'warning' : 'error'} />
          <Typography variant="h4" ml={1} color={getColor(score)}>
            {score}
          </Typography>
          <Typography variant="body2" color="text.secondary" ml={1}>
            /100
          </Typography>
        </Box>
      </Box>
      <LinearProgress
        variant="determinate"
        value={score}
        sx={{
          height: 10,
          borderRadius: 5,
          backgroundColor: '#e0e0e0',
          '& .MuiLinearProgress-bar': {
            backgroundColor: getColor(score),
            borderRadius: 5,
          },
        }}
      />
      <Box display="flex" justifyContent="space-between" mt={1}>
        <Typography variant="caption" color="text.secondary">
          {score >= 90
            ? 'Excellent security posture'
            : score >= 70
            ? 'Good security posture'
            : score >= 50
            ? 'Needs attention'
            : 'Critical issues detected'}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Last updated: {new Date().toLocaleTimeString()}
        </Typography>
      </Box>
    </Item>
  );
};

const IntentSummaryCard = ({ container }: { container: any }) => (
  <Item>
    <Typography variant="h6" fontWeight={600} mb={2}>
      {container.name}
    </Typography>
    
    <Box mb={2}>
      <Typography variant="subtitle2" color="text.secondary" mb={1}>
        🌐 Allowed Domains
      </Typography>
      <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
        {container.allowedDomains.map((domain: string, index: number) => (
          <Chip key={index} label={domain} size="small" variant="outlined" />
        ))}
      </Stack>
    </Box>
    
    <Box mb={2}>
      <Typography variant="subtitle2" color="text.secondary" mb={1}>
        🔌 Allowed Ports
      </Typography>
      <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
        {container.allowedPorts.map((port: number, index: number) => (
          <Chip key={index} label={port} size="small" color="primary" variant="outlined" />
        ))}
      </Stack>
    </Box>
    
    <Box>
      <Typography variant="subtitle2" color="text.secondary" mb={1}>
        📝 Expected Behavior
      </Typography>
      <Typography variant="body2">{container.expectedBehavior}</Typography>
    </Box>
  </Item>
);

const DriftAlertCard = () => (
  <Item sx={{ backgroundColor: '#fff8e1' }}>
    <Box display="flex" alignItems="center" mb={1}>
      <WarningIcon color="warning" sx={{ mr: 1 }} />
      <Typography variant="subtitle1" fontWeight={600}>
        Drift Detected
      </Typography>
    </Box>
    <Typography variant="body2" color="text.secondary" mb={2}>
      3 containers have configuration drift from their intended state
    </Typography>
    <Button
      variant="outlined"
      color="warning"
      size="small"
      endIcon={<TimelineIcon />}
      sx={{ textTransform: 'none', borderRadius: '20px' }}
    >
      View Drift Analysis
    </Button>
  </Item>
);

const Overview = () => {
  // Mock data - replace with actual data from your backend
  const containers = [
    {
      id: 1,
      name: 'frontend-app',
      allowedDomains: ['api-service', 'cdn.example.com'],
      allowedPorts: [80, 443],
      expectedBehavior: 'Web traffic only (HTTP/HTTPS) to backend services and CDN',
    },
    {
      id: 2,
      name: 'api-service',
      allowedDomains: ['database', 'auth-service', 'redis'],
      allowedPorts: [5432, 6379, 3000],
      expectedBehavior: 'Database access and internal service communication only',
    },
  ];

  return (
    <Box>
      <Typography variant="h5" fontWeight={600} mb={3}>
        Security Dashboard Overview
      </Typography>
      
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '2fr 1fr' }, gap: 3, mb: 3 }}>
        <Box>
          <PipelineStatus />
        </Box>
        <Box>
          <SecurityScoreCard />
        </Box>
      </Box>
      
      <DriftAlertCard />
      
      <Typography variant="h6" mt={4} mb={2} fontWeight={600}>
        Container Intent Summary
      </Typography>
      
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' }, gap: 3 }}>
        {containers.map((container) => (
          <Box key={container.id}>
            <IntentSummaryCard container={container} />
          </Box>
        ))}
      </Box>
    </Box>
  );
};

export default Overview;
