from openai import AsyncClient
from pydantic_ai import Agent
from pydantic_ai.models.openai import ModelSettings, OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider
from pydantic_ai.providers.openai import OpenAIProvider


def create_ollama_model(model_name:str = 'gpt-oss:20b') -> OpenAIChatModel:
    """Create and return an OpenAIChatModel configured to use the Ollama provider."""
    return OpenAIChatModel(
        model_name=model_name,
        provider=OllamaProvider(base_url='http://localhost:11434/v1'),
    )
    
def create_openai_like(
    model_name:str,
    api_key:str, 
    base_url:str,
    default_headers = None, 
    extra_body = None,
    **kwargs):
    """
    Create openai like pydantic-compatible model.
    Tested with sglang deployed models
    """
    
    client_args = {
        "api_key": api_key,
        "base_url": base_url
    }
    
    if default_headers:
        client_args.update({
            "default_headers": default_headers
        })
        
    client = AsyncClient(**client_args)
    
    if extra_body:
        model_settings = ModelSettings(
            extra_body=extra_body,
            **kwargs
        )    
    else:
        model_settings = ModelSettings(
            **kwargs
        )
        
    return OpenAIChatModel(
        model_name = model_name,
        provider = OpenAIProvider(openai_client=client),
        settings = model_settings
        
    )

if __name__ == "__main__":
    from pydantic_ai import Agent
    agent = Agent(model = create_ollama_model())
    res = agent.run_sync("Write a haiku about AI in the style of Basho.")
    print(res)