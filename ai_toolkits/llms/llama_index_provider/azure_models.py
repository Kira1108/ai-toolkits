from llama_index.llms.azure_openai import AzureOpenAI 
from dotenv import load_dotenv
from pathlib import Path
import os

class LlamaIndeAzureOpenAI(AzureOpenAI):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    @classmethod
    def from_dotenv(cls, env_path:str = None, **kwargs):
        """
        Creates an AzureOpenAI instance with credentials loaded from environment variables.

        Args:
            env_path (str): Path to the .env file containing the environment variables.
        Returns:
            AzureOpenAI: An instance of AzureOpenAI with the loaded credentials.
        Raises:
            ValueError: If any of the required environment variables are missing.
        """
        
        if env_path is None:
            env_path = str(Path.home() / ".env")
        
        load_dotenv(env_path)

        api_version = os.getenv("OPENAI_API_VERSION", None)
        api_key = os.getenv("AZURE_OPENAI_API_KEY", None)
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", None)

        if not all([api_version, api_key, azure_endpoint]):
            raise ValueError("Please set the OPENAI_API_VERSION, AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT environment variables in your .env file.")

        return cls(
            api_version= api_version,
            api_key= api_key,
            azure_endpoint= azure_endpoint,
            **kwargs
            )
        

if __name__ == "__main__":
    llm = LlamaIndeAzureOpenAI.from_dotenv(model = 'gpt-4o', deployment_name = 'gpt-4o')
    print(llm.complete("hi what is your name?"))
