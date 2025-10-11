import logging
logging.basicConfig(level=logging.INFO)
from .microphone import MicrophoneClient
from .tencent_asr import TencentASR
import asyncio

async def consume_text_queue(queue:asyncio.Queue):
    while True:
        item = await queue.get()
        print(item)
        queue.task_done()
        await asyncio.sleep(0.01)

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
    await asr_client.connect()
    record_task = asyncio.create_task(microphone_client.record())
    send_task = asyncio.create_task(asr_client.send_audio())
    receive_task = asyncio.create_task(asr_client.receive_results())
    consume_task = asyncio.create_task(consume_text_queue(text_output_queue))
    logging.info("Starting the workflow...")
    await asyncio.gather(record_task, send_task, receive_task, consume_task)
    await asyncio.sleep(0.1)
    print("Workflow completed.")