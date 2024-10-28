from openai import OpenAI
from providers.base_provider import BaseProvider
import os

class Open_AI(BaseProvider):
    def __init__(self):
        open_ai_api = os.environ["OPEN_AI_API"]
        super().__init__(api_key=open_ai_api, client_class=OpenAI)
        # model names 
        self.model_map = {
            "3b-instruct": "gpt-4o-mini", # speculative: 8-40b
            "7b-instruct": "gpt-4o", # speculative: 200-1000b
            "70b-instruct" : "gpt-4" # 1000-1800b
        }

