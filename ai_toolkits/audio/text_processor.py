import logging
from .base import BaseTextHandler
from ai_toolkits.llms.openai_provider import create_async_client
import asyncio
logger = logging.getLogger(__name__)

class PrintOutTextHandler:
    def __init__(self, text_queue:asyncio.Queue = None):
        self.text_queue = text_queue or asyncio.Queue()
        
    def bind_text_queue(self, text_queue:asyncio.Queue):
        self.text_queue = text_queue
        
    async def process_text(self):
        try:
            while True:
                try:
                    item = await asyncio.wait_for(self.text_queue.get(), timeout=1.0)
                    print("Recognized:", item)
                    self.text_queue.task_done()
                except asyncio.TimeoutError:
                    continue
                except asyncio.CancelledError:
                    break
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            logger.info("Text queue consumer cancelled")
            raise
        
        
class TranslateTextHandler:
    def __init__(self, text_queue:asyncio.Queue = None):
        self.text_queue = text_queue or asyncio.Queue()
        self.client = create_async_client()
    def bind_text_queue(self, text_queue:asyncio.Queue):
        self.text_queue = text_queue
        
    async def process_text(self):
        try:
            while True:
                try:
                    item = await asyncio.wait_for(self.text_queue.get(), timeout=1.0)
                    translation = await self.client.chat.completions.create(
                        model="gpt-4.1",    
                        messages=[{"role": "user", "content": f"Translate the following text to English: {item}, do not add any other explanations."}],
                    )
                    translated = f"Translated: {translation.choices[0].message.content}"
                    print("Translation:", translated)
                    self.text_queue.task_done()
                except asyncio.TimeoutError:
                    continue
                except asyncio.CancelledError:
                    break
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            logger.info("Text queue consumer cancelled")
            raise