from ai_toolkits.audio.real_time import RealTimeTask
from ai_toolkits.audio.microphone import MicrophoneClient
from ai_toolkits.audio.text_processor import (
    TranslateTextHandler, 
    ShortAnswerTextHandler,
    ConversationHandler,
    ConversationStreamHandler
)

def create_translator() -> RealTimeTask:
    translation_handler = TranslateTextHandler()
    task = RealTimeTask(
        audio_input_provider=MicrophoneClient(duration=120),
        text_handler=translation_handler
    )
    return task

def create_stateless_conversation_bot() -> RealTimeTask:
    short_answer_handler = ShortAnswerTextHandler()
    task = RealTimeTask(
        audio_input_provider=MicrophoneClient(duration=120),
        text_handler=short_answer_handler
    )
    return task

def create_conversation_bot(system_prmopt:str = None) -> RealTimeTask:
    
    if system_prmopt is None:
        system_prmopt = "You are a helpful assistant, You provide concise and colloquial style answers."
        
    conversation_handler = ConversationHandler(system_prompt=system_prmopt)
    
    task = RealTimeTask(
        audio_input_provider=MicrophoneClient(duration=120),
        text_handler=conversation_handler
    )
    return task

def create_streaming_conversation_bot(
    system_prmopt:str = None, 
    duration_seconds: int = 120) -> RealTimeTask:
    
    if system_prmopt is None:
        system_prmopt = "You are a helpful assistant, You provide concise and colloquial style answers."
        
    conversation_handler = ConversationStreamHandler(system_prompt=system_prmopt)
    
    task = RealTimeTask(
        audio_input_provider=MicrophoneClient(duration=duration_seconds),
        text_handler=conversation_handler
    )
    return task

