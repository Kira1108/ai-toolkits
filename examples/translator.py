import logging
# logging.basicConfig(level=logging.INFO)
from ai_toolkits.audio.real_time import RealTimeTask
from ai_toolkits.audio.text_processor import TranslateTextHandler
import asyncio


if __name__ == "__main__": 
    translate_handler = TranslateTextHandler()
    task = RealTimeTask(text_handler=translate_handler)
    asyncio.run(task.run())