from openai import AzureOpenAI, AsyncAzureOpenAI
from dotenv import load_dotenv
from pathlib import Path
load_dotenv(str(Path.home() / ".env"))

def create_sync_client(*args, **kwargs):
    return AzureOpenAI(*args, **kwargs)

def create_async_client(*args, **kwargs):
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