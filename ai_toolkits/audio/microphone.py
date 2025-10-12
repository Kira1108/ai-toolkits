import asyncio
import pyaudio
import json
import logging
logger = logging.getLogger(__name__)

class MicrophoneClient:
    def __init__(self,
        audio_input_queue: asyncio.Queue = None,
        sampling_rate: int = 8000, 
        chunk_ms: int = 40, 
        channels: int = 1,
        duration:int = 8):
        
        self.audio_input_queue = audio_input_queue if audio_input_queue is not None else asyncio.Queue()
        self.sampling_rate = sampling_rate
        self.chunk_size = int(sampling_rate * (chunk_ms / 1000))
        self.channels = channels
            
        self.port_audio = pyaudio.PyAudio()
        self.duration = duration
        self.stream = self.port_audio.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=sampling_rate,
            input=True,
            frames_per_buffer=self.chunk_size)
        
        
    async def receive_audio(self):
        logger.info("Starting audio recording...")
        start = asyncio.get_event_loop().time()
        while self.stream.is_active():
            if asyncio.get_event_loop().time() - start > self.duration:
                logger.info("Recording duration reached, stopping.")
                await self.audio_input_queue.put(json.dumps({"type": "end"}))
                await asyncio.sleep(100)
            data = self.stream.read(self.chunk_size, exception_on_overflow=False)
            await self.audio_input_queue.put(data)
            await asyncio.sleep(0.01)
        