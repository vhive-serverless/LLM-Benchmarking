import os
import os
from openai import OpenAI
from providers.base_provider import BaseProvider

class PerplexityAI(BaseProvider):
    """ perplexity provider class """
    def __init__(self):
        """
        Initializes the AnthropicProvider with the necessary API key and client.
        """
        perplexity_api = os.environ.get("PERPLEXITY_AI_API")

        if not perplexity_api:
            raise ValueError(
                "Perplexity AI API token must be provided as an environment variable."
            )

        client_class = OpenAI
        base_url = "https://api.perplexity.ai"

        super().__init__(
            api_key=perplexity_api, client_class=client_class, base_url=base_url
        )

        # model names mapping
        self.model_map = {
            "meta-llama-3.1-70b-instruct": "llama-3.1-70b-instruct",  # 70b
            "meta-llama-3.1-8b-instruct": "llama-3.1-8b-instruct",  # 8b
            "meta-llama-3.1-sonar-405B": "llama-3.1-sonar-huge-128k-online",  # 405B
        }
