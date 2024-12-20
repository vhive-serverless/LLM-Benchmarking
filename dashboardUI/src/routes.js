import { Navigate, useRoutes } from 'react-router-dom';
// layouts
import DashboardLayout from './layouts/dashboard';
import LogoOnlyLayout from './layouts/LogoOnlyLayout';
//
import Team from './pages/Team';
import NotFound from './pages/Page404';
import TimeBetweenToken from './pages/TimeBetweenToken';
import TimeToFirstToken from './pages/TimeToFirstToken';
import About from './pages/About';
import SingleRequest from './pages/SingleRequest';
import ResponseTimes from './pages/ResponseTimes';
import TimeBetweenTokenMedian from './pages/TimeBetweenTokenMedian';
import TimeBetweenTokenP95 from './pages/TimeBetweenTokenMedianP95';

// ----------------------------------------------------------------------

export default function Router() {
  return useRoutes([
    {
      path: '/dashboard',
      element: <DashboardLayout />,
      children: [
        {
          path: 'about/',
          element: <About />
        },
        {
          path: 'metric',
          children: [
            { path: 'time-to-first-token', element: <TimeToFirstToken /> },
            { path: 'time-between-token', element: <TimeBetweenToken /> },
            { path: 'time-between-token-median', element: <TimeBetweenTokenMedian /> },
            { path: 'time-between-token-p95', element: <TimeBetweenTokenP95 /> },
            { path: 'response-times', element: <ResponseTimes /> },
            { path: 'single-request', element: <SingleRequest /> },
            // { path: 'deployment-language', element: <ComingSoon /> }
          ]
        },
        { path: 'team', element: <Team /> },
      ],

    },
    {
      path: '/',
      element: <LogoOnlyLayout />,
      children: [
        { path: '/', element: <Navigate to="/dashboard/about" /> },
        { path: '/dashboard', element: <Navigate to="/dashboard/about" /> },
        { path: '404', element: <NotFound /> },
        { path: '*', element: <Navigate to="/404" /> },
      ],
    },
    { path: '*', element: <Navigate to="/404" replace /> },
  ]);
}
