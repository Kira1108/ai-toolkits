import logging
from .microphone import MicrophoneClient
from .tencent_asr import TencentASR
from .text_processor import PrintOutTextHandler
from .base import AudioStreamReader, BaseSTT, BaseTextHandler
import asyncio
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)
        
@dataclass  
class RealTimeTask:
    audio_input_provider: AudioStreamReader = field(default_factory=MicrophoneClient)
    text_handler: BaseTextHandler = field(default_factory=PrintOutTextHandler)
    stt_service: BaseSTT = field(default_factory=TencentASR)
    audio_input_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    text_output_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    trace_conversation: bool = True
    
    def __post_init__(self):
        self.audio_input_provider.bind_audio_queue(self.audio_input_queue)
        self.stt_service.bind_audio_queue(self.audio_input_queue)
        self.stt_service.bind_text_queue(self.text_output_queue)
        self.text_handler.bind_text_queue(self.text_output_queue)
    
    async def run(self):
        await self.stt_service.connect()
        tasks = []
        try:
            print("Preparing to start...")
            record_task = asyncio.create_task(self.audio_input_provider.receive_audio())
            send_task = asyncio.create_task(self.stt_service.send_audio())
            receive_task = asyncio.create_task(self.stt_service.receive_results())
            consume_task = asyncio.create_task(self.text_handler.process_text())
            tasks = [record_task, send_task, receive_task, consume_task]
            print("Start speaking now...")
            
            done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            first_exc = None
            for task in done:
                exc = task.exception()
                if exc is not None:
                    first_exc = exc
                    logger.error(f"Task {task.get_name()} raised an exception: {exc}")
                    break

            if first_exc is None:
                logger.info("A task completed successfully, initiating graceful shutdown...")
                if not record_task.done():
                    record_task.cancel()
                    logger.info("Stopped recording")
                logger.info("Sending end signal to STT service...")
                await self.stt_service.send_end_signal()
                if not send_task.done():
                    await send_task
                if not receive_task.done():
                    await receive_task
                logger.info("STT tasks completed")
                logger.info("Waiting for queues to be processed...")
                await self.audio_input_queue.join()
                await self.text_output_queue.join()
                logger.info("All queues processed")
                consume_task.cancel()
                try:
                    await consume_task
                except asyncio.CancelledError:
                    pass
                logger.info("Text consumer stopped")
            else:
                logger.error("Exception occurred, cancelling remaining tasks...")
                for task in pending:
                    task.cancel()
                if pending:
                    await asyncio.gather(*pending, return_exceptions=True)
                raise first_exc

            logger.info("Workflow completed successfully.")
        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt received, initiating graceful shutdown...")
            if not record_task.done():
                record_task.cancel()
            try:
                await self.stt_service.send_end_signal()
            except Exception as e:
                logger.warning(f"Error sending end signal: {e}")
            for task in tasks:
                if not task.done():
                    task.cancel()
        except Exception as e:
            logger.error(f"Unexpected error in workflow: {e}")
            for task in tasks:
                if not task.done():
                    task.cancel()
            raise
        
        finally:
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                
            if hasattr(self.text_handler, "conversation_history") and self.trace_conversation:
                import json
                import uuid
                import os
                os.makedirs("trace", exist_ok=True)
                with open(f"trace/conversation_history-{uuid.uuid4()}.json", "w", encoding="utf-8") as f:
                    json.dump(self.text_handler.conversation_history, f, ensure_ascii=False, indent=4)
            try:
                await self.stt_service.disconnect()
                logger.info("Disconnected from STT service")
            except Exception as e:
                logger.warning(f"Error during disconnect: {e}")
            logger.info("Cleanup completed.")   
    
    def run_app(self):
        asyncio.run(self.run())
    