import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  Grid,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Paper,
  Chip,
  Divider
} from '@mui/material';
import {
  DirectionsBus,
  DirectionsWalk,
  DirectionsSubway,
  DirectionsCar,
  DirectionsBike,
  ExpandMore
} from '@mui/icons-material';
import apiService from '../services/api';

const TransportTab: React.FC = () => {
  const [userRequest, setUserRequest] = useState('');
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [time, setTime] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [transportData, setTransportData] = useState<any>(null);

  const handleFindRoutes = async () => {
    if (!userRequest.trim()) {
      setError('Please enter a transit request');
      return;
    }

    setLoading(true);
    setError(null);
    setTransportData(null);

    try {
      const result = await apiService.getTransportRoutes(userRequest, origin, destination, time);
      
      if (result.success) {
        setTransportData(result);
      } else {
        setError(result.message || 'Failed to find routes');
      }
    } catch (err) {
      console.error('Error finding routes:', err);
      setError('Failed to connect to transit service');
    } finally {
      setLoading(false);
    }
  };

  const getTransportIcon = (mode: string) => {
    switch (mode?.toLowerCase()) {
      case 'bus':
        return <DirectionsBus color="primary" />;
      case 'subway':
      case 'train':
        return <DirectionsSubway color="primary" />;
      case 'walking':
      case 'walk':
        return <DirectionsWalk color="primary" />;
      case 'driving':
      case 'car':
        return <DirectionsCar color="primary" />;
      case 'bicycling':
      case 'bike':
        return <DirectionsBike color="primary" />;
      default:
        return <DirectionsBus color="primary" />;
    }
  };

  const renderRouteDetails = (route: any, index: number) => {
    try {
      return (
        <Accordion key={index} sx={{ mb: 2 }}>
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
              {getTransportIcon(route.route_type || route.mode)}
              <Box sx={{ flexGrow: 1 }}>
                <Typography variant="subtitle1">
                  {route.route_id || `Route ${index + 1}`}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {route.route_type || 'Transit'} • {route.time_taken || route.duration || 'Unknown duration'}
                </Typography>
              </Box>
              {route.cost && (
                <Typography variant="body2" color="primary">
                  ${route.cost}
                </Typography>
              )}
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Box>
              {/* Route Summary */}
              <Box sx={{ mb: 2 }}>
                <Typography variant="h6" gutterBottom>
                  Route Summary
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="body2" color="text.secondary">
                      Departure
                    </Typography>
                    <Typography variant="body1">
                      {route.departure_time || 'N/A'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="body2" color="text.secondary">
                      Arrival
                    </Typography>
                    <Typography variant="body1">
                      {route.arrival_time || 'N/A'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="body2" color="text.secondary">
                      Duration
                    </Typography>
                    <Typography variant="body1">
                      {route.time_taken || route.duration || 'N/A'}
                    </Typography>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Typography variant="body2" color="text.secondary">
                      Cost
                    </Typography>
                    <Typography variant="body1">
                      {route.cost ? `$${route.cost}` : 'N/A'}
                    </Typography>
                  </Grid>
                </Grid>
              </Box>

              <Divider sx={{ my: 2 }} />

              {/* Stops */}
              {route.stops && Array.isArray(route.stops) && route.stops.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Stops ({route.total_stops || route.stops.length})
                  </Typography>
                  {route.stops.map((stop: any, stopIndex: number) => (
                    <Box key={stopIndex} sx={{ mb: 1, pl: 2 }}>
                      <Typography variant="body2">
                        {stop.stop_name || stop.name || `Stop ${stopIndex + 1}`}
                      </Typography>
                      {stop.arrival_time && (
                        <Typography variant="caption" color="text.secondary">
                          Arrival: {stop.arrival_time}
                        </Typography>
                      )}
                    </Box>
                  ))}
                </Box>
              )}

              {/* Route Steps */}
              {route.steps && Array.isArray(route.steps) && route.steps.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Route Steps:
                  </Typography>
                  {route.steps.map((step: any, stepIndex: number) => (
                    <Box key={stepIndex} sx={{ mb: 1, pl: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {getTransportIcon(step.mode || 'transit')}
                        <Typography variant="body2">
                          {step.instruction || step.description || `Step ${stepIndex + 1}`}
                        </Typography>
                      </Box>
                      {step.duration && (
                        <Typography variant="caption" color="text.secondary" sx={{ ml: 4 }}>
                          Duration: {step.duration}
                        </Typography>
                      )}
                    </Box>
                  ))}
                </Box>
              )}

              {/* Route Legs */}
              {route.legs && Array.isArray(route.legs) && route.legs.length > 0 && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    Route Legs:
                  </Typography>
                  {route.legs.map((leg: any, legIndex: number) => (
                    <Paper key={legIndex} sx={{ p: 2, mb: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        {getTransportIcon(leg.mode || 'transit')}
                        <Typography variant="subtitle2">
                          {leg.mode || 'Transit'}
                        </Typography>
                      </Box>
                      <Typography variant="body2" gutterBottom>
                        {leg.instruction || leg.description || `Leg ${legIndex + 1}`}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 2 }}>
                        {leg.duration && (
                          <Typography variant="caption" color="text.secondary">
                            Duration: {leg.duration}
                          </Typography>
                        )}
                        {leg.distance && (
                          <Typography variant="caption" color="text.secondary">
                            Distance: {leg.distance}
                          </Typography>
                        )}
                      </Box>
                    </Paper>
                  ))}
                </Box>
              )}

              {/* Transit Agencies */}
              {route.agencies && Array.isArray(route.agencies) && route.agencies.length > 0 && (
                <Box>
                  <Typography variant="h6" gutterBottom>
                    Transit Agencies:
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {route.agencies.map((agency: any, agencyIndex: number) => (
                      <Chip
                        key={agencyIndex}
                        label={agency.name || agency}
                        size="small"
                        variant="outlined"
                      />
                    ))}
                  </Box>
                </Box>
              )}
            </Box>
          </AccordionDetails>
        </Accordion>
      );
    } catch (err) {
      console.error('Error rendering route:', err);
      return (
        <Alert severity="error" sx={{ mb: 2 }}>
          Error displaying route {index + 1}
        </Alert>
      );
    }
  };

  // Get the correct routes array from the response
  const getRoutesArray = () => {
    if (!transportData) return [];
    
    // Check for different possible structures
    if (transportData.routes && Array.isArray(transportData.routes)) {
      return transportData.routes;
    }
    
    if (transportData.data && transportData.data.transit_routes && Array.isArray(transportData.data.transit_routes)) {
      return transportData.data.transit_routes;
    }
    
    if (transportData.data && transportData.data.optimized_routes && Array.isArray(transportData.data.optimized_routes)) {
      return transportData.data.optimized_routes;
    }
    
    return [];
  };

  const routesArray = getRoutesArray();

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <DirectionsBus color="primary" />
        BC CrewAI Transit Route Planner
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Describe your transit need"
                placeholder="e.g., Get me from SFO to Embarcadero by 9am"
                value={userRequest}
                onChange={(e) => setUserRequest(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleFindRoutes()}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Origin"
                placeholder="e.g., SFO"
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleFindRoutes()}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Destination"
                placeholder="e.g., EMB"
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleFindRoutes()}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="Time"
                placeholder="e.g., 09:00"
                value={time}
                onChange={(e) => setTime(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleFindRoutes()}
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                fullWidth
                variant="contained"
                onClick={handleFindRoutes}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <DirectionsBus />}
                sx={{ height: 56 }}
              >
                {loading ? 'Finding Routes...' : 'Find Transit Routes'}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {transportData && transportData.success && (
        <Box>
          <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              BC CrewAI Transit Results
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Found {routesArray.length} route(s)
            </Typography>
          </Paper>

          <Box>
            {routesArray.length > 0 ? (
              routesArray.map((route: any, index: number) => renderRouteDetails(route, index))
            ) : (
              <Alert severity="info">
                No routes found. Please try different parameters.
              </Alert>
            )}
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default TransportTab; 