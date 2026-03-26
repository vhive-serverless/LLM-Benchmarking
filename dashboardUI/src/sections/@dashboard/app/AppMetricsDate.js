import React from "react";
import PropTypes from "prop-types";
import merge from "lodash/merge";
import ReactApexChart from "react-apexcharts";
// @mui
import { Card, CardHeader, Box } from "@mui/material";
// Base chart options
import { BaseOptionChart } from "../../../components/chart";

export const providerColors = {
    "PerplexityAI": "#FF5733",   // Red-Orange
    "AWSBedrock": "#33FF57",     // Green
    "Hyperbolic": "#3357FF",     // Blue
    "Open_AI": "#FF33A8",        // Pink
    "Azure": "#FFA500",          // Orange
    "TogetherAI": "#800080",     // Purple
    "Cloudflare": "#FFD700",     // Gold
    "Anthropic": "#008080",      // Teal
    "GoogleGemini": "#00BFFF",   // Deep Sky Blue
    "GroqProvider": "#A52A2A",   // Brown
    "VLLM": "#4B0082"            // Indigo
};

const getProviderColor = (fullName) => {
  const lower = fullName.toLowerCase();

  const match = Object.entries(providerColors).find(([baseName]) =>
    lower.includes(baseName.toLowerCase())
  );

  return match ? match[1] : "#999999";
};

const AppMetricsDate = ({ title, subheader, metrics, dateArray, yaxis, logScale = true }) => {
    // Prepare chart data with normalized dates; log-transform values when logScale is enabled
    const transformedMetrics = {};

    const transformValue = (val) => {
        if (val == null) return null;
        if (!logScale) return val;
        return val > 0 ? Math.log10(val) : null;
    };

    Object.keys(metrics).forEach((provider) => {
        transformedMetrics[provider] = metrics[provider].map((metric) => ({
            ...metric,
            aggregated_metric: transformValue(metric.aggregated_metric),
        }));
    });
    const sortedProviders = Object.keys(transformedMetrics).sort();

    const chartData = sortedProviders.map((provider) => ({
        name: provider,
        type: "line",
        data: dateArray.map((date) => {
            const entry = transformedMetrics[provider].find((metric) => metric.date === date);
            return entry ? entry.aggregated_metric : null;
        }),
    }));

    const chartOptions = merge(BaseOptionChart(), {
        stroke: {
            curve: "straight",
            width: 2,
        },
        markers: {
            size: 5,
        },
        colors: sortedProviders.map((provider) => getProviderColor(provider)),
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
                text: (() => {
                    const base = yaxis === "Accuracy" ? "Accuracy" : "Latency ms";
                    return logScale ? `${base} (Log Scale)` : base;
                })(),
            },
            labels: {
                formatter: (value) => {
                    if (value == null || Number.isNaN(value)) return "N/A";
                    return logScale ? `${(10 ** value).toFixed(3)}` : `${value.toFixed(3)}`;
                },
            },
            type: "linear",
            max: (max) => {
                    if (yaxis !== "Accuracy") return max + 0.1;
                    return logScale ? 0 : 1;
                },
        },
        tooltip: {
            shared: true,
            intersect: false,
            x: {
                formatter: (value) => value,
            },
            y: {
                formatter: (value) => {
                    if (value == null || Number.isNaN(value)) return "N/A";
                    return logScale ? `${(10 ** value).toFixed(3)}` : `${value.toFixed(3)}`;
                },
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
    yaxis: PropTypes.string.isRequired,
    logScale: PropTypes.bool,
};

export default AppMetricsDate;
