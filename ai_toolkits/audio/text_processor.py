import logging
from .base import BaseTextHandler
import asyncio
logger = logging.getLogger(__name__)

class PrintOutTextHandler:
    def __init__(self, text_queue:asyncio.Queue):
        self.text_queue = text_queue
        
    async def process_text(self):
        try:
            while True:
                try:
                    item = await asyncio.wait_for(self.text_queue.get(), timeout=1.0)
                    print(f"Transcription: {item}")
                    self.text_queue.task_done()
                except asyncio.TimeoutError:
                    continue
                except asyncio.CancelledError:
                    break
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            logger.info("Text queue consumer cancelled")
            raise