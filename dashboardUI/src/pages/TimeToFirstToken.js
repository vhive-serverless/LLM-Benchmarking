import AppMetricsPage from "../sections/@dashboard/app/AppMetricsPage";

export default function TimeToFirstToken() {
  return <AppMetricsPage metricType="timetofirsttoken" title="Time To First Token Metrics" metricName="Time To First Token" min={50} />;
}
