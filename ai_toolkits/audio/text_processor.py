import logging
from .base import BaseTextHandler
from ai_toolkits.llms.openai_provider import create_async_client
import asyncio

class PrintOutTextHandler(BaseTextHandler):
    def __init__(self, text_queue:asyncio.Queue = None):
        super().__init__(text_queue)

    async def do_process(self, text: str) -> str:
        print(f"Transcription: {text}")
        return text

class TranslateTextHandler(BaseTextHandler):
    
    def __init__(self, text_queue:asyncio.Queue = None):
        super().__init__(text_queue)
        self.client = create_async_client()
        self.text_queue = text_queue
        
    async def do_process(self, text: str) -> str:
        translation = await self.client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": f"Translate the following text to English: {text}, do not add any other explanations."}],
        )
        print(f"Translation: {translation.choices[0].message.content}")
        return translation.choices[0].message.content
