import logging
# logging.basicConfig(level=logging.INFO)
from ai_toolkits.audio.audio_apps import create_conversation_bot


if __name__ == "__main__": 
    bot = create_conversation_bot()
    # bot = create_conversation_bot("You are a helpful chat assistant, you only reply with short emojis.")
    bot.run_app()