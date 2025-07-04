import React, { useState, useEffect } from 'react';
import { Button, Box, CircularProgress, Typography } from '@mui/material';
import axios from 'axios';

export const HubSpotIntegration = ({ user, org, integrationParams, setIntegrationParams }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isConnected, setIsConnected] = useState(false);

  const handleConnect = async () => {
    try {
      setIsLoading(true);
      setError('');
      
      const response = await axios.post('/integrations/hubspot/authorize', {
        user_id: user,
        org_id: org
      });

      if (!response.data.url) {
        throw new Error('Failed to get authorization URL');
      }

      // Open OAuth window
      const oauthWindow = window.open(response.data.url, '_blank', 'width=800,height=600');
      
      // Poll to check if window is closed
      const checkWindowClosed = setInterval(() => {
        if (oauthWindow.closed) {
          clearInterval(checkWindowClosed);
          checkConnectionStatus();
        }
      }, 200);
    } catch (error) {
      setError(error.message);
      setIsLoading(false);
    } finally {
      setIsLoading(false);
    }
  };

  const checkConnectionStatus = async () => {
    try {
      const response = await axios.get('/integrations/hubspot/credentials');
      if (response.data.credentials) {
        setIsConnected(true);
        setIntegrationParams(prev => ({ ...prev, credentials: response.data.credentials, type: 'HubSpot' }));
      }
    } catch (error) {
      console.error('Error checking connection:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (integrationParams?.credentials) {
      setIsConnected(true);
    }
  }, [integrationParams?.credentials]);

  return (
    <Box>
      {isLoading ? (
        <CircularProgress />
      ) : (
        <Button
          variant="contained"
          onClick={handleConnect}
          disabled={isConnected}
        >
          {isConnected ? 'Connected' : 'Connect to HubSpot'}
        </Button>
      )}
      {error && <Typography color="error">{error}</Typography>}
    </Box>
  );
};

  return (
    <Box>
      {isLoading && <CircularProgress />}
      {error && <Typography color="error">{error}</Typography>}
      
      {isConnected ? (
        <Button
          variant="contained"
          color="success"
          onClick={handleConnect}
          disabled={isLoading}
        >
          Reconnect to HubSpot
        </Button>
      ) : (
        <Button
          variant="contained"
          color="primary"
          onClick={handleConnect}
          disabled={isLoading}
        >
          {isLoading ? <CircularProgress size={20} /> : 'Connect to HubSpot'}
        </Button>
      )}
    </Box>
  )

