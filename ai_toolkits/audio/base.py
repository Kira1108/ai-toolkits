from abc import ABC, abstractmethod
from typing import Any, Optional, Union, Protocol


class AudioStreamReader(Protocol):
    async def receive_audio(self) -> None:
        ...
        
class BaseSTT(Protocol):
    async def send_audio(self) -> None:
        ...
        
    async def receive_results(self) -> None:
        ...
        
        
class BaseTextHandler(Protocol):
    async def process_text(self):
        ...