import React, { useState, useEffect } from 'react';
import { Box, Paper, Typography, Button, Chip, Stack, Divider, LinearProgress } from '@mui/material';
import { styled } from '@mui/material/styles';
import SecurityIcon from '@mui/icons-material/Security';
import WarningIcon from '@mui/icons-material/Warning';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import TimelineIcon from '@mui/icons-material/Timeline';
import { triggerPipeline, getDriftLogs, getContainers, getPolicies } from '../services/api';

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
    <Box sx={{ display: 'flex', flexDirection: 'column' }}>
      <Typography variant="body2" color={active ? 'primary' : 'text.secondary'} sx={{ fontWeight: active ? 600 : 400 }}>
        {step}
      </Typography>
    </Box>
    {!last && (
      <Box sx={{ flex: 1, mx: 1 }}>
        <Divider sx={{ borderColor: completed ? '#4caf50' : '#e0e0e0', borderWidth: 2 }} />
      </Box>
    )}
  </Box>
);

const PipelineStatus = ({ currentStep }: { currentStep: number }) => {
  const steps = [
    { id: 1, name: 'Intent Validated' },
    { id: 2, name: 'Policies Compiled' },
    { id: 3, name: 'Traffic Captured' },
    { id: 4, name: 'Drift Detected' },
    { id: 5, name: 'Rules Enforced' },
  ];

  return (
    <Box width="100%">
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3, width: '100%' }}>
        {steps.map((step, index) => (
          <PipelineStep
            key={step.id}
            step={(index + 1).toString()}
            completed={index < currentStep}
            active={index === currentStep}
            last={index === steps.length - 1}
          />
        ))}
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
        {steps.map((step, index) => (
          <Typography
            key={step.id}
            variant="caption"
            color={index < currentStep ? 'success.main' : index === currentStep ? 'primary.main' : 'text.secondary'}
            fontWeight={index === currentStep ? 600 : 400}
          >
            {step.name}
          </Typography>
        ))}
      </Box>
    </Box>
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

const Overview = () => {
  const [containers, setContainers] = useState<any[]>([]);
  const [driftCount, setDriftCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [score, setScore] = useState(100);
  const [pipelineStep, setPipelineStep] = useState(5); // Default to all done

  const fetchData = async () => {
    try {
      const [cnts, drifts, pols] = await Promise.all([
        getContainers(),
        getDriftLogs(),
        getPolicies()
      ]);

      const uiContainers = cnts.map((c: any) => ({
        id: c.name,
        name: c.name,
        allowedDomains: ['(managed by policy)'],
        allowedPorts: ['(auto-detected)'],
        expectedBehavior: c.image,
        status: c.status
      }));

      setContainers(uiContainers);

      const dCount = (Array.isArray(drifts) ? drifts : []).length;

      // Calculate penalties
      let penalty = 0;

      // 1. Drift Penalty (10 pts each)
      penalty += (dCount * 10);

      // 2. Dangerous Ports Penalty (20 pts each)
      // Iterate over policies to find warnings
      let dangerousCount = 0;
      if (Array.isArray(pols)) {
        pols.forEach((p: any) => {
          if (p.metadata?.annotations?.security_risk === 'High') {
            dangerousCount++;
          }
        });
      }
      penalty += (dangerousCount * 20);

      // 3. Unauthorized Container Penalty (Check drift logs for "Undeclared: ALL")
      if (Array.isArray(drifts)) {
        drifts.forEach((d: any) => {
          if (d.undeclared_ports && d.undeclared_ports.includes('ALL')) {
            penalty += 40; // Extra penalty for rogue containers
          }
        });
      }

      setScore(Math.max(0, 100 - penalty));
      setDriftCount(dCount);

    } catch (e) {
      console.error("Failed to fetch dashboard data", e);
    }
  };



  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleRunPipeline = async () => {
    setLoading(true);
    setPipelineStep(0); // Reset steps

    // Optimistic progress indicator
    const progressTimer = setInterval(() => {
      setPipelineStep(prev => Math.min(prev + 1, 4));
    }, 800);

    try {
      await triggerPipeline();
      setPipelineStep(5);
      await fetchData();
    } catch (e: any) {
      console.error(e);
      alert("Pipeline failed to start: " + (e.message || "Unknown error"));
      setPipelineStep(0); // Reset on error
    } finally {
      clearInterval(progressTimer);
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h5" fontWeight={600} mb={3}>
        Security Dashboard Overview
      </Typography>

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '2fr 1fr' }, gap: 3, mb: 3 }}>
        <Box>
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
                onClick={handleRunPipeline}
                disabled={loading}
                sx={{ textTransform: 'none', borderRadius: '20px' }}
              >
                {loading ? 'Running...' : 'Run Full Pipeline'}
              </Button>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <Typography variant="body2" color="text.secondary">
                Pipeline checks intent, compiles policies, captures traffic, detects drift, and enforces rules.
              </Typography>
            </Box>
            <PipelineStatus currentStep={pipelineStep} />
          </Item>
        </Box>
        <Box>
          <Item>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6" fontWeight={600}>Score</Typography>
              <Typography variant="h4" color={score > 80 ? 'success.main' : 'warning.main'}>{score}</Typography>
            </Box>
            <LinearProgress variant="determinate" value={score} color={score > 80 ? 'success' : 'warning'} />
            <Box display="flex" justifyContent="space-between" mt={1}>
              <Typography variant="caption" color="text.secondary">
                {score >= 90 ? 'Excellent' : score >= 70 ? 'Good' : 'Needs Attention'}
              </Typography>
            </Box>
          </Item>
        </Box>
      </Box>

      {driftCount > 0 && (
        <Item sx={{ backgroundColor: '#fff8e1', mb: 3 }}>
          <Box display="flex" alignItems="center" mb={1}>
            <WarningIcon color="warning" sx={{ mr: 1 }} />
            <Typography variant="subtitle1" fontWeight={600}>
              Drift Detected
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" mb={2}>
            {driftCount} drift events detected across containers.
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
      )}

      <Typography variant="h6" mt={4} mb={2} fontWeight={600}>
        Active Live Containers
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
