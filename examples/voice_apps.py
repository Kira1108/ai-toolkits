# import logging
# # logging.basicConfig(level=logging.INFO)
# from ai_toolkits.audio.audio_apps import create_conversation_bot


# if __name__ == "__main__": 
#     bot = create_conversation_bot()
#     # bot = create_conversation_bot("You are a helpful chat assistant, you only reply with short emojis.")
#     bot.run_app()


from ai_toolkits.audio.real_time import RealTimeTask
from ai_toolkits.audio.microphone import MicrophoneClient
from ai_toolkits.audio.text_processor import (
    TranslateTextHandler, 
    ShortAnswerTextHandler,
    ConversationHandler,
    ConversationStreamHandler
)


conversation_handler = ConversationStreamHandler()

task = RealTimeTask(
    audio_input_provider=MicrophoneClient(duration=120),
    text_handler=conversation_handler
)
task.run_app()

