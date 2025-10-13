import logging
from abc import ABC, abstractmethod
from typing import Any, Optional, Union, Protocol
import asyncio

class AudioStreamReader(Protocol):
    async def receive_audio(self) -> None:
        ...
        
class BaseSTT(Protocol):
    async def send_audio(self) -> None:
        ...
        
    async def receive_results(self) -> None:
        ...
          
class BaseTextHandler:
    
    def __init__(self, text_queue:asyncio.Queue = None):
        self.text_queue = text_queue or asyncio.Queue()
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def bind_text_queue(self, text_queue:asyncio.Queue):
        self.text_queue = text_queue
        
    @abstractmethod
    async def do_process(self, text: str) -> str:
        raise NotImplementedError("Subclasses must implement this method")
        
    async def process_text(self):
        try:
            while True:
                try:
                    item = await asyncio.wait_for(self.text_queue.get(), timeout=1.0)
                    processed = await self.do_process(item)
                    end_call = "再见" in processed or "拜" in processed
                    if end_call:
                        print("Detected end call phrase, stopping processing.")
                        self.text_queue.task_done()
                        break
                    self.logger.info(f"Processed text: {processed}")
                    self.text_queue.task_done()
                except asyncio.TimeoutError:
                    continue
                except asyncio.CancelledError:
                    break
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            self.logger.info("Text queue consumer cancelled")
            raise