from benchmarking.benchmark import Benchmark
from providers.together_ai_provider import TogetherAI
from providers.cloudflare_provider import Cloudflare
from providers.open_ai_provider import Open_AI

models = ["mistral-7b-instruct-v0.1"] # "google-gemma-2b-it" meta-llama-3.1-70b-instruct
prompt = "What are some fun things to do in New York? Give me 1 short example."
providers = [TogetherAI(), Cloudflare(), Open_AI()]
num_requests = 1

b = Benchmark(providers, num_requests, models, prompt, streaming=True)
b.run()