from openai import AzureOpenAI, AsyncAzureOpenAI
from ai_toolkits.load_env import load_environment

def create_sync_client(*args, **kwargs):
    load_environment()  
    return AzureOpenAI(*args, **kwargs)

def create_async_client(*args, **kwargs):
    load_environment()  
    return AsyncAzureOpenAI(*args, **kwargs)

def test_openai_clients():
    client = create_sync_client()
    async_client = create_async_client()

    res = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print("[Sync client] Response:")
    print(res)

    import asyncio
    async_res = asyncio.run(async_client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": "Hello!"}]
    ))

    print("[Async client] Response:")
    print(async_res)
    
if __name__ == "__main__":
    test_openai_clients()