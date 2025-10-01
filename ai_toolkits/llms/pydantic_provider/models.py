from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.ollama import OllamaProvider

def create_ollama_model(model_name:str = 'gpt-oss:20b') -> OpenAIChatModel:
    """Create and return an OpenAIChatModel configured to use the Ollama provider."""
    return OpenAIChatModel(
        model_name=model_name,
        provider=OllamaProvider(base_url='http://localhost:11434/v1'),
    )
    
if __name__ == "__main__":
    from pydantic_ai import Agent
    agent = Agent(model = create_ollama_model())
    res = agent.run_sync("Write a haiku about AI in the style of Basho.")
    print(res)