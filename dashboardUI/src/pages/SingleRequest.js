import AppMetricsPage from "../sections/@dashboard/app/AppMetricsPage";

export default function SingleRequest() {
  return <AppMetricsPage metricType="response_times" streaming={false} title="Single Request Metrics" metricName="Response Times" />;
}
