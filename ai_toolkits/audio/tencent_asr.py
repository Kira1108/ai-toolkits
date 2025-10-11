from __future__ import annotations

import logging

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
from uuid import uuid4

import websockets
from pydantic import BaseModel, Field
import os
from ai_toolkits.load_env import get_env_var

BASE_URL = get_env_var("TENCENT_ASR_BASE_URL") 
PART_URL = get_env_var("TENCENT_ASR_PART_URL") 
SECRET_KEY = get_env_var("TENCENT_ASR_SECRET_KEY")
SECRET_ID = get_env_var("TENCENT_ASR_SECRET_ID")

class TencentASRResponse(BaseModel):
    sentence:str = Field(..., description = "ASR recognition result")
    start_time:int = Field(..., description = "speech start time (ms)")
    end_time:int = Field(..., description = "speech end time (ms)")
    slice_type:int = Field(..., description = "result time, 0:start（partial） 1:speaking（partial） 2: end（stable）")
    final:int = Field(..., description = "is final chunk or not, 0:recognizing 1:finish")
    
    @classmethod
    def from_tencent(cls, data:dict):
        return cls(
            sentence = data.get('result', {}).get('voice_text_str', ''),
            start_time = data.get('result', {}).get('start_time', 0),
            end_time = data.get('result', {}).get('end_time', 0),
            slice_type = data.get('result', {}).get('slice_type', 0),
            final = data.get('result', {}).get('final', 0)
        )
        
    @property
    def is_vad_end(self) -> bool:
        return self.slice_type == 2
    
    @property
    def is_final(self) -> bool:
        return self.final == 1


def make_uid():
    return base64.urlsafe_b64encode(uuid4().bytes).rstrip(b'=').decode('ascii')

def url_encode(component: str) -> str:
    return urllib.parse.quote(component)

def generate_hmac_sha1(
    message: str, 
    secret_key: str=None) -> str:
    secret_key = secret_key or SECRET_KEY
    hmac_obj = hmac.new(secret_key.encode(), message.encode(), hashlib.sha1)
    hmac_digest = hmac_obj.digest()
    hmac_base64 = base64.b64encode(hmac_digest).decode('utf-8')
    return hmac_base64

def get_api_uri(vad_slience:int = 1000) -> str:
    params = [
        "engine_model_type=8k_zh",
        "needvad=1",
        f"timestamp={int(time.time())}",
        f"vad_silence={str(vad_slience)}",
        f"secretid={SECRET_ID}",
        f"expired={int((datetime.now() + timedelta(days=1)).timestamp())}",
        f"voice_id={str(make_uid())}",
        "voice_format=1",
        "nonce=" + str(random.randint(100000, 999999)),
        
    ]
    params.sort()
    
    data = "&".join(params)
    
    signature = generate_hmac_sha1(PART_URL + data)
    signature = url_encode(signature)
    info = data + f"&signature={signature}"
    return BASE_URL + info

class TencentASR:
    
    def __init__(self, 
                 audio_input_queue: asyncio.Queue = None,
                 text_output_queue: asyncio.Queue = None):
        
        self.websocket_url = get_api_uri()
        self.logger = logging.getLogger(__name__)
        self.audio_input_queue = audio_input_queue if audio_input_queue is not None else asyncio.Queue()
        self.text_output_queue = text_output_queue if text_output_queue is not None else asyncio.Queue()

        self.websocket = None
    
    async def connect(self):
        self.logger.info(f"Connecting to ASR WebSocket at {self.websocket_url}")
        self.websocket = await websockets.connect(self.websocket_url)
        auth_response = await self.websocket.recv()
        if json.loads(auth_response).get('code') != 0:
            raise ConnectionError(f"ASR connection failed: {auth_response}")
        self.logger.info("ASR WebSocket connection successful.")
        
    async def disconnect(self):
        if self.websocket:
            await self.websocket.close()
            self.logger.info("ASR WebSocket connection closed.")
        
    async def send_audio(self):
        while True:
            final = False
            audio_chunk = await self.audio_input_queue.get()
            if isinstance(audio_chunk, str):
                audio_chunk = json.loads(audio_chunk)
                if audio_chunk.get("type") == "end":
                    final = True
            
            if (audio_chunk is None) or final :  # End signal
                    self.audio_input_queue.task_done()
                    await self.websocket.send(json.dumps({"type": "end"}))
                    break
                
            await self.websocket.send(audio_chunk)
            self.audio_input_queue.task_done()
            
    async def receive_results(self):
        async for result in self.websocket:
            data = json.loads(result)
            asr_response = TencentASRResponse.from_tencent(data)
            
            if asr_response.is_vad_end or asr_response.is_final:
                self.logger.info(f"Got asr result: {asr_response.sentence}")
                await self.text_output_queue.put(asr_response.sentence)
                
            if asr_response.is_final:
                self.logger.info("Final result received, ending ASR session.")
                break