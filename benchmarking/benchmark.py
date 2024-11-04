# import matplotlib.pyplot as plt
# import numpy as np

# class Benchmark:
#     def __init__(self, providers, num_requests, models, prompt, streaming=False):
#         self.providers = providers
#         self.num_requests = num_requests
#         self.models = models
#         self.prompt = prompt
#         self.streaming = streaming

#     def plot_metrics(self, metric):
#         plt.figure(figsize=(8, 8))
        
#         for provider in self.providers:
#             provider_name = provider.__class__.__name__
#             for model, latencies in provider.metrics[metric].items():
#                 # Convert to milliseconds and sort for CDF
#                 latencies_sorted = np.sort(latencies) * 1000
#                 cdf = np.arange(1, len(latencies_sorted) + 1) / len(latencies_sorted)
#                 model_name = provider.get_model_name(model)
#                 # Plot each model's CDF
#                 plt.plot(latencies_sorted, cdf, marker='o', linestyle='-', markersize=5, label=f'{provider_name} - {model_name}')

#         # Add title, labels, and grid
#         # plt.title('Latency Comparison of 3 Models')
#         plt.xlabel('Latency (ms)', fontsize=12)
#         plt.ylabel('Portion of requests', fontsize=12)
#         plt.grid(True)

#         # Add legend
#         plt.legend(loc='lower right')
#         plt.xscale('log')
        
#         # Show the plot
#         plt.tight_layout()
#         plt.show()

#         return plt 
    
#     def run(self):

#         for provider in self.providers:

#             display(Markdown(f"### {provider.__class__.__name__}"))
#             for model in self.models:
#                 model_name = provider.get_model_name(model)
#                 display(Markdown(f"#### Model: {model_name}\n #### Prompt: {self.prompt}"))
                
#                 for _ in range(self.num_requests):
                    
#                     display(Markdown(f'Request {_}'))
#                     if self.streaming:
#                         provider.perform_inference_streaming(model, self.prompt)

#                     else:
#                         provider.perform_inference(model, self.prompt)
