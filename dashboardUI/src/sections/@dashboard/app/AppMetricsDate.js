import React from "react";
import PropTypes from "prop-types";
import merge from "lodash/merge";
import ReactApexChart from "react-apexcharts";
// @mui
import { Card, CardHeader, Box } from "@mui/material";
// Base chart options
import { BaseOptionChart } from "../../../components/chart";

const AppMetricsDate = ({ title, subheader, metrics, dateArray }) => {

    // Prepare chart data with normalized dates
    const chartData = Object.keys(metrics).map((provider) => ({
        name: provider,
        type: "line",
        data: dateArray.map((date) => {
            const entry = metrics[provider].find((metric) => metric.date === date);
            return entry ? entry.aggregated_metric : null;
        }),
    }));

    const chartOptions = merge(BaseOptionChart(), {
        stroke: {
            curve: "smooth",
            width: 2,
        },
        markers: {
            size: 5,
        },
        xaxis: {
            categories: dateArray,
            title: {
                text: "Date",
            },
            labels: {
                formatter: (value) => value,
            },
        },
        yaxis: {
            title: {
                text: "Latency (ms)",
            },
            labels: {
                formatter: (value) => (value !== null ? `${value.toFixed(2)} ms` : "N/A"),
            },
        },
        tooltip: {
            shared: true,
            intersect: false,
            x: {
                formatter: (value) => value,
            },
            y: {
                formatter: (value) => (value !== null ? `${value.toFixed(2)} ms` : "N/A"),
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
    title: PropTypes.string.isRequired,
    subheader: PropTypes.string,
    metrics: PropTypes.object.isRequired,
    dateArray: PropTypes.arrayOf(PropTypes.string).isRequired,
};

export default AppMetricsDate;
