// material
import { Grid, Card, Container, Stack, Box, Typography, CardContent, Link } from '@mui/material';
import ListItem from '@mui/material/ListItem';
// components
import Page from '../components/Page';

export default function LLMetrics() {
  return (
    <Page title="Dashboard: LLMetrics">
      <Container maxWidth="xl">
        <Stack direction="row" alignItems="center" justifyContent="space-between" mt={3}>
          {/* <Typography variant="h4" gutterBottom>
          LLMetrics
          </Typography> */}
        </Stack>

        <Grid item xs={12} mb={3}>
          <Card>
            <CardContent>
              <Typography variant='h4' marginBottom={3}>
                What is LLMetrics? (Large Language Model Metrics)
              </Typography>
              <Typography variant='p'>
                LLMetrics is a benchmarking tool designed to evaluate and compare the performance of Large Language Model (LLM) service providers. By using a fixed prompt, input token, and output token across all providers, LLMetrics ensures a standardized testing environment for accurate performance assessments. <br /><br />

                The tool measures essential benchmarks, such as:
              </Typography>
              <Box sx={{ ml: 5, my: 2 }}>
                <ListItem sx={{ display: 'list-item' }}>
                  <b>Time to First Token:</b> The time it takes for the first token of a response to be generated.
                </ListItem>
                <ListItem sx={{ display: 'list-item' }}>
                  <b>Time Between Tokens:</b> The time interval between the generation of consecutive tokens.
                </ListItem>
                <ListItem sx={{ display: 'list-item' }}>
                  <b>Total Response Time:</b> The overall time taken to generate the complete response.
                </ListItem>
              </Box>

              <Typography variant='p'>
                This data-driven approach provides valuable insights into the efficiency and responsiveness of various LLM providers, empowering developers and organizations to make informed decisions when selecting a provider for their applications. <br /><br />

                LLMetrics currently benchmarks the following providers:
              </Typography>
              <Box sx={{ ml: 5, my: 2 }}>
                <ListItem sx={{ display: 'list-item' }}>Anthropic</ListItem>
                <ListItem sx={{ display: 'list-item' }}>AWS</ListItem>
                <ListItem sx={{ display: 'list-item' }}>Azure</ListItem>
                <ListItem sx={{ display: 'list-item' }}>Cloudflare</ListItem>
                <ListItem sx={{ display: 'list-item' }}>Google</ListItem>
                <ListItem sx={{ display: 'list-item' }}>Groq</ListItem>
                <ListItem sx={{ display: 'list-item' }}>Hyperbolic</ListItem>
                <ListItem sx={{ display: 'list-item' }}>OpenAI</ListItem>
                <ListItem sx={{ display: 'list-item' }}>Perplexity</ListItem>
                <ListItem sx={{ display: 'list-item' }}>Together AI</ListItem>
              </Box>

              <Typography variant='p'>
                To achieve these benchmarks, we make requests to all providers using the same input and output token configurations. Our benchmarking runs are conducted weekly via a GitHub Actions workflow, ensuring consistency and regularity in the performance evaluations. The collected experiment data is securely stored in a DynamoDB database for analysis and visualization. <br /><br />
                LLMetrics is a part of the <Link target="_blank" href={'https://vhive-serverless.github.io/'}>vHive Ecosystem.</Link>
              </Typography>

              <Typography variant='h4' marginTop={5} marginBottom={3}>
                Single Request End-to-End Metric
              </Typography>
              <Typography variant='p'>
                The single request end-to-end metric measures the total response time for a non-streaming request sent to an LLM provider. Unlike streaming benchmarks, this metric captures the duration from the moment the request is initiated until the complete response is received. <br /><br />

                This metric is critical for evaluating the performance of non-streaming LLM workflows, where latency directly impacts user experience in applications such as chatbots, content generation tools, and other interactive systems. <br /><br />

                By analyzing the single request end-to-end metric, developers can identify bottlenecks in response handling and optimize their integration with LLM providers for improved efficiency.
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Container>
    </Page>
  );
}
