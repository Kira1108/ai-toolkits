from llama_index.llms.azure_openai import AzureOpenAI 
from ai_toolkits.load_env import load_environment, get_required_env_var

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
        
        # Load environment variables using centralized configuration
        load_environment(env_path)

        try:
            api_version = get_required_env_var("OPENAI_API_VERSION")
            api_key = get_required_env_var("AZURE_OPENAI_API_KEY")
            azure_endpoint = get_required_env_var("AZURE_OPENAI_ENDPOINT")
        except ValueError as e:
            raise ValueError(f"Missing required environment variables: {e}")

        return cls(
            api_version= api_version,
            api_key= api_key,
            azure_endpoint= azure_endpoint,
            **kwargs
            )
        

if __name__ == "__main__":
    llm = LlamaIndeAzureOpenAI.from_dotenv(model = 'gpt-4o', deployment_name = 'gpt-4o')
    print(llm.complete("hi what is your name?"))
