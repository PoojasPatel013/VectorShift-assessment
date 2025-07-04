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
    Avatar,
    Chip,
    styled,
    alpha,
    useTheme,
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

// Custom styles
const IntegrationCard = styled(Card)(({ theme }) => ({
    transition: 'transform 0.2s',
    '&:hover': {
        transform: 'translateY(-4px)',
        boxShadow: theme.shadows[8],
    },
}));

const IntegrationIcon = styled(Avatar)(({ theme }) => ({
    width: 48,
    height: 48,
    fontSize: '1.5rem',
    backgroundColor: theme.palette.primary.main,
    color: theme.palette.primary.contrastText,
}));

const IntegrationOption = styled('div')(({ theme }) => ({
    padding: theme.spacing(2),
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(2),
}));

export const IntegrationForm = () => {
    const [integrationParams, setIntegrationParams] = useState({});
    const [user, setUser] = useState('TestUser');
    const [org, setOrg] = useState('TestOrg');
    const [currType, setCurrType] = useState(null);
    const CurrIntegration = integrationMapping[currType];
    const theme = useTheme();

    const integrationOptions = Object.keys(integrationMapping).map(key => ({
        value: key,
        label: key.charAt(0).toUpperCase() + key.slice(1)
    }));

    const getIntegrationIcon = (type) => {
        const icons = {
            'airtable': '📊',
            'notion': '📝',
            'hubspot': '👥'
        };
        return icons[type] || '⚙️';
    };

    return (
        <Box sx={{ 
            width: '100%', 
            maxWidth: 1200,
            mx: 'auto',
            p: 4,
            bgcolor: theme.palette.background.default
        }}>
            <Paper elevation={4} sx={{ p: 4, mb: 4, borderRadius: 2 }}>
                <Typography variant="h3" component="h1" gutterBottom sx={{ color: theme.palette.primary.main }}>
                    Integration Hub
                </Typography>
                <Typography variant="body1" color="text.secondary" paragraph sx={{ mb: 4 }}>
                    Connect and integrate your favorite tools to streamline your workflow
                </Typography>

                <Grid container spacing={4}>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            fullWidth
                            label="User ID"
                            value={user}
                            onChange={(e) => setUser(e.target.value)}
                            variant="outlined"
                            size="medium"
                            sx={{ 
                                mt: 2,
                                '& .MuiOutlinedInput-root': {
                                    '& fieldset': {
                                        borderColor: alpha(theme.palette.primary.main, 0.3),
                                    },
                                    '&:hover fieldset': {
                                        borderColor: theme.palette.primary.main,
                                    },
                                    '&.Mui-focused fieldset': {
                                        borderColor: theme.palette.primary.main,
                                    },
                                },
                            }}
                        />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                        <TextField
                            fullWidth
                            label="Organization ID"
                            value={org}
                            onChange={(e) => setOrg(e.target.value)}
                            variant="outlined"
                            size="medium"
                            sx={{ 
                                mt: 2,
                                '& .MuiOutlinedInput-root': {
                                    '& fieldset': {
                                        borderColor: alpha(theme.palette.primary.main, 0.3),
                                    },
                                    '&:hover fieldset': {
                                        borderColor: theme.palette.primary.main,
                                    },
                                    '&.Mui-focused fieldset': {
                                        borderColor: theme.palette.primary.main,
                                    },
                                },
                            }}
                        />
                    </Grid>
                    <Grid item xs={12}>
                        <Autocomplete
                            id="integration-type"
                            options={integrationOptions}
                            value={currType ? { value: currType, label: currType.charAt(0).toUpperCase() + currType.slice(1) } : null}
                            sx={{ 
                                width: '100%', 
                                mt: 2,
                                '& .MuiOutlinedInput-root': {
                                    '& fieldset': {
                                        borderColor: alpha(theme.palette.primary.main, 0.3),
                                    },
                                    '&:hover fieldset': {
                                        borderColor: theme.palette.primary.main,
                                    },
                                    '&.Mui-focused fieldset': {
                                        borderColor: theme.palette.primary.main,
                                    },
                                },
                            }}
                            renderInput={(params) => (
                                <TextField 
                                    {...params} 
                                    label="Choose Integration" 
                                    variant="outlined" 
                                    size="medium"
                                />
                            )}
                            onChange={(e, value) => setCurrType(value?.value)}
                            renderOption={(props, option) => (
                                <IntegrationOption {...props}>
                                    <IntegrationIcon>{getIntegrationIcon(option.value)}</IntegrationIcon>
                                    <Box>
                                        <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                                            {option.label}
                                        </Typography>
                                        <Typography variant="body2" color="text.secondary">
                                            Connect your {option.label} account
                                        </Typography>
                                    </Box>
                                </IntegrationOption>
                            )}
                        />
                    </Grid>
                </Grid>
            </Paper>

            {currType && (
                <IntegrationCard sx={{ mb: 4 }}>
                    <CardHeader
                        avatar={
                            <IntegrationIcon>{getIntegrationIcon(currType)}</IntegrationIcon>
                        }
                        title={
                            <Typography variant="h5" sx={{ color: theme.palette.primary.main }}>
                                {currType.charAt(0).toUpperCase() + currType.slice(1)} Integration
                            </Typography>
                        }
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
                </IntegrationCard>
            )}

            {integrationParams?.credentials && (
                <IntegrationCard>
                    <CardHeader
                        avatar={
                            <IntegrationIcon>📊</IntegrationIcon>
                        }
                        title={
                            <Typography variant="h5" sx={{ color: theme.palette.primary.main }}>
                                Data Configuration
                            </Typography>
                        }
                        titleTypographyProps={{ variant: 'h6' }}
                    />
                    <Divider />
                    <CardContent>
                        <DataForm 
                            integrationType={integrationParams?.type} 
                            credentials={integrationParams?.credentials} 
                        />
                    </CardContent>
                </IntegrationCard>
            )}
        </Box>
    );
}
