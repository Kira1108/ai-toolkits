import logging
logging.basicConfig(level=logging.INFO)
from ai_toolkits.audio.transcribe import RealTimeTask
import asyncio


if __name__ == "__main__": 
    task = RealTimeTask()
    asyncio.run(task.run())