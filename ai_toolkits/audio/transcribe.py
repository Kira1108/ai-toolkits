import logging
from .microphone import MicrophoneClient
from .tencent_asr import TencentASR
from .text_processor import PrintOutTextHandler
import asyncio
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)
async def real_time_transcribe():
    """
    Real-time transcription workflow using microphone input and Tencent ASR.
    Usage:
    ```python
    from ai_toolkits.audio.transcribe import real_time_transcribe   
    import asyncio
    asyncio.run(real_time_transcribe())
    ```
    """
    audio_input_queue = asyncio.Queue()
    text_output_queue = asyncio.Queue()
    microphone_client = MicrophoneClient(audio_input_queue=audio_input_queue)
    asr_client = TencentASR(audio_input_queue=audio_input_queue, text_output_queue=text_output_queue)
    text_handler = PrintOutTextHandler(text_queue=text_output_queue)
    tasks = []
    
    try:
        await asr_client.connect()
        
        # Create tasks
        record_task = asyncio.create_task(microphone_client.receive_audio())
        send_task = asyncio.create_task(asr_client.send_audio())
        receive_task = asyncio.create_task(asr_client.receive_results())
        consume_task = asyncio.create_task(text_handler.process_text())
        
        tasks = [record_task, send_task, receive_task, consume_task]
        logger.info("Starting the workflow...")

        # Wait until the first task completes (either exception or completion)
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

        # Check if any task completed with an exception
        first_exc = None
        for task in done:
            exc = task.exception()
            if exc is not None:
                first_exc = exc
                logger.error(f"Task {task.get_name()} raised an exception: {exc}")
                break

        # If no exception, this means a task completed successfully (likely receive_task got final result)
        if first_exc is None:
            logger.info("A task completed successfully, initiating graceful shutdown...")
            
            # Step 1: Stop recording first
            if not record_task.done():
                record_task.cancel()
                logger.info("Stopped recording")
            
            # Step 2: Send end signal and wait for final result
            logger.info("Sending end signal to ASR service...")
            await asr_client.send_end_signal()
            
            # Step 3: Wait for send and receive tasks to complete
            if not send_task.done():
                await send_task
            if not receive_task.done():
                await receive_task
            logger.info("ASR tasks completed")
            
            # Step 4: Wait for queues to be empty
            logger.info("Waiting for queues to be processed...")
            await audio_input_queue.join()
            await text_output_queue.join()
            logger.info("All queues processed")

            # Step 5: Cancel consume task
            consume_task.cancel()
            try:
                await consume_task
            except asyncio.CancelledError:
                pass
            logger.info("Text consumer stopped")
            
        else:
            # If there was an exception, cancel all pending tasks
            logger.error("Exception occurred, cancelling remaining tasks...")
            for task in pending:
                task.cancel()
            
            # Wait for all tasks to finish
            if pending:
                await asyncio.gather(*pending, return_exceptions=True)
            
            raise first_exc

        logger.info("Workflow completed successfully.")
        
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received, initiating graceful shutdown...")

        # Step 1: Stop recording
        if not record_task.done():
            record_task.cancel()
        
        # Step 2: Send end signal and wait for final result
        try:
            await asr_client.send_end_signal()
        except Exception as e:
            logger.warning(f"Error sending end signal: {e}")
        
        # Step 3: Cancel remaining tasks
        for task in tasks:
            if not task.done():
                task.cancel()
        
    except Exception as e:
        logger.error(f"Unexpected error in workflow: {e}")
        # Cancel all tasks on unexpected error
        for task in tasks:
            if not task.done():
                task.cancel()
        raise
        
    finally:
        # Ensure all tasks are finished
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Step 4: Disconnect from ASR service
        try:
            await asr_client.disconnect()
            logger.info("Disconnected from ASR service")
        except Exception as e:
            logger.warning(f"Error during disconnect: {e}")

        logger.info("Cleanup completed.")
        
@dataclass  
class RealTimeTask:
    audio_input_provider: str = "default"
    audio_input_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    text_output_queue: asyncio.Queue = field(default_factory=asyncio.Queue)
    