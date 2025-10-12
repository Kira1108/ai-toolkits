from ai_toolkits.audio.transcribe import real_time_transcribe   
import asyncio
import nest_asyncio
nest_asyncio.apply()    
asyncio.run(real_time_transcribe())