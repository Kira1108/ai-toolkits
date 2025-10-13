from ai_toolkits.audio.real_time import RealTimeTask
from ai_toolkits.audio.tencent_asr import TencentASR
from ai_toolkits.audio.microphone import MicrophoneClient
from ai_toolkits.audio.text_processor import (
    TranslateTextHandler, 
    ShortAnswerTextHandler,
    ConversationHandler,
    ConversationStreamHandler,
    SpeakOutStreamHandler
)
from openai import AsyncClient

def create_translator() -> RealTimeTask:
    translation_handler = TranslateTextHandler()
    task = RealTimeTask(
        audio_input_provider=MicrophoneClient(duration=120),
        text_handler=translation_handler,
        trace_conversation=False
    )
    return task

def create_stateless_conversation_bot() -> RealTimeTask:
    short_answer_handler = ShortAnswerTextHandler()
    task = RealTimeTask(
        audio_input_provider=MicrophoneClient(duration=120),
        text_handler=short_answer_handler,
        trace_conversation=False
    )
    return task

def create_conversation_bot(system_prmopt:str = None) -> RealTimeTask:
    
    if system_prmopt is None:
        system_prmopt = "You are a helpful assistant, You provide concise and colloquial style answers."
        
    conversation_handler = ConversationHandler(system_prompt=system_prmopt)
    
    task = RealTimeTask(
        audio_input_provider=MicrophoneClient(duration=120),
        text_handler=conversation_handler,
        trace_conversation=False
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
        text_handler=conversation_handler,
        stt_service=TencentASR(vad_silence=1800),
        trace_conversation=False
    )
    return task


def create_streaming_conversation_bot_qwen3(
    system_prmopt:str = None,
    duration_seconds: int = 120,
    extra_body: dict = None,
    async_client:AsyncClient = None,
    create_trace:bool = True
    ) -> RealTimeTask:
    
    if extra_body is None:
        extra_body = {
            "chat_template_kwargs": {
                "enable_thinking": False,
                "separate_reasoning": True
            }
        }
    conversation_handler = ConversationStreamHandler(
        system_prompt=system_prmopt if system_prmopt else "You are a helpful assistant, You provide concise and colloquial style answers.",
        extra_body=extra_body,
        async_client=async_client
    )
    task = RealTimeTask(
        audio_input_provider=MicrophoneClient(duration=duration_seconds),
        text_handler=conversation_handler,
        stt_service=TencentASR(vad_silence=1800),
        trace_conversation=create_trace
    )
    return task

def create_siri_bot(
    system_prmopt:str = None, 
    duration_seconds: int = 120) -> RealTimeTask:
    
    if system_prmopt is None:
        system_prmopt = "You are a helpful assistant, You provide concise and colloquial style answers."
        
    
    conversation_handler = SpeakOutStreamHandler(system_prompt=system_prmopt)
    
    task = RealTimeTask(
        audio_input_provider=MicrophoneClient(duration=duration_seconds),
        text_handler=conversation_handler,
        stt_service=TencentASR(vad_silence=1000),
        trace_conversation=False
    )
    return task