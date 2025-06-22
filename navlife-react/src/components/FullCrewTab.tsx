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
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Group as FullCrewIcon,
  ExpandMore as ExpandMoreIcon,
  Science as ResearchIcon,
  DirectionsBus as TransportIcon,
  Article as ArticleIcon,
} from '@mui/icons-material';
import { apiService } from '../services/api';

const FullCrewTab: React.FC = () => {
  const [userRequest, setUserRequest] = useState('Research AI LLMs trends and plan my commute from SFO to Embarcadero by 9am');
  const [topic, setTopic] = useState('AI LLMs and Transit Planning');
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [time, setTime] = useState('');
  const [fullCrewData, setFullCrewData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExecuteFullCrew = async () => {
    if (!userRequest.trim()) {
      setError('Please enter your request');
      return;
    }

    setLoading(true);
    setError(null);
    setFullCrewData(null);

    try {
      const data = await apiService.getFullCrew(userRequest, topic, origin, destination, time);
      setFullCrewData(data);
      if (!data.success) {
        setError(data.message || 'Failed to execute full crew request');
      }
    } catch (err) {
      setError('An error occurred while executing full crew request');
      console.error('Full Crew API error:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderResearchSection = (research: any) => {
    if (!research) return null;

    return (
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ResearchIcon color="primary" />
            <Typography variant="h6">Research Results</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          {research.summary && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                Summary
              </Typography>
              <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
                {research.summary}
              </Typography>
            </Box>
          )}

          {research.key_findings && research.key_findings.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                Key Findings
              </Typography>
              <Box component="ul" sx={{ pl: 2 }}>
                {research.key_findings.map((finding: string, index: number) => (
                  <Typography key={index} component="li" variant="body2" sx={{ mb: 0.5 }}>
                    {finding}
                  </Typography>
                ))}
              </Box>
            </Box>
          )}

          {research.recommendations && research.recommendations.length > 0 && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Recommendations
              </Typography>
              <Box component="ol" sx={{ pl: 2 }}>
                {research.recommendations.map((recommendation: string, index: number) => (
                  <Typography key={index} component="li" variant="body2" sx={{ mb: 0.5 }}>
                    {recommendation}
                  </Typography>
                ))}
              </Box>
            </Box>
          )}
        </AccordionDetails>
      </Accordion>
    );
  };

  const renderTransportSection = (transport: any) => {
    if (!transport) return null;

    return (
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TransportIcon color="primary" />
            <Typography variant="h6">Transport Planning</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          {transport.routes && transport.routes.length > 0 ? (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Recommended Routes ({transport.routes.length})
              </Typography>
              {transport.routes.map((route: any, index: number) => (
                <Paper key={index} sx={{ p: 2, mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                      Route {index + 1}
                    </Typography>
                    <Chip
                      label={route.summary || `Route ${index + 1}`}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  </Box>
                  {route.duration && (
                    <Typography variant="body2" color="text.secondary">
                      Duration: {route.duration}
                    </Typography>
                  )}
                  {route.distance && (
                    <Typography variant="body2" color="text.secondary">
                      Distance: {route.distance}
                    </Typography>
                  )}
                  {route.instructions && (
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      {route.instructions}
                    </Typography>
                  )}
                </Paper>
              ))}
            </Box>
          ) : (
            <Typography variant="body2" color="text.secondary">
              No transport routes found
            </Typography>
          )}
        </AccordionDetails>
      </Accordion>
    );
  };

  const renderIntegrationSection = (integration: any) => {
    if (!integration) return null;

    return (
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <ArticleIcon color="primary" />
            <Typography variant="h6">Integrated Analysis</Typography>
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          {integration.analysis && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                Combined Analysis
              </Typography>
              <Typography variant="body2" sx={{ lineHeight: 1.6 }}>
                {integration.analysis}
              </Typography>
            </Box>
          )}

          {integration.recommendations && integration.recommendations.length > 0 && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Integrated Recommendations
              </Typography>
              <Box component="ol" sx={{ pl: 2 }}>
                {integration.recommendations.map((recommendation: string, index: number) => (
                  <Typography key={index} component="li" variant="body2" sx={{ mb: 0.5 }}>
                    {recommendation}
                  </Typography>
                ))}
              </Box>
            </Box>
          )}
        </AccordionDetails>
      </Accordion>
    );
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <FullCrewIcon color="primary" />
        BC CrewAI Full Crew (Research + Transit)
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Your Request"
                placeholder="e.g., Research AI trends and plan my commute from SFO to Embarcadero"
                value={userRequest}
                onChange={(e) => setUserRequest(e.target.value)}
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Research Topic"
                placeholder="e.g., AI LLMs and Transit Planning"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={2}>
              <TextField
                fullWidth
                label="Origin"
                placeholder="e.g., SFO"
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={2}>
              <TextField
                fullWidth
                label="Destination"
                placeholder="e.g., EMB"
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={2}>
              <TextField
                fullWidth
                label="Time"
                placeholder="e.g., 09:00"
                value={time}
                onChange={(e) => setTime(e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                fullWidth
                variant="contained"
                onClick={handleExecuteFullCrew}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <FullCrewIcon />}
                sx={{ height: 56 }}
              >
                {loading ? 'Executing Full Crew...' : 'Execute Full Crew'}
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

      {fullCrewData && fullCrewData.success && (
        <Box>
          <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Full Crew Results
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Successfully executed research and transit planning
            </Typography>
          </Paper>

          <Box>
            {renderResearchSection(fullCrewData.research)}
            {renderTransportSection(fullCrewData.transport)}
            {renderIntegrationSection(fullCrewData.integration)}
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default FullCrewTab; 