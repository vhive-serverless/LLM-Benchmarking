import React, { useEffect, useState, useCallback } from "react";
import PropTypes from "prop-types";
import axios from "axios";
import { Grid, Container, Typography, CircularProgress, Alert, Stack } from "@mui/material";
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import Page from "../../../components/Page";
import AppMetrics from "./AppMetrics";
import AppMetricsDate from "./AppMetricsDate";

// ----------------------------------------------------------------------

const AppMetricsPage = ({ metricType, streaming = true }) => {
    const [metrics, setMetrics] = useState(null);
    const [periodMetrics, setPeriodMetrics] = useState(null);
    const [dateList, setDateList] = useState(null)
    const [loadingMetrics, setLoadingMetrics] = useState(true);
    const [loadingPeriodMetrics, setLoadingPeriodMetrics] = useState(true);
    const [error, setError] = useState(false);
    const [dateRange, setDateRange] = useState("three-month");
    const [selectedDate, setSelectedDate] = useState('latest');

    const baseURL = "http://localhost:8000";

    const fetchMetrics = useCallback(async () => {
        setLoadingMetrics(true);
        let metricsResponse
        try {
            metricsResponse = await axios.get(`${baseURL}/metrics/date`, {
                params: { date: selectedDate, metricType, streaming },
            });
            setMetrics(metricsResponse.data.metrics);
        } catch (error) {
            console.error("Error fetching metrics:", error);
            setError(true);
        } finally {
            setLoadingMetrics(false);
        }
    }, [baseURL, selectedDate, metricType, streaming]);

    const fetchPeriodMetrics = useCallback(async () => {
        setLoadingPeriodMetrics(true);
        try {
            const response = await axios.get(`${baseURL}/metrics/period`, {
                params: { timeRange: dateRange, metricType, streaming },
            });
            setPeriodMetrics(response.data.aggregated_metrics);
            setDateList(response.data.date_array)
        } catch (error) {
            console.error("Error fetching period metrics:", error);
            setError(true);
        } finally {
            setLoadingPeriodMetrics(false);
        }
    }, [baseURL, dateRange, metricType, streaming]);

    useEffect(() => {
        fetchMetrics();
        fetchPeriodMetrics();
    }, [fetchMetrics, fetchPeriodMetrics]);

    const handleDateRangeChange = (event) => {
        setDateRange(event.target.value);
    };

    const handleDateChange = (event) => {
        setSelectedDate(event.target.value)
    };

    // Combine loading states
    const loading = loadingMetrics || loadingPeriodMetrics;

    if (loading) return <CircularProgress />;
    if (error)
        return (
            <Alert variant="outlined" severity="error">
                Something went wrong while fetching metrics!
            </Alert>
        );

    if (!metrics || !periodMetrics) return <Typography>No data available</Typography>;
    return (
        <Page title="Metrics Dashboard">
            <Container maxWidth="xl">
                <Typography variant="h4" sx={{ mb: 2 }}>
                    Metrics Dashboard
                </Typography>

                <Grid container spacing={3}>

                    <Stack direction="row" alignItems="center" sx={{ mb: 2, pt: 3, pl: 3 }}>
                        <InputLabel sx={{ mr: 3 }}>Time span:</InputLabel>
                        <Select
                            value={dateRange}
                            onChange={handleDateRangeChange}
                            label="Date Range"
                        >
                            <MenuItem value="week">Last week</MenuItem>
                            <MenuItem value="month">Last month</MenuItem>
                            <MenuItem value="three-month">Last 3 months</MenuItem>
                        </Select>
                    </Stack>

                    <Grid item xs={12}>
                        <AppMetricsDate
                            title={`Aggregated Metrics for ${metricType.replace("_", " ")}`}
                            subheader={`Aggregated Latency Metrics (${dateRange})`}
                            metrics={periodMetrics}
                        />
                    </Grid>
                    <Stack direction="row" alignItems="center" sx={{ mb: 2, pt: 5, pl: 3 }}>
                        <InputLabel sx={{ mr: 3 }}>Date:</InputLabel>
                        <Select
                            value={selectedDate}
                            onChange={handleDateChange}
                            label="Select Date"
                            MenuProps={{
                                PaperProps: {
                                    style: {
                                        maxHeight: 200, // Set max height of dropdown menu (in px)
                                        overflowY: "auto", // Enable vertical scrolling
                                    },
                                },
                            }}
                        >
                            <MenuItem value="latest">Latest</MenuItem>
                            {dateList.map((date, index) => (
                                <MenuItem key={index} value={date}>
                                    {`${date}`}
                                </MenuItem>
                            ))}
                        </Select>
                    </Stack>

                    <Grid item xs={12}>
                        <AppMetrics
                            title={metricType}
                            subheader={`Latency vs CDF across all providers`}
                            metrics={metrics}
                        />
                    </Grid>
                </Grid>
            </Container>
        </Page>
    );
};
AppMetricsPage.propTypes = {
    metricType: PropTypes.string.isRequired,
    streaming: PropTypes.bool,
};
export default AppMetricsPage;
