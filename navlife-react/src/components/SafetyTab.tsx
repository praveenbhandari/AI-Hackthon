import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Box,
  Grid,
  Paper,
  Alert,
  CircularProgress,
  Chip,
  Slider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Security as SafetyIcon,
  ExpandMore as ExpandMoreIcon,
  LocationOn as LocationIcon,
  Route as RouteIcon,
  Warning as WarningIcon,
  CheckCircle as SuccessIcon,
} from '@mui/icons-material';
import { apiService } from '../services/api';

const SafetyTab: React.FC = () => {
  // Enhanced Route Finding State
  const [startLat, setStartLat] = useState(37.7694);
  const [startLng, setStartLng] = useState(-122.4862);
  const [endLat, setEndLat] = useState(37.8087);
  const [endLng, setEndLng] = useState(-122.4098);
  const [safetyWeight, setSafetyWeight] = useState(0.7);
  const [maxDistanceFactor, setMaxDistanceFactor] = useState(2.0);

  // Safety Info Checker State
  const [checkLat, setCheckLat] = useState(37.7749);
  const [checkLng, setCheckLng] = useState(-122.4194);

  // Results State
  const [enhancedRouteData, setEnhancedRouteData] = useState<any>(null);
  const [safetyInfoData, setSafetyInfoData] = useState<any>(null);
  const [loadingEnhanced, setLoadingEnhanced] = useState(false);
  const [loadingSafetyInfo, setLoadingSafetyInfo] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFindEnhancedRoute = async () => {
    setLoadingEnhanced(true);
    setError(null);
    setEnhancedRouteData(null);

    try {
      const data = await apiService.getEnhancedSafetyRoute(
        startLat,
        startLng,
        endLat,
        endLng,
        safetyWeight,
        maxDistanceFactor
      );
      setEnhancedRouteData(data);
      if (!data.success) {
        setError(data.message || 'Failed to find enhanced safety route');
      }
    } catch (err) {
      setError('An error occurred while finding enhanced safety route');
      console.error('Enhanced Safety Route API error:', err);
    } finally {
      setLoadingEnhanced(false);
    }
  };

  const handleCheckSafetyInfo = async () => {
    setLoadingSafetyInfo(true);
    setError(null);
    setSafetyInfoData(null);

    try {
      const data = await apiService.getSafetyInfo(checkLat, checkLng);
      setSafetyInfoData(data);
      if (!data.success) {
        setError(data.message || 'Failed to get safety information');
      }
    } catch (err) {
      setError('An error occurred while getting safety information');
      console.error('Safety Info API error:', err);
    } finally {
      setLoadingSafetyInfo(false);
    }
  };

  const renderEnhancedRouteResults = (routeData: any) => {
    if (!routeData) return null;

    return (
      <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <RouteIcon color="primary" />
          Enhanced Route Results
        </Typography>

        {routeData.route && (
          <Box sx={{ mb: 3 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Route Summary
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Safety Score:</strong> {routeData.route.safety_score?.toFixed(2) || 'N/A'}
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Distance:</strong> {routeData.route.distance || 'N/A'}
                </Typography>
                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Duration:</strong> {routeData.route.duration || 'N/A'}
                </Typography>
                <Typography variant="body2">
                  <strong>Safety Weight Used:</strong> {safetyWeight}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <Typography variant="subtitle1" gutterBottom>
                  Route Details
                </Typography>
                {routeData.route.steps && routeData.route.steps.length > 0 && (
                  <Box>
                    <Typography variant="body2" gutterBottom>
                      <strong>Steps:</strong> {routeData.route.steps.length}
                    </Typography>
                    {routeData.route.steps.slice(0, 3).map((step: any, index: number) => (
                      <Typography key={index} variant="body2" color="text.secondary" sx={{ fontSize: '0.875rem' }}>
                        {index + 1}. {step.instruction || step.description || `Step ${index + 1}`}
                      </Typography>
                    ))}
                    {routeData.route.steps.length > 3 && (
                      <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.875rem' }}>
                        ... and {routeData.route.steps.length - 3} more steps
                      </Typography>
                    )}
                  </Box>
                )}
              </Grid>
            </Grid>
          </Box>
        )}

        {routeData.alternative_routes && routeData.alternative_routes.length > 0 && (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="subtitle1">
                Alternative Routes ({routeData.alternative_routes.length})
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              {routeData.alternative_routes.map((altRoute: any, index: number) => (
                <Paper key={index} sx={{ p: 2, mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="subtitle2">
                      Alternative {index + 1}
                    </Typography>
                    <Chip
                      label={`Safety: ${altRoute.safety_score?.toFixed(2) || 'N/A'}`}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  </Box>
                  <Typography variant="body2" color="text.secondary">
                    Distance: {altRoute.distance} | Duration: {altRoute.duration}
                  </Typography>
                </Paper>
              ))}
            </AccordionDetails>
          </Accordion>
        )}

        {routeData.map_html && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle1" gutterBottom>
              Interactive Route Map
            </Typography>
            <Box
              sx={{
                border: 1,
                borderColor: 'divider',
                borderRadius: 1,
                overflow: 'hidden',
                height: 400,
              }}
              dangerouslySetInnerHTML={{ __html: routeData.map_html }}
            />
          </Box>
        )}
      </Paper>
    );
  };

  const renderSafetyInfoResults = (safetyData: any) => {
    if (!safetyData) return null;

    return (
      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <LocationIcon color="primary" />
          Safety Information for Location
        </Typography>

        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle1" gutterBottom>
              Location Details
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Latitude:</strong> {checkLat}
            </Typography>
            <Typography variant="body2" sx={{ mb: 1 }}>
              <strong>Longitude:</strong> {checkLng}
            </Typography>
            {safetyData.address && (
              <Typography variant="body2">
                <strong>Address:</strong> {safetyData.address}
              </Typography>
            )}
          </Grid>
          <Grid item xs={12} sm={6}>
            <Typography variant="subtitle1" gutterBottom>
              Safety Metrics
            </Typography>
            {safetyData.incident_count !== undefined && (
              <Typography variant="body2" sx={{ mb: 1 }}>
                <strong>Incident Count:</strong> {safetyData.incident_count}
              </Typography>
            )}
            {safetyData.safety_score !== undefined && (
              <Typography variant="body2" sx={{ mb: 1 }}>
                <strong>Safety Score:</strong> {safetyData.safety_score.toFixed(2)}
              </Typography>
            )}
            {safetyData.risk_level && (
              <Typography variant="body2">
                <strong>Risk Level:</strong> {safetyData.risk_level}
              </Typography>
            )}
          </Grid>
        </Grid>

        {safetyData.recent_incidents && safetyData.recent_incidents.length > 0 && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle1" gutterBottom>
              Recent Incidents
            </Typography>
            <Box sx={{ maxHeight: 200, overflow: 'auto' }}>
              {safetyData.recent_incidents.map((incident: any, index: number) => (
                <Paper key={index} sx={{ p: 1, mb: 1 }}>
                  <Typography variant="body2" sx={{ fontWeight: 'bold' }}>
                    {incident.type || 'Incident'}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {incident.date || incident.timestamp || 'Unknown date'}
                  </Typography>
                  {incident.description && (
                    <Typography variant="body2" sx={{ mt: 0.5 }}>
                      {incident.description}
                    </Typography>
                  )}
                </Paper>
              ))}
            </Box>
          </Box>
        )}
      </Paper>
    );
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <SafetyIcon color="primary" />
        Enhanced Safety Route Finder with Interactive Map
      </Typography>

      <Grid container spacing={3}>
        {/* Enhanced Route Finding */}
        <Grid item xs={12} md={6}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <RouteIcon color="primary" />
                Enhanced Route Finding
              </Typography>

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Start Latitude"
                    type="number"
                    value={startLat}
                    onChange={(e) => setStartLat(parseFloat(e.target.value) || 0)}
                    inputProps={{ step: 0.000001 }}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Start Longitude"
                    type="number"
                    value={startLng}
                    onChange={(e) => setStartLng(parseFloat(e.target.value) || 0)}
                    inputProps={{ step: 0.000001 }}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="End Latitude"
                    type="number"
                    value={endLat}
                    onChange={(e) => setEndLat(parseFloat(e.target.value) || 0)}
                    inputProps={{ step: 0.000001 }}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="End Longitude"
                    type="number"
                    value={endLng}
                    onChange={(e) => setEndLng(parseFloat(e.target.value) || 0)}
                    inputProps={{ step: 0.000001 }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Typography gutterBottom>
                    Safety Weight (0=Fastest, 1=Safest): {safetyWeight}
                  </Typography>
                  <Slider
                    value={safetyWeight}
                    onChange={(_, value) => setSafetyWeight(value as number)}
                    min={0}
                    max={1}
                    step={0.05}
                    marks
                    valueLabelDisplay="auto"
                  />
                </Grid>
                <Grid item xs={12}>
                  <Typography gutterBottom>
                    Max Distance Factor (1x-3x direct distance): {maxDistanceFactor}
                  </Typography>
                  <Slider
                    value={maxDistanceFactor}
                    onChange={(_, value) => setMaxDistanceFactor(value as number)}
                    min={1}
                    max={3}
                    step={0.1}
                    marks
                    valueLabelDisplay="auto"
                  />
                </Grid>
                <Grid item xs={12}>
                  <Button
                    fullWidth
                    variant="contained"
                    onClick={handleFindEnhancedRoute}
                    disabled={loadingEnhanced}
                    startIcon={loadingEnhanced ? <CircularProgress size={20} /> : <SafetyIcon />}
                    sx={{ height: 56 }}
                  >
                    {loadingEnhanced ? 'Finding Enhanced Safe Route...' : '🚀 Find Enhanced Safe Route'}
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Safety Information Checker */}
        <Grid item xs={12} md={6}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <LocationIcon color="primary" />
                Safety Information Checker
              </Typography>

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Check Latitude"
                    type="number"
                    value={checkLat}
                    onChange={(e) => setCheckLat(parseFloat(e.target.value) || 0)}
                    inputProps={{ step: 0.000001 }}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Check Longitude"
                    type="number"
                    value={checkLng}
                    onChange={(e) => setCheckLng(parseFloat(e.target.value) || 0)}
                    inputProps={{ step: 0.000001 }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Button
                    fullWidth
                    variant="outlined"
                    onClick={handleCheckSafetyInfo}
                    disabled={loadingSafetyInfo}
                    startIcon={loadingSafetyInfo ? <CircularProgress size={20} /> : <LocationIcon />}
                    sx={{ height: 56 }}
                  >
                    {loadingSafetyInfo ? 'Checking Safety Info...' : '🔍 Check Safety Info'}
                  </Button>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Results */}
      {enhancedRouteData && enhancedRouteData.success && (
        <Box sx={{ mb: 4 }}>
          {renderEnhancedRouteResults(enhancedRouteData)}
        </Box>
      )}

      {safetyInfoData && safetyInfoData.success && (
        <Box>
          {renderSafetyInfoResults(safetyInfoData)}
        </Box>
      )}
    </Box>
  );
};

export default SafetyTab; 