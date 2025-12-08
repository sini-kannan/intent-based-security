import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { AppBar, Toolbar, Typography, Container, Box, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Divider } from '@mui/material';
import DashboardIcon from '@mui/icons-material/Dashboard';
import SecurityIcon from '@mui/icons-material/Security';
import TimelineIcon from '@mui/icons-material/Timeline';
import SettingsIcon from '@mui/icons-material/Settings';
import HomeIcon from '@mui/icons-material/Home';

// Pages
import Overview from './pages/Overview';
import DriftAnalysis from './pages/DriftAnalysis';
import EnforcementRules from './pages/EnforcementRules';
import Settings from './pages/Settings';
import IntentInput from './pages/IntentInput';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';

const drawerWidth = 240;

type MenuItem = {
  text: string;
  icon: React.ReactNode;
  path: string;
};

const menuItems: MenuItem[] = [
  { text: 'Overview', icon: <HomeIcon />, path: '/' },
  { text: 'New Intent', icon: <AddCircleOutlineIcon />, path: '/intent' },
  { text: 'Drift Analysis', icon: <TimelineIcon />, path: '/drift' },
  { text: 'Enforcement Rules', icon: <SecurityIcon />, path: '/rules' },
  { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
];

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: [
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Roboto',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif',
    ].join(','),
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <AppContent />
      </Router>
    </ThemeProvider>
  );
}

function AppContent() {
  const location = useLocation();

  return (
    <Box sx={{ display: 'flex' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: `calc(100% - ${drawerWidth}px)`,
          ml: `${drawerWidth}px`,
          backgroundColor: 'white',
          color: 'black',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        }}
      >
        <Toolbar>
          <Typography variant="h6" noWrap component="div">
            Intent-Based Security Dashboard
          </Typography>
          <Box sx={{ flexGrow: 1 }} />
          <Typography variant="body2" color="text.secondary">
            Last updated: {new Date().toLocaleString()}
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Sidebar */}
      <Drawer
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: drawerWidth,
            boxSizing: 'border-box',
            bgcolor: '#1e293b',
            color: 'white',
          },
        }}
        variant="permanent"
        anchor="left"
      >
        <Toolbar>
          <DashboardIcon sx={{ mr: 2 }} />
          <Typography variant="h6" noWrap component="div">
            Security Dashboard
          </Typography>
        </Toolbar>
        <Divider sx={{ bgcolor: 'rgba(255,255,255,0.1)' }} />
        <List>
          {menuItems.map((item) => (
            <ListItem
              key={item.text}
              disablePadding
              sx={{
                color: 'rgba(255, 255, 255, 0.7)',
                '& .MuiListItemButton-root': {
                  color: 'inherit',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    color: 'white',
                    // ... existing styles ...
                  },
                  '&.Mui-selected': {
                    backgroundColor: 'rgba(25, 118, 210, 0.2)',
                    color: 'white',
                    '&:hover': {
                      backgroundColor: 'rgba(25, 118, 210, 0.3)',
                    },
                  },
                },
              }}
            >
              <ListItemButton
                component={Link}
                to={item.path}
                selected={location.pathname === item.path}
                sx={{
                  width: '100%',
                  padding: '8px 16px',
                }}
              >
                <ListItemIcon sx={{ color: 'inherit', minWidth: 40 }}>{item.icon}</ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Drawer>

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          bgcolor: 'background.default',
          p: 3,
          marginTop: '64px',
          minHeight: 'calc(100vh - 64px)',
        }}
      >
        <Container maxWidth="xl">
          <Routes>
            <Route path="/" element={<Overview />} />
            <Route path="/intent" element={<IntentInput />} />
            <Route path="/drift" element={<DriftAnalysis />} />
            <Route path="/rules" element={<EnforcementRules />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Container>
      </Box>
    </Box>
  );
}

export default App;
