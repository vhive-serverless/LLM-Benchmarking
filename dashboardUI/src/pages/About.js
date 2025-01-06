// material
import { Grid, Card, Container, Stack, Box, Button, Typography, CardContent, Link } from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';
import ListItem from '@mui/material/ListItem';
import { ReactComponent as ArchitectureDiagram } from '../images/diagram.svg';
// components
import Page from '../components/Page';

export default function About() {
  return (
    <Page title="Dashboard: About">
      <Container maxWidth="xl">
        <Stack direction="row" alignItems="center" justifyContent="space-between" mt={3}>
          {/* <Typography variant="h4" gutterBottom>
          About
          </Typography> */}
        </Stack>

        <Grid item xs={12} mb={3}>
          <Card>
            <CardContent>
              <Typography variant='h4' marginBottom={3}>What is LLMetrics ?</Typography>
              <Typography variant='p'>LLMetrics is a benchmarking tool designed to evaluate and compare the performance of Large Language Model (LLM) service providers. By setting a fixed prompt and input token, LLMetrics ensures a standardized testing environment to assess key performance metrics across providers. The tool measures essential benchmarks such as time to first token, total response time, and the time intervals between token generation. This data-driven approach provides valuable insights into the efficiency and responsiveness of LLM providers like OpenAI, Perplexity, Hyperbolic, and others. LLMetrics empowers developers and organizations to make informed
                decisions when selecting an LLM provider for their applications, ensuring optimal performance and user experience.. <br />
                LLMetrics is a part of the <Link target="_blank" href={'https://vhive-serverless.github.io/'}>vHive Ecosystem.</Link>

              </Typography>
            </CardContent>



          </Card>

        </Grid>


      </Container>
    </Page>
  );
}
