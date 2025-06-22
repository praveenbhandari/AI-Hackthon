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
} from '@mui/material';
import {
  Science as ResearchIcon,
  CalendarToday as CalendarIcon,
  Article as ArticleIcon,
} from '@mui/icons-material';
import { apiService, ResearchResult } from '../services/api';

const ResearchTab: React.FC = () => {
  const [topic, setTopic] = useState('AI LLMs');
  const [currentYear, setCurrentYear] = useState(new Date().getFullYear().toString());
  const [researchData, setResearchData] = useState<ResearchResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleStartResearch = async () => {
    if (!topic.trim()) {
      setError('Please enter a research topic');
      return;
    }

    setLoading(true);
    setError(null);
    setResearchData(null);

    try {
      const data = await apiService.getResearch(topic, currentYear);
      setResearchData(data);
      if (!data.success) {
        setError(data.message || 'Failed to start research');
      }
    } catch (err) {
      setError('An error occurred while conducting research');
      console.error('Research API error:', err);
    } finally {
      setLoading(false);
    }
  };

  const renderResearchResults = (research: any) => {
    if (!research) return null;

    return (
      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ArticleIcon color="primary" />
          Research Results
        </Typography>

        {research.summary && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Summary
            </Typography>
            <Typography variant="body1" sx={{ lineHeight: 1.6 }}>
              {research.summary}
            </Typography>
          </Box>
        )}

        {research.key_findings && research.key_findings.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Key Findings
            </Typography>
            <Box component="ul" sx={{ pl: 2 }}>
              {research.key_findings.map((finding: string, index: number) => (
                <Typography key={index} component="li" variant="body1" sx={{ mb: 1 }}>
                  {finding}
                </Typography>
              ))}
            </Box>
          </Box>
        )}

        {research.trends && research.trends.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Current Trends
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {research.trends.map((trend: string, index: number) => (
                <Chip
                  key={index}
                  label={trend}
                  color="primary"
                  variant="outlined"
                  size="small"
                />
              ))}
            </Box>
          </Box>
        )}

        {research.recommendations && research.recommendations.length > 0 && (
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recommendations
            </Typography>
            <Box component="ol" sx={{ pl: 2 }}>
              {research.recommendations.map((recommendation: string, index: number) => (
                <Typography key={index} component="li" variant="body1" sx={{ mb: 1 }}>
                  {recommendation}
                </Typography>
              ))}
            </Box>
          </Box>
        )}

        {research.sources && research.sources.length > 0 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Sources
            </Typography>
            <Box component="ul" sx={{ pl: 2 }}>
              {research.sources.map((source: string, index: number) => (
                <Typography key={index} component="li" variant="body2" sx={{ mb: 0.5 }}>
                  {source}
                </Typography>
              ))}
            </Box>
          </Box>
        )}

        {research.raw_data && (
          <Box sx={{ mt: 3, pt: 3, borderTop: 1, borderColor: 'divider' }}>
            <Typography variant="h6" gutterBottom>
              Raw Research Data
            </Typography>
            <Paper variant="outlined" sx={{ p: 2, backgroundColor: 'grey.50' }}>
              <Typography variant="body2" component="pre" sx={{ 
                whiteSpace: 'pre-wrap', 
                fontFamily: 'monospace',
                fontSize: '0.875rem'
              }}>
                {JSON.stringify(research.raw_data, null, 2)}
              </Typography>
            </Paper>
          </Box>
        )}
      </Paper>
    );
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <ResearchIcon color="primary" />
        BC CrewAI Research
      </Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Research Topic"
                placeholder="e.g., AI LLMs, Machine Learning, etc."
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleStartResearch()}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Current Year"
                placeholder="e.g., 2024"
                value={currentYear}
                onChange={(e) => setCurrentYear(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleStartResearch()}
                InputProps={{
                  startAdornment: <CalendarIcon sx={{ mr: 1, color: 'text.secondary' }} />,
                }}
              />
            </Grid>
            <Grid item xs={12}>
              <Button
                fullWidth
                variant="contained"
                onClick={handleStartResearch}
                disabled={loading}
                startIcon={loading ? <CircularProgress size={20} /> : <ResearchIcon />}
                sx={{ height: 56 }}
              >
                {loading ? 'Conducting Research...' : 'Start Research'}
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

      {researchData && researchData.success && researchData.research && (
        <Box>
          {renderResearchResults(researchData.research)}
        </Box>
      )}
    </Box>
  );
};

export default ResearchTab; 