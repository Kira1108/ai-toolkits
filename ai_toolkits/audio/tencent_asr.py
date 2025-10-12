from __future__ import annotations

import asyncio
import base64
import hashlib
import hmac
import json
import logging
import random
import time
import urllib.parse
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
from uuid import uuid4

import websockets
from pydantic import BaseModel, Field
import os
from ai_toolkits.load_env import get_env_var

# Configuration
BASE_URL = get_env_var("TENCENT_ASR_BASE_URL") 
PART_URL = get_env_var("TENCENT_ASR_PART_URL") 
SECRET_KEY = get_env_var("TENCENT_ASR_SECRET_KEY")
SECRET_ID = get_env_var("TENCENT_ASR_SECRET_ID")


class ASRConnectionState(Enum):
    """ASR connection states."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ENDING = "ending"


class TencentASRResponse(BaseModel):
    """Represents a response from Tencent ASR service."""
    
    sentence: str = Field(..., description="ASR recognition result")
    start_time: int = Field(..., description="speech start time (ms)")
    end_time: int = Field(..., description="speech end time (ms)")
    slice_type: int = Field(..., description="result type: 0=start, 1=speaking, 2=end")
    final: int = Field(..., description="final flag: 0=recognizing, 1=finish")
    
    @classmethod
    def from_tencent_data(cls, data: dict) -> 'TencentASRResponse':
        """
        Create ASRResponse from Tencent API response data.
        
        Handles two types of responses:
        1. Recognition results: {'result': {'voice_text_str': '...', 'final': 1, ...}}
        2. Final completion: {'code': 0, 'message': 'success', 'final': 1, ...}
        """
        if 'result' in data:
            # Standard recognition result
            result = data['result']
            return cls(
                sentence=result.get('voice_text_str', ''),
                start_time=result.get('start_time', 0),
                end_time=result.get('end_time', 0),
                slice_type=result.get('slice_type', 0),
                final=result.get('final', 0)
            )
        else:
            # Final completion message
            return cls(
                sentence='',  # No text in final completion message
                start_time=0,
                end_time=0,
                slice_type=0,
                final=data.get('final', 0)  # Final flag is at top level
            )
        
    @property
    def is_vad_end(self) -> bool:
        """Check if this is a VAD (Voice Activity Detection) end result."""
        return self.slice_type == 2
    
    @property
    def is_final_result(self) -> bool:
        """Check if this is the final recognition result."""
        return self.final == 1
    
    @property
    def has_content(self) -> bool:
        """Check if this response contains transcribed text."""
        return bool(self.sentence.strip())


def _generate_unique_id() -> str:
    """Generate a unique ID for voice session."""
    return base64.urlsafe_b64encode(uuid4().bytes).rstrip(b'=').decode('ascii')


def _url_encode(component: str) -> str:
    """URL encode a component."""
    return urllib.parse.quote(component)


def _generate_signature(message: str, secret_key: str = None) -> str:
    """Generate HMAC-SHA1 signature for authentication."""
    secret_key = secret_key or SECRET_KEY
    hmac_obj = hmac.new(secret_key.encode(), message.encode(), hashlib.sha1)
    hmac_digest = hmac_obj.digest()
    return base64.b64encode(hmac_digest).decode('utf-8')


def _build_api_url(vad_silence: int = 1000) -> str:
    """Build the WebSocket API URL with authentication parameters."""
    params = [
        "engine_model_type=8k_zh",
        "needvad=1",
        f"timestamp={int(time.time())}",
        f"vad_silence={vad_silence}",
        f"secretid={SECRET_ID}",
        f"expired={int((datetime.now() + timedelta(days=1)).timestamp())}",
        f"voice_id={_generate_unique_id()}",
        "voice_format=1",
        f"nonce={random.randint(100000, 999999)}",
    ]
    params.sort()
    
    query_string = "&".join(params)
    signature = _generate_signature(PART_URL + query_string)
    encoded_signature = _url_encode(signature)
    
    return f"{BASE_URL}{query_string}&signature={encoded_signature}"

class TencentASR:
    """
    Tencent ASR (Automatic Speech Recognition) client.
    
    Manages WebSocket connection to Tencent Cloud ASR service for real-time
    speech recognition. Handles audio streaming and result processing.
    """
    
    def __init__(self, 
                 audio_input_queue: Optional[asyncio.Queue] = None,
                 text_output_queue: Optional[asyncio.Queue] = None,
                 vad_silence: int = 500):
        """
        Initialize Tencent ASR client.
        
        Args:
            audio_input_queue: Queue for incoming audio data
            text_output_queue: Queue for outgoing transcription results
            vad_silence: VAD silence threshold in milliseconds
        """
        self._websocket_url = _build_api_url(vad_silence)
        self._logger = logging.getLogger(__name__)
        
        # Queues for audio and text processing
        self._audio_input_queue = audio_input_queue or asyncio.Queue()
        self._text_output_queue = text_output_queue or asyncio.Queue()
        
        # Connection management
        self._websocket: Optional[websockets.WebSocketServerProtocol] = None
        self._connection_state = ASRConnectionState.DISCONNECTED
        
        # Synchronization primitives
        self._final_result_received = asyncio.Event()
        self._end_signal_sent = False
        
    def bind_audio_queue(self, queue: asyncio.Queue) -> None:
        """Bind a new audio input queue."""
        self._audio_input_queue = queue
        
    def bind_text_queue(self, queue: asyncio.Queue) -> None:
        """Bind a new text output queue."""
        self._text_output_queue = queue
    
    @property
    def is_connected(self) -> bool:
        """Check if WebSocket is connected and ready."""
        if self._connection_state != ASRConnectionState.CONNECTED:
            return False
        if self._websocket is None:
            return False
        # Check if websocket is open (avoid using .closed which doesn't exist)
        try:
            return hasattr(self._websocket, 'send') and hasattr(self._websocket, 'recv')
        except AttributeError:
            return False
    
    @property
    def audio_input_queue(self) -> asyncio.Queue:
        """Get the audio input queue."""
        return self._audio_input_queue
    
    @property
    def text_output_queue(self) -> asyncio.Queue:
        """Get the text output queue."""
        return self._text_output_queue
    
    async def connect(self) -> None:
        """
        Connect to Tencent ASR WebSocket service.
        
        Raises:
            ConnectionError: If connection or authentication fails
        """
        if self._connection_state != ASRConnectionState.DISCONNECTED:
            self._logger.warning("Already connected or connecting")
            return
            
        self._connection_state = ASRConnectionState.CONNECTING
        
        try:
            self._logger.info(f"Connecting to ASR WebSocket at {self._websocket_url}")
            self._websocket = await websockets.connect(self._websocket_url)
            
            # Wait for authentication response
            auth_response = await asyncio.wait_for(self._websocket.recv(), timeout=10.0)
            auth_data = json.loads(auth_response)
            
            if auth_data.get('code') != 0:
                raise ConnectionError(f"ASR authentication failed: {auth_response}")
            
            self._connection_state = ASRConnectionState.CONNECTED
            self._logger.info("ASR WebSocket connection successful")
            
        except Exception as e:
            self._connection_state = ASRConnectionState.DISCONNECTED
            if self._websocket:
                await self._websocket.close()
                self._websocket = None
            self._logger.error(f"Failed to connect to ASR: {e}")
            raise
        
    async def disconnect(self) -> None:
        """Disconnect from ASR WebSocket service."""
        if self._connection_state == ASRConnectionState.DISCONNECTED:
            return
            
        try:
            if self._websocket:
                # Don't check .closed attribute, just try to close
                await self._websocket.close()
                self._logger.info("ASR WebSocket connection closed")
        except Exception as e:
            self._logger.warning(f"Error during disconnect: {e}")
        finally:
            self._websocket = None
            self._connection_state = ASRConnectionState.DISCONNECTED
        
    async def send_audio_stream(self) -> None:
        """
        Send audio data from input queue to ASR service.
        
        Continuously reads audio chunks from the input queue and sends them
        as binary messages to the ASR WebSocket. Handles end signals properly.
        """
        self._logger.info("Starting audio stream transmission")
        
        try:
            while self._connection_state == ASRConnectionState.CONNECTED:
                if not self._websocket:
                    self._logger.warning("WebSocket is None, stopping audio transmission")
                    break
                
                # Get audio chunk from queue
                audio_chunk = await self._audio_input_queue.get()
                task_completed = False
                
                try:
                    if await self._handle_audio_chunk(audio_chunk):
                        # End signal processed, stop sending
                        task_completed = True
                        break
                        
                except (websockets.exceptions.ConnectionClosedError, 
                        websockets.exceptions.ConnectionClosedOK) as e:
                    self._logger.warning(f"WebSocket closed during audio transmission: {e}")
                    break
                except Exception as e:
                    self._logger.error(f"Error sending audio chunk: {e}")
                    raise
                finally:
                    if not task_completed:
                        self._audio_input_queue.task_done()
                    
        except Exception as e:
            self._logger.error(f"Error in audio stream transmission: {e}")
            raise
        finally:
            self._logger.info("Audio stream transmission completed")
    
    async def _handle_audio_chunk(self, audio_chunk) -> bool:
        """
        Handle a single audio chunk or end signal.
        
        Args:
            audio_chunk: Audio data (bytes) or end signal (None/str)
            
        Returns:
            True if end signal was processed, False otherwise
        """
        # Handle None as end signal
        if audio_chunk is None:
            await self._send_end_signal()
            self._audio_input_queue.task_done()
            return True
        
        # Handle string-based end signal
        if isinstance(audio_chunk, str):
            if await self._handle_string_chunk(audio_chunk):
                self._audio_input_queue.task_done()
                return True
        
        # Handle binary audio data
        elif isinstance(audio_chunk, (bytes, bytearray)):
            await self._send_binary_audio(audio_chunk)
        
        else:
            self._logger.warning(f"Unexpected audio chunk type: {type(audio_chunk)}")
        
        return False
    
    async def _handle_string_chunk(self, chunk: str) -> bool:
        """Handle string-based audio chunk (might be end signal)."""
        try:
            data = json.loads(chunk)
            if data.get("type") == "end":
                await self._send_end_signal()
                return True
        except json.JSONDecodeError:
            self._logger.warning(f"Received non-JSON string data: {chunk[:100]}...")
        
        return False
    
    async def _send_binary_audio(self, audio_data: bytes) -> None:
        """Send binary audio data to ASR service."""
        if len(audio_data) > 0:
            await self._websocket.send(audio_data)
        else:
            self._logger.warning("Received empty audio chunk, skipping")
    
    async def _send_end_signal(self) -> None:
        """Send end signal to ASR service if not already sent."""
        if not self._end_signal_sent:
            end_message = json.dumps({"type": "end"})
            await self._websocket.send(end_message)
            self._end_signal_sent = True
            self._connection_state = ASRConnectionState.ENDING
            self._logger.info("Sent end signal as text message to ASR")
        else:
            self._logger.info("End signal already sent")

    async def receive_results(self) -> None:
        """
        Receive and process ASR results from WebSocket.
        
        Continuously receives messages from ASR service and processes them.
        Stops when final result is received or connection is closed.
        """
        self._logger.info("Starting to receive ASR results")
        
        try:
            while self._connection_state in (ASRConnectionState.CONNECTED, ASRConnectionState.ENDING):
                if not self._websocket:
                    self._logger.warning("WebSocket is None, stopping result reception")
                    break
                
                try:
                    message = await self._websocket.recv()
                except (websockets.exceptions.ConnectionClosedOK,
                        websockets.exceptions.ConnectionClosedError) as e:
                    self._logger.info(f"WebSocket connection closed: {e}")
                    break
                
                try:
                    if await self._process_asr_message(message):
                        # Final result received, stop processing
                        break
                        
                except (json.JSONDecodeError, Exception) as e:
                    self._logger.error(f"Error processing ASR message: {e}")
                    self._logger.error(f"Raw message: {message}")
                    continue
                    
        except Exception as e:
            self._logger.error(f"Unexpected error in result reception: {e}")
            raise
        finally:
            self._logger.info("ASR result reception completed")
    
    async def _process_asr_message(self, message: str) -> bool:
        """
        Process a single ASR message.
        
        Args:
            message: Raw message from ASR service
            
        Returns:
            True if final result was received, False otherwise
        """
        data = json.loads(message)
        self._logger.debug(f"Received ASR data: {data}")
        
        response = TencentASRResponse.from_tencent_data(data)
        
        # Log response details
        self._logger.debug(f"ASR Response - sentence: '{response.sentence}', "
                          f"slice_type: {response.slice_type}, "
                          f"final: {response.final}, "
                          f"is_vad_end: {response.is_vad_end}, "
                          f"is_final: {response.is_final_result}")
        
        # Send meaningful results to output queue
        if response.is_vad_end or response.is_final_result:
            if response.has_content:
                self._logger.info(f"Got ASR result: {response.sentence}")
                await self._text_output_queue.put(response.sentence)
        
        # Check for final result
        if response.is_final_result:
            self._logger.info("Final result received, ending ASR session")
            self._final_result_received.set()
            return True
            
        return False
    async def send_end_signal_and_wait(self) -> None:
        """
        Send end signal to ASR service and wait for final result.
        
        This method handles the graceful shutdown sequence by sending
        the end signal and waiting for the final acknowledgment.
        """
        if self._end_signal_sent:
            self._logger.info("End signal already sent, just waiting for final result")
        else:
            self._logger.info("Sending end signal to ASR service")
            await self._audio_input_queue.put(None)  # Signal send_audio to send end
        
        # Wait for final result to be received
        try:
            await asyncio.wait_for(self._final_result_received.wait(), timeout=15.0)
            self._logger.info("Final result received from ASR service")
        except asyncio.TimeoutError:
            self._logger.warning("Timeout waiting for final result from ASR service")
            
    async def wait_for_final_result(self, timeout: float = 10.0) -> bool:
        """
        Wait for final result from ASR service.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if final result was received, False if timeout
        """
        try:
            await asyncio.wait_for(self._final_result_received.wait(), timeout=timeout)
            return True
        except asyncio.TimeoutError:
            self._logger.warning(f"Timeout after {timeout}s waiting for final result")
            return False
    
    # Legacy method names for backward compatibility
    async def send_audio(self) -> None:
        """Legacy method name for send_audio_stream."""
        await self.send_audio_stream()
    
    async def send_end_signal(self) -> None:
        """Legacy method name for send_end_signal_and_wait."""
        await self.send_end_signal_and_wait()
    
    @property
    def websocket(self):
        """Legacy property for backward compatibility."""
        return self._websocket
    
    @property
    def logger(self):
        """Legacy property for backward compatibility."""
        return self._logger
    
    @property
    def audio_input_queue(self):
        """Legacy property for backward compatibility."""
        return self._audio_input_queue
    
    @property
    def text_output_queue(self):
        """Legacy property for backward compatibility."""
        return self._text_output_queue
    
    @property
    def final_received(self):
        """Legacy property for backward compatibility."""
        return self._final_result_received