import React, { useState } from 'react';
import { Box, Typography, Paper, Divider, TextField, Button, Switch, FormControlLabel, Tabs, Tab, List, ListItem, ListItemText, IconButton, ListItemSecondaryAction, Alert } from '@mui/material';
import { styled } from '@mui/material/styles';
import DeleteIcon from '@mui/icons-material/Delete';
import AddIcon from '@mui/icons-material/Add';
import SaveIcon from '@mui/icons-material/Save';
import SecurityIcon from '@mui/icons-material/Security';
import NotificationsIcon from '@mui/icons-material/Notifications';
import CodeIcon from '@mui/icons-material/Code';

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.mode === 'dark' ? '#1A2027' : '#fff',
  ...theme.typography.body2,
  padding: theme.spacing(3),
  color: theme.palette.text.secondary,
  borderRadius: '10px',
  boxShadow: '0 4px 20px 0 rgba(0,0,0,0.05)',
  marginBottom: theme.spacing(3),
}));

const StyledTabs = styled(Tabs)({
  '& .MuiTabs-indicator': {
    backgroundColor: '#1976d2',
  },
  marginBottom: '20px',
});

const StyledTab = styled(Tab)({
  textTransform: 'none',
  minWidth: 0,
  marginRight: '24px',
  '&:hover': {
    opacity: 1,
  },
  '&.Mui-selected': {
    color: '#1976d2',
    fontWeight: 600,
  },
});

const Settings = () => {
  const [tabValue, setTabValue] = useState(0);
  const [notifications, setNotifications] = useState({
    securityAlerts: true,
    policyChanges: true,
    weeklyReports: false,
  });
  
  const [badPorts, setBadPorts] = useState([22, 23, 25, 53, 135, 137, 138, 139, 445, 1433, 1434, 3306, 3389, 5432]);
  const [newPort, setNewPort] = useState('');
  const [apiKey, setApiKey] = useState('sk_test_51JkL...');
  const [settingsSaved, setSettingsSaved] = useState(false);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleNotificationChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setNotifications({
      ...notifications,
      [event.target.name]: event.target.checked,
    });
  };

  const handleAddBadPort = () => {
    if (newPort && !badPorts.includes(Number(newPort))) {
      setBadPorts([...badPorts, Number(newPort)].sort((a, b) => a - b));
      setNewPort('');
    }
  };

  const handleRemoveBadPort = (port: number) => {
    setBadPorts(badPorts.filter(p => p !== port));
  };

  const handleSaveSettings = () => {
    // Here you would typically make an API call to save the settings
    setSettingsSaved(true);
    setTimeout(() => setSettingsSaved(false), 3000);
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5" fontWeight={600}>
          Settings
        </Typography>
        <Button
          variant="contained"
          startIcon={<SaveIcon />}
          onClick={handleSaveSettings}
          sx={{ textTransform: 'none', borderRadius: '20px' }}
        >
          Save Changes
        </Button>
      </Box>

      {settingsSaved && (
        <Alert severity="success" sx={{ mb: 3 }}>
          Settings saved successfully!
        </Alert>
      )}

      <StyledTabs
        value={tabValue}
        onChange={handleTabChange}
        aria-label="settings tabs"
      >
        <StyledTab icon={<SecurityIcon />} label="Security" />
        <StyledTab icon={<NotificationsIcon />} label="Notifications" />
        <StyledTab icon={<CodeIcon />} label="API" />
      </StyledTabs>

      {tabValue === 0 && (
        <Box>
          <Item>
            <Typography variant="h6" fontWeight={600} mb={3}>
              Port Configuration
            </Typography>
            
            <Typography variant="subtitle2" color="text.secondary" mb={2}>
              Bad Ports (Automatically Blocked)
            </Typography>
            <Typography variant="body2" color="text.secondary" mb={2}>
              These ports are considered high-risk and will be automatically blocked by the system.
            </Typography>
            
            <Box display="flex" mb={3}>
              <TextField
                label="Add port to block"
                type="number"
                size="small"
                value={newPort}
                onChange={(e) => setNewPort(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAddBadPort()}
                sx={{ width: 200, mr: 2 }}
                InputProps={{
                  inputProps: { min: 1, max: 65535 },
                }}
              />
              <Button
                variant="outlined"
                startIcon={<AddIcon />}
                onClick={handleAddBadPort}
                sx={{ textTransform: 'none', borderRadius: '20px' }}
              >
                Add Port
              </Button>
            </Box>
            
            <List dense sx={{ bgcolor: 'background.paper', borderRadius: 1, border: '1px solid rgba(0,0,0,0.12)' }}>
              {badPorts.map((port) => (
                <ListItem key={port} divider>
                  <ListItemText primary={`Port ${port}`} />
                  <ListItemSecondaryAction>
                    <IconButton
                      edge="end"
                      aria-label="delete"
                      onClick={() => handleRemoveBadPort(port)}
                      size="small"
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </Item>
          
          <Item>
            <Typography variant="h6" fontWeight={600} mb={2}>
              Security Policies
            </Typography>
            <FormControlLabel
              control={
                <Switch
                  checked={true}
                  name="enabled"
                  color="primary"
                  disabled
                />
              }
              label="Enable automatic drift detection"
              sx={{ mb: 1 }}
            />
            <Typography variant="body2" color="text.secondary" mb={2} ml={4}>
              Automatically detect and alert on configuration drift
            </Typography>
            
            <FormControlLabel
              control={
                <Switch
                  checked={true}
                  name="enabled"
                  color="primary"
                />
              }
              label="Enforce security policies"
              sx={{ mb: 1 }}
            />
            <Typography variant="body2" color="text.secondary" mb={2} ml={4}>
              Automatically block traffic that violates security policies
            </Typography>
            
            <FormControlLabel
              control={
                <Switch
                  checked={false}
                  name="enabled"
                  color="primary"
                />
              }
              label="Require approval for policy changes"
              sx={{ mb: 1 }}
            />
            <Typography variant="body2" color="text.secondary" ml={4}>
              Require manual approval for all security policy changes
            </Typography>
          </Item>
        </Box>
      )}

      {tabValue === 1 && (
        <Item>
          <Typography variant="h6" fontWeight={600} mb={3}>
            Notification Preferences
          </Typography>
          
          <FormControlLabel
            control={
              <Switch
                checked={notifications.securityAlerts}
                onChange={handleNotificationChange}
                name="securityAlerts"
                color="primary"
              />
            }
            label="Security Alerts"
            sx={{ mb: 1, display: 'block' }}
          />
          <Typography variant="body2" color="text.secondary" mb={2} ml={4}>
            Receive immediate alerts for security incidents and policy violations
          </Typography>
          
          <FormControlLabel
            control={
              <Switch
                checked={notifications.policyChanges}
                onChange={handleNotificationChange}
                name="policyChanges"
                color="primary"
              />
            }
            label="Policy Change Notifications"
            sx={{ mb: 1, display: 'block' }}
          />
          <Typography variant="body2" color="text.secondary" mb={2} ml={4}>
            Get notified when security policies are modified
          </Typography>
          
          <FormControlLabel
            control={
              <Switch
                checked={notifications.weeklyReports}
                onChange={handleNotificationChange}
                name="weeklyReports"
                color="primary"
              />
            }
            label="Weekly Security Reports"
            sx={{ mb: 1, display: 'block' }}
          />
          <Typography variant="body2" color="text.secondary" mb={2} ml={4}>
            Receive a weekly summary of security events and policy violations
          </Typography>
          
          <TextField
            label="Notification Email"
            defaultValue="admin@example.com"
            fullWidth
            margin="normal"
            size="small"
          />
        </Item>
      )}

      {tabValue === 2 && (
        <Item>
          <Typography variant="h6" fontWeight={600} mb={2}>
            API Access
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={3}>
            Use the API to programmatically manage your security policies and monitor compliance.
          </Typography>
          
          <Box mb={3}>
            <Typography variant="subtitle2" color="text.secondary" mb={1}>
              API Key
            </Typography>
            <Box display="flex" alignItems="center">
              <TextField
                value={apiKey}
                size="small"
                fullWidth
                disabled
                sx={{ mr: 2 }}
                InputProps={{
                  style: { fontFamily: 'monospace' },
                }}
              />
              <Button variant="outlined" size="small" sx={{ textTransform: 'none', borderRadius: '20px' }}>
                Regenerate
              </Button>
            </Box>
            <Typography variant="caption" color="text.secondary">
              Keep your API key secure and do not share it publicly
            </Typography>
          </Box>
          
          <Divider sx={{ my: 3 }} />
          
          <Typography variant="subtitle1" fontWeight={600} mb={2}>
            API Documentation
          </Typography>
          <Typography variant="body2" color="text.secondary" mb={3}>
            For detailed API documentation and examples, please visit our API reference.
          </Typography>
          
          <Button
            variant="contained"
            color="primary"
            href="/api-docs"
            target="_blank"
            sx={{ textTransform: 'none', borderRadius: '20px' }}
          >
            View API Documentation
          </Button>
        </Item>
      )}
    </Box>
  );
};

export default Settings;
