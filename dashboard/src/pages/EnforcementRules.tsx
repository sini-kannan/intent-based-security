import React from 'react';
import { Box, Typography, Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Chip, Button, Divider, Switch, FormControlLabel } from '@mui/material';
import { styled } from '@mui/material/styles';
import SecurityIcon from '@mui/icons-material/Security';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import BlockIcon from '@mui/icons-material/Block';

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

const RuleStatus = ({ enforced }: { enforced: boolean }) => (
  <Chip
    icon={enforced ? <CheckCircleIcon fontSize="small" /> : <WarningIcon fontSize="small" />}
    label={enforced ? 'Enforced' : 'Not Enforced'}
    color={enforced ? 'success' : 'warning'}
    variant="outlined"
    size="small"
  />
);

const ActionChip = ({ action }: { action: 'ALLOW' | 'DENY' }) => (
  <Chip
    icon={action === 'ALLOW' ? <CheckCircleIcon fontSize="small" /> : <BlockIcon fontSize="small" />}
    label={action}
    color={action === 'ALLOW' ? 'success' : 'error'}
    variant="outlined"
    size="small"
  />
);

const EnforcementRules = () => {
  // Mock data - replace with actual data from your backend
  const rules = [
    {
      id: 1,
      container: 'frontend-app',
      source: '0.0.0.0/0',
      destination: '0.0.0.0/0',
      protocol: 'tcp',
      port: '80,443',
      action: 'ALLOW',
      enforced: true,
      lastUpdated: '2025-12-05T14:30:00Z',
    },
    {
      id: 2,
      container: 'api-service',
      source: 'frontend-app',
      destination: 'api-service',
      protocol: 'tcp',
      port: '3000',
      action: 'ALLOW',
      enforced: true,
      lastUpdated: '2025-12-05T14:25:00Z',
    },
    {
      id: 3,
      container: 'database',
      source: 'api-service',
      destination: 'database',
      protocol: 'tcp',
      port: '5432',
      action: 'ALLOW',
      enforced: true,
      lastUpdated: '2025-12-05T14:20:00Z',
    },
    {
      id: 4,
      container: '*',
      source: '*',
      destination: '*',
      protocol: '*',
      port: '22',
      action: 'DENY',
      enforced: true,
      lastUpdated: '2025-12-05T14:15:00Z',
    },
  ];

  const [enforcementEnabled, setEnforcementEnabled] = React.useState(true);

  const handleToggleEnforcement = (event: React.ChangeEvent<HTMLInputElement>) => {
    setEnforcementEnabled(event.target.checked);
    // Here you would typically make an API call to update enforcement status
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h5" fontWeight={600}>
            Enforcement Rules
          </Typography>
          <Typography variant="body2" color="text.secondary">
            View and manage your security enforcement rules
          </Typography>
        </Box>
        <FormControlLabel
          control={
            <Switch
              checked={enforcementEnabled}
              onChange={handleToggleEnforcement}
              color="primary"
            />
          }
          label={
            <Box display="flex" alignItems="center">
              <SecurityIcon
                color={enforcementEnabled ? 'success' : 'disabled'}
                fontSize="small"
                sx={{ mr: 1 }}
              />
              <Typography variant="body2">
                {enforcementEnabled ? 'Enforcement Active' : 'Enforcement Paused'}
              </Typography>
            </Box>
          }
        />
      </Box>

      <Item>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h6" fontWeight={600}>
            Active Rules
          </Typography>
          <Box>
            <Button
              variant="outlined"
              size="small"
              sx={{ textTransform: 'none', borderRadius: '20px', mr: 1 }}
            >
              Export Rules
            </Button>
            <Button
              variant="contained"
              size="small"
              sx={{ textTransform: 'none', borderRadius: '20px' }}
            >
              Add Rule
            </Button>
          </Box>
        </Box>

        <TableContainer component={Paper} elevation={0} sx={{ borderRadius: '8px', border: '1px solid rgba(0,0,0,0.12)' }}>
          <StyledTable>
            <TableHead>
              <TableRow>
                <TableCell>Container</TableCell>
                <TableCell>Source</TableCell>
                <TableCell>Destination</TableCell>
                <TableCell>Protocol</TableCell>
                <TableCell>Port(s)</TableCell>
                <TableCell>Action</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Last Updated</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rules.map((rule) => (
                <TableRow key={rule.id} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight={500}>
                      {rule.container}
                    </Typography>
                  </TableCell>
                  <TableCell>{rule.source}</TableCell>
                  <TableCell>{rule.destination}</TableCell>
                  <TableCell>{rule.protocol.toUpperCase()}</TableCell>
                  <TableCell>{rule.port}</TableCell>
                  <TableCell>
                    <ActionChip action={rule.action as 'ALLOW' | 'DENY'} />
                  </TableCell>
                  <TableCell>
                    <RuleStatus enforced={rule.enforced} />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" color="text.secondary">
                      {new Date(rule.lastUpdated).toLocaleString()}
                    </Typography>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </StyledTable>
        </TableContainer>
      </Item>

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' }, gap: 3, mb: 3 }}>
        <Box>
          <Item>
            <Typography variant="h6" fontWeight={600} mb={2}>
              Default Policy
            </Typography>
            <Typography variant="body2" mb={3}>
              The default policy is applied to all traffic that doesn't match any other rules.
            </Typography>
            <Box display="flex" alignItems="center" justifyContent="space-between">
              <Box>
                <Typography variant="subtitle2" color="text.secondary">
                  Default Action
                </Typography>
                <Typography variant="h6">Deny All</Typography>
              </Box>
              <Button variant="outlined" size="small" sx={{ textTransform: 'none', borderRadius: '20px' }}>
                Change Policy
              </Button>
            </Box>
          </Item>
        </Box>
        <Box>
          <Item>
            <Typography variant="h6" fontWeight={600} mb={2}>
              Rule Statistics
            </Typography>
            <Box display="flex" justifyContent="space-around" textAlign="center">
              <Box>
                <Typography variant="h4" color="success.main">
                  {rules.filter(r => r.action === 'ALLOW').length}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Allow Rules
                </Typography>
              </Box>
              <Box>
                <Typography variant="h4" color="error.main">
                  {rules.filter(r => r.action === 'DENY').length}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Deny Rules
                </Typography>
              </Box>
              <Box>
                <Typography variant="h4" color="primary.main">
                  {rules.length}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Total Rules
                </Typography>
              </Box>
            </Box>
          </Item>
        </Box>
      </Box>
    </Box>
  );
};

export default EnforcementRules;
