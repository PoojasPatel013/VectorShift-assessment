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
      
      if (!user || !org) {
        throw new Error('User and organization IDs are required');
      }

      const formData = new FormData();
      formData.append('user_id', user);
      formData.append('org_id', org);

      const response = await axios.post(
        'http://localhost:8000/integrations/hubspot/authorize',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      if (!response.data?.url) {
        throw new Error('Failed to get authorization URL');
      }

      const oauthWindow = window.open(response.data.url, '_blank', 'width=800,height=600');
      
      const checkWindowClosed = setInterval(() => {
        if (oauthWindow.closed) {
          clearInterval(checkWindowClosed);
          checkConnectionStatus();
        }
      }, 200);
    } catch (error) {
      setError(error.response?.data?.detail || error.message);
      setIsLoading(false);
    } finally {
      setIsLoading(false);
    }
  };

  const checkConnectionStatus = async () => {
    try {
      if (!user || !org) {
        throw new Error('User and organization IDs are required');
      }

      const formData = new FormData();
      formData.append('user_id', user);
      formData.append('org_id', org);

      const response = await axios.post(
        'http://localhost:8000/integrations/hubspot/credentials',
        formData
      );

      if (response.data && response.data.credentials) {
        setIsConnected(true);
        setIntegrationParams(prev => ({ 
          ...prev, 
          credentials: response.data.credentials, 
          type: 'HubSpot' 
        }));
      }
    } catch (error) {
      console.error('Error checking connection:', error);
      setError(error.response?.data?.detail || error.message);
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
          Connect to HubSpot
        </Button>
      )}
    </Box>
  );
};
