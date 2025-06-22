import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Button,
  Box,
  Grid,
  Paper,
  Alert,
  CircularProgress,
  Chip,
} from '@mui/material';
import {
  Info as BCInfoIcon,
  Person as AgentIcon,
  Assignment as TaskIcon,
  Code as CodeIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { apiService, BCAgentsInfo, BCTasksInfo } from '../services/api';

const BCInfoTab: React.FC = () => {
  const [agentsData, setAgentsData] = useState<BCAgentsInfo | null>(null);
  const [tasksData, setTasksData] = useState<BCTasksInfo | null>(null);
  const [loadingAgents, setLoadingAgents] = useState(false);
  const [loadingTasks, setLoadingTasks] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleViewAgents = async () => {
    setLoadingAgents(true);
    setError(null);
    setAgentsData(null);

    try {
      const data = await apiService.getBCAgentsInfo();
      setAgentsData(data);
      if (!data.success) {
        setError(data.message || 'Failed to get agents information');
      }
    } catch (err) {
      setError('An error occurred while fetching agents information');
      console.error('Agents API error:', err);
    } finally {
      setLoadingAgents(false);
    }
  };

  const handleViewTasks = async () => {
    setLoadingTasks(true);
    setError(null);
    setTasksData(null);

    try {
      const data = await apiService.getBCTasksInfo();
      setTasksData(data);
      if (!data.success) {
        setError(data.message || 'Failed to get tasks information');
      }
    } catch (err) {
      setError('An error occurred while fetching tasks information');
      console.error('Tasks API error:', err);
    } finally {
      setLoadingTasks(false);
    }
  };

  const renderAgentCard = (agent: any, index: number) => {
    return (
      <Card key={index} sx={{ mb: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <AgentIcon color="primary" />
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
              {agent.name || `Agent ${index + 1}`}
            </Typography>
            {agent.role && (
              <Chip
                label={agent.role}
                size="small"
                color="secondary"
                variant="outlined"
              />
            )}
          </Box>

          {agent.description && (
            <Typography variant="body2" sx={{ mb: 2, lineHeight: 1.6 }}>
              {agent.description}
            </Typography>
          )}

          {agent.capabilities && agent.capabilities.length > 0 && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Capabilities:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {agent.capabilities.map((capability: string, capIndex: number) => (
                  <Chip
                    key={capIndex}
                    label={capability}
                    size="small"
                    variant="outlined"
                    icon={<CodeIcon />}
                  />
                ))}
              </Box>
            </Box>
          )}

          {agent.tools && agent.tools.length > 0 && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Tools:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {agent.tools.map((tool: string, toolIndex: number) => (
                  <Chip
                    key={toolIndex}
                    label={tool}
                    size="small"
                    variant="outlined"
                    icon={<SettingsIcon />}
                  />
                ))}
              </Box>
            </Box>
          )}
        </CardContent>
      </Card>
    );
  };

  const renderTaskCard = (task: any, index: number) => {
    return (
      <Card key={index} sx={{ mb: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <TaskIcon color="primary" />
            <Typography variant="h6" sx={{ fontWeight: 'bold' }}>
              {task.name || `Task ${index + 1}`}
            </Typography>
            {task.status && (
              <Chip
                label={task.status}
                size="small"
                color={task.status === 'completed' ? 'success' : 'warning'}
                variant="outlined"
              />
            )}
          </Box>

          {task.description && (
            <Typography variant="body2" sx={{ mb: 2, lineHeight: 1.6 }}>
              {task.description}
            </Typography>
          )}

          {task.agent && (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              <strong>Assigned Agent:</strong> {task.agent}
            </Typography>
          )}

          {task.expected_duration && (
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
              <strong>Expected Duration:</strong> {task.expected_duration}
            </Typography>
          )}

          {task.dependencies && task.dependencies.length > 0 && (
            <Box>
              <Typography variant="subtitle2" gutterBottom>
                Dependencies:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                {task.dependencies.map((dependency: string, depIndex: number) => (
                  <Chip
                    key={depIndex}
                    label={dependency}
                    size="small"
                    variant="outlined"
                  />
                ))}
              </Box>
            </Box>
          )}
        </CardContent>
      </Card>
    );
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <BCInfoIcon color="primary" />
        BC CrewAI Information
      </Typography>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <AgentIcon color="primary" />
                View Agents
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Get information about all available BC CrewAI agents
              </Typography>
              <Button
                fullWidth
                variant="contained"
                onClick={handleViewAgents}
                disabled={loadingAgents}
                startIcon={loadingAgents ? <CircularProgress size={20} /> : <AgentIcon />}
              >
                {loadingAgents ? 'Loading Agents...' : '🤖 View Agents'}
              </Button>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TaskIcon color="primary" />
                View Tasks
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Get information about all available BC CrewAI tasks
              </Typography>
              <Button
                fullWidth
                variant="contained"
                onClick={handleViewTasks}
                disabled={loadingTasks}
                startIcon={loadingTasks ? <CircularProgress size={20} /> : <TaskIcon />}
              >
                {loadingTasks ? 'Loading Tasks...' : '📋 View Tasks'}
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {agentsData && agentsData.success && (
        <Box sx={{ mb: 4 }}>
          <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              BC CrewAI Agents ({agentsData.agents.length})
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Available agents and their capabilities
            </Typography>
          </Paper>

          <Grid container spacing={2}>
            {agentsData.agents.map((agent, index) => (
              <Grid item xs={12} md={6} key={index}>
                {renderAgentCard(agent, index)}
              </Grid>
            ))}
          </Grid>
        </Box>
      )}

      {tasksData && tasksData.success && (
        <Box>
          <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              BC CrewAI Tasks ({tasksData.tasks.length})
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Available tasks and their details
            </Typography>
          </Paper>

          <Grid container spacing={2}>
            {tasksData.tasks.map((task, index) => (
              <Grid item xs={12} md={6} key={index}>
                {renderTaskCard(task, index)}
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Box>
  );
};

export default BCInfoTab; 