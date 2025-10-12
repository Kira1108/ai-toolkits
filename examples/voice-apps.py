import logging
# logging.basicConfig(level=logging.INFO)
from ai_toolkits.audio.real_time import RealTimeTask
from ai_toolkits.audio.microphone import MicrophoneClient
from ai_toolkits.audio.text_processor import (
    TranslateTextHandler, 
    ShortAnswerTextHandler,
    ConversationHandler
)
import asyncio


if __name__ == "__main__": 
    translate_handler = TranslateTextHandler()
    short_answer_handler = ShortAnswerTextHandler()
    conversation_handler = ConversationHandler()
    task = RealTimeTask(
        audio_input_provider=MicrophoneClient(duration=120),
        text_handler=conversation_handler
    )
    task.run_app()