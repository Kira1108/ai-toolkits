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

    tasks = {record_task, send_task, receive_task, consume_task}
    # Wait until the first exception occurs (or all tasks complete)
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

    # If any completed task raised, cancel the rest and re-raise the exception
    first_exc = None
    for t in done:
        exc = t.exception()
        if exc is not None:
            first_exc = exc
            logging.exception("A task raised an exception, cancelling remaining tasks.")
            break

    # Cancel pending tasks
    for p in pending:
        p.cancel()

    # Ensure all pending tasks are awaited to suppress warnings; collect results/exceptions
    await asyncio.gather(*pending, return_exceptions=True)

    # If there was an exception, re-raise it so callers can handle it
    if first_exc:
        raise first_exc

    await asyncio.sleep(0.1)
    print("Workflow completed.")