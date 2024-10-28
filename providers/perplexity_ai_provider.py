from openai import OpenAI
from providers.base_provider import BaseProvider
import os


class PerplexityAI(BaseProvider):
    def __init__(self):
        perplexity_api = os.environ.get("PERPLEXITY_AI_API")
        
        if not perplexity_api:
            raise ValueError("Perplexity AI API token must be provided as an environment variable.")
        
        client_class = OpenAI 
        base_url = "https://api.perplexity.ai"  
        
        super().__init__(api_key=perplexity_api, client_class=client_class, base_url=base_url)

        # model names mapping
        self.model_map = {
            "70b-instruct": "llama-3.1-70b-instruct",  # 70b
            "8b-instruct": "llama-3.1-8b-instruct",    # 8b
            "405b-instruct": "llama-3.1-sonar-huge-128k-online"  # 405B
        }
