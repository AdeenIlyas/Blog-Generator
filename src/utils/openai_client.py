import openai

class OpenAIClient:
    _instance = None
    client = None

    @classmethod
    def initialize(cls, api_key):
        if not cls._instance:
            openai.api_key = api_key
            cls.client = openai
            cls._instance = cls()
        return cls._instance

    @classmethod
    def get_client(cls):
        return cls.client 