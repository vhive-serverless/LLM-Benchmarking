from providers.base_provider import BaseProvider
import os
from together import Together

class TogetherAI(BaseProvider):
    def __init__(self):
        together_api = os.environ["TOGETHER_AI_API"]
        super().__init__(api_key=together_api, client_class=Together)

        # model names 
        self.model_map = {
            "2b-it": "google/gemma-2b-it",
            "3b-instruct": "meta-llama/Llama-3.2-3B-Instruct-Turbo",
            "7b-instruct": "mistralai/Mistral-7B-Instruct-v0.1",
            "70b-instruct": "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
            "405b-instruct": "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo"
        }