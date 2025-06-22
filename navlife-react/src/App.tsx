import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline, Box, Container, Alert, CircularProgress } from '@mui/material';
import { apiService, BCHealthCheck } from './services/api';
import Navbar from './components/Navbar';
import WeatherTab from './components/WeatherTab';
import FoodTab from './components/FoodTab';
import TransportTab from './components/TransportTab';
import ResearchTab from './components/ResearchTab';
import FullCrewTab from './components/FullCrewTab';
import BCInfoTab from './components/BCInfoTab';
import SafetyTab from './components/SafetyTab';

// Create theme
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
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          borderRadius: 12,
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
  },
});

function App() {
  const [bcHealth, setBcHealth] = useState<BCHealthCheck | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await apiService.checkBCHealth();
        setBcHealth(health);
      } catch (error) {
        console.error('Health check failed:', error);
        setBcHealth({
          status: 'unhealthy',
          message: 'Failed to check BC CrewAI API health'
        });
      } finally {
        setLoading(false);
      }
    };

    checkHealth();
  }, []);

  const getStatusAlert = () => {
    if (loading) {
      return (
        <Box display="flex" justifyContent="center" alignItems="center" p={2}>
          <CircularProgress size={24} sx={{ mr: 2 }} />
          Checking system status...
        </Box>
      );
    }

    if (!bcHealth) {
      return (
        <Alert severity="error" sx={{ mb: 2 }}>
          Unable to check system status
        </Alert>
      );
    }

    if (bcHealth.status === 'healthy') {
      return (
        <Alert severity="success" sx={{ mb: 2 }}>
          ✅ <strong>All Systems Available</strong><br />
          Enhanced Safety Routing + BC CrewAI API + Google Maps Router initialized successfully
        </Alert>
      );
    } else {
      return (
        <Alert severity="warning" sx={{ mb: 2 }}>
          ⚠️ <strong>Partial System Available</strong><br />
          {bcHealth.message}
        </Alert>
      );
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ minHeight: '100vh', backgroundColor: 'background.default' }}>
          <Navbar />
          <Container maxWidth="lg" sx={{ mt: 2, mb: 4 }}>
            {getStatusAlert()}
            <Routes>
              <Route path="/" element={<WeatherTab />} />
              <Route path="/weather" element={<WeatherTab />} />
              <Route path="/food" element={<FoodTab />} />
              <Route path="/transport" element={<TransportTab />} />
              <Route path="/research" element={<ResearchTab />} />
              <Route path="/full-crew" element={<FullCrewTab />} />
              <Route path="/bc-info" element={<BCInfoTab />} />
              <Route path="/safety" element={<SafetyTab />} />
            </Routes>
          </Container>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
