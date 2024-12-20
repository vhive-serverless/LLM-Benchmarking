import React from "react";
import PropTypes from "prop-types";
import merge from "lodash/merge";
import ReactApexChart from "react-apexcharts";
// @mui
import { Card, CardHeader, Box } from "@mui/material";
// Base chart options
import { BaseOptionChart } from "../../../components/chart";

const AppMetricsDate = ({ title, subheader, metrics }) => {

    const chartData = Object.keys(metrics).map((provider) => {
        return {
            name: provider,
            type: "line",
            data: metrics[provider].map((entry) => entry.aggregated_metric),
        };
    });

    const chartLabels = metrics[Object.keys(metrics)[0]]?.map((entry) => entry.date) || [];

    const chartOptions = merge(BaseOptionChart(), {
        stroke: {
            curve: "smooth",
            width: 2,
        },
        markers: {
            size: 5,
        },
        xaxis: {
            categories: chartLabels,
            title: {
                text: "Date",
            },
        },
        yaxis: {
            title: {
                text: "Latency (ms)",
            },
            labels: {
                formatter: (value) => `${value.toFixed(2)} ms`,
            },
        },
        tooltip: {
            shared: true,
            intersect: false,
            x: {
                formatter: (value) => value,
            },
            y: {
                formatter: (value) => `${value.toFixed(2)} ms`,
            },
        },
    });

    return (
        <Card
            sx={{
                transition: "0.3s",
                margin: "auto",
                boxShadow: "0 8px 40px -12px rgba(0,0,0,0.2)",
                "&:hover": {
                    boxShadow: "0 16px 70px -12.125px rgba(0,0,0,0.3)",
                },
            }}
        >
            <CardHeader title={title} subheader={subheader} />
            <Box sx={{ p: 3, pb: 1 }} dir="ltr">
                <ReactApexChart
                    type="line"
                    series={chartData}
                    options={chartOptions}
                    height={450}
                />
            </Box>
        </Card>
    );
};

AppMetricsDate.propTypes = {
    title: PropTypes.string.isRequired, // Metric name (e.g., response_times, timetofirsttoken)
    subheader: PropTypes.string, // Additional information to display
    metrics: PropTypes.object.isRequired, // Aggregated metrics data structured by provider
};

export default AppMetricsDate;
