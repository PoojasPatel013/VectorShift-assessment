import React, { useState } from 'react';
import {
    Box,
    Autocomplete,
    TextField,
    Paper,
    Typography,
    Grid,
    Card,
    CardContent,
    CardHeader,
    Divider,
    Button,
    CircularProgress,
    Alert,
    Stack,
} from '@mui/material';
import { AirtableIntegration } from './integrations/airtable';
import { NotionIntegration } from './integrations/notion';
import { HubSpotIntegration } from './integrations/hubspot';
import { DataForm } from './data-form';

const integrationMapping = {
    'airtable': AirtableIntegration,
    'notion': NotionIntegration,
    'hubspot': HubSpotIntegration
};

export const IntegrationForm = () => {
    const [integrationParams, setIntegrationParams] = useState({});
    const [user, setUser] = useState('TestUser');
    const [org, setOrg] = useState('TestOrg');
    const [currType, setCurrType] = useState(null);
    const CurrIntegration = integrationMapping[currType];

    const integrationOptions = Object.keys(integrationMapping).map(key => ({
        value: key,
        label: key.charAt(0).toUpperCase() + key.slice(1)
    }));

    return (
        <Box sx={{ 
            width: '100%', 
            maxWidth: 800,
            mx: 'auto',
            p: 3,
            bgcolor: '#f5f5f5'
        }}>
            <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    Integration Setup
                </Typography>
                <Typography variant="body1" color="text.secondary" paragraph>
                    Connect your favorite tools to streamline your workflow
                </Typography>

                <Grid container spacing={3}>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            fullWidth
                            label="User ID"
                            value={user}
                            onChange={(e) => setUser(e.target.value)}
                            variant="outlined"
                            size="small"
                            sx={{ mt: 2 }}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            fullWidth
                            label="Organization ID"
                            value={org}
                            onChange={(e) => setOrg(e.target.value)}
                            variant="outlined"
                            size="small"
                            sx={{ mt: 2 }}
                        />
                    </Grid>
                    <Grid item xs={12}>
                        <Autocomplete
                            id="integration-type"
                            options={integrationOptions}
                            value={currType ? { value: currType, label: currType.charAt(0).toUpperCase() + currType.slice(1) } : null}
                            sx={{ width: '100%', mt: 2 }}
                            renderInput={(params) => (
                                <TextField 
                                    {...params} 
                                    label="Choose Integration" 
                                    variant="outlined" 
                                    size="small"
                                />
                            )}
                            onChange={(e, value) => setCurrType(value?.value)}
                            renderOption={(props, option) => (
                                <Box component="li" {...props} sx={{ '& > img': { mr: 2, flexShrink: 0 } }}>
                                    <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                                        {option.label}
                                    </Typography>
                                    <Typography variant="body2" color="text.secondary">
                                        Connect your {option.label} account
                                    </Typography>
                                </Box>
                            )}
                        />
                    </Grid>
                </Grid>
            </Paper>

            {currType && (
                <Card sx={{ mb: 4 }}>
                    <CardHeader
                        title={currType.charAt(0).toUpperCase() + currType.slice(1) + ' Integration'}
                        titleTypographyProps={{ variant: 'h6' }}
                    />
                    <Divider />
                    <CardContent>
                        <CurrIntegration 
                            user={user} 
                            org={org} 
                            integrationParams={integrationParams} 
                            setIntegrationParams={setIntegrationParams} 
                        />
                    </CardContent>
                </Card>
            )}

            {integrationParams?.credentials && (
                <Card>
                    <CardHeader
                        title="Data Configuration"
                        titleTypographyProps={{ variant: 'h6' }}
                    />
                    <Divider />
                    <CardContent>
                        <DataForm 
                            integrationType={integrationParams?.type} 
                            credentials={integrationParams?.credentials} 
                        />
                    </CardContent>
                </Card>
            )}
        </Box>
    );
}
