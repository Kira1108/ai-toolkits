"""
Audio Agent Frame Types

This module defines the frame structure for audio agent communication.
Frames are used to transport data through asyncio queues between different
components of the audio processing pipeline.
"""

from typing import Literal, Any
from uuid import uuid4
from pydantic import BaseModel, Field
import time

DEFAULT_SAMPLING_RATE = 8000


def _time_in_millis() -> int:
    """Generate current timestamp in milliseconds."""
    return int(time.time() * 1000)


def _create_unique_id() -> str:
    """Generate a unique identifier for frames."""
    return str(uuid4())


class Frame(BaseModel):
    """
    Base frame class for all communication frames.
    
    This is the foundation class that all frame types inherit from.
    It provides basic metadata for frame identification and timing.
    
    Attributes:
        frame_type: The type of frame - either "message" or "event"
        frame_created: Timestamp when the frame was created (milliseconds)
        frame_id: Unique identifier for the frame
    """
    frame_type: Literal["message", "event"]
    frame_created: float = Field(default_factory=_time_in_millis)
    frame_id: str = Field(default_factory=_create_unique_id)
    
    def is_message_frame(self) -> bool:
        """
        Check if this frame is a message frame.
        
        Returns:
            bool: True if frame_type is "message", False otherwise
        """
        return self.frame_type == "message"
    
    def is_event_frame(self) -> bool:
        """
        Check if this frame is an event frame.
        
        Returns:
            bool: True if frame_type is "event", False otherwise
        """
        return self.frame_type == "event"
    
    @classmethod
    def get_frame_class_name(cls) -> str:
        """
        Get the class name for type identification.
        
        Returns:
            str: The name of the frame class
        """
        return cls.__name__
    

class EventFrame(Frame):
    """
    Event frame for carrying event notifications.
    """
    pass


class MessageFrame(Frame):
    """
    Message frame for carrying data payload.
    
    MessageFrame extends the base Frame with data content and data type
    classification. This is the parent class for all frames that carry
    actual data (audio, text, JSON, etc.).
    
    Attributes:
        data: The content of the frame (audio bytes, text, JSON, etc.)
        frame_type: Fixed to "message" for all message frames
        data_type: The type of data contained in this frame
    """
    data: Any
    frame_type: Literal["message"] = "message"
    data_type: Literal['audio', "text", "json"]
    
    def is_audio_frame(self) -> bool:
        """
        Check if this frame contains audio data.
        
        Returns:
            bool: True if data_type is "audio", False otherwise
        """
        return self.data_type == "audio"
    
    def is_text_frame(self) -> bool:
        """
        Check if this frame contains text data.
        
        Returns:
            bool: True if data_type is "text", False otherwise
        """
        return self.data_type == "text"
    
    def is_json_frame(self) -> bool:
        """
        Check if this frame contains JSON data.
        
        Returns:
            bool: True if data_type is "json", False otherwise
        """
        return self.data_type == "json"
    

class AudioInputFrame(MessageFrame):
    """
    Audio input frame with audio-specific metadata.
    
    This frame carries raw audio data along with audio processing metadata.
    It inherits frame_type="message" from MessageFrame and sets data_type="audio".
    Used for transporting audio data through the processing pipeline.
    
    Attributes:
        data: Raw audio data in bytes format
        data_type: Fixed to "audio" for audio frames
        sequence_id: Sequential number for ordering audio frames (-1 if not set)
        sampling_rate: Audio sampling rate in Hz (default: 8000Hz)
    """
    data: bytes  # Override with more specific type
    data_type: Literal['audio'] = 'audio'  # Override with fixed value
    sequence_id: int = Field(default=-1)
    sampling_rate: int = Field(default=DEFAULT_SAMPLING_RATE)
    
    def __len__(self) -> int:
        """
        Get the length of audio data.
        
        Returns:
            int: Number of bytes in the audio data
        """
        return len(self.data)
    
    
class TextInputFrame(MessageFrame):
    """
    Text input frame with text-specific metadata.
    
    This frame carries transcribed text data along with timing information
    that correlates the text back to the original audio segments.
    It inherits frame_type="message" from MessageFrame and sets data_type="text".
    
    Attributes:
        data: Transcribed text as a string
        data_type: Fixed to "text" for text frames
        start_audio_time: Start timestamp of the associated audio segment
        end_audio_time: End timestamp of the associated audio segment  
        start_audio_sequence_id: Sequence ID of the first audio frame
        end_audio_sequence_id: Sequence ID of the last audio frame
    """
    data: str  # Override with more specific type
    data_type: Literal['text'] = 'text'  # Override with fixed value
    start_audio_time: float = Field(default=-1)
    end_audio_time: float = Field(default=-1)
    start_audio_sequence_id: int = Field(default=-1)
    end_audio_sequence_id: int = Field(default=-1)
    
    def __len__(self) -> int:
        """
        Get the length of text data.
        
        Returns:
            int: Number of characters in the text data
        """
        return len(self.data)
    
    
class StreamTextInputFrame(TextInputFrame):
    
    """
    Streaming text input frame with additional flags.
    This frame extends TextInputFrame by adding flags to indicate
    whether the text segment is the start or end of a stream.
    
    Attributes:
        is_start: Flag indicating if this is the start of a stream
        is_end_bool: Flag indicating if this is the end of a stream
    """
    data:str = None
    data_type: Literal['text'] = 'text' 
    start_audio_time: float = Field(default=-1)
    end_audio_time: float = Field(default=-1)
    start_audio_sequence_id: int = Field(default=-1)
    end_audio_sequence_id: int = Field(default=-1)
    is_start:bool = Field(default=False)
    is_end_bool:bool = Field(default=False)
