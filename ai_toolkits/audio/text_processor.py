import logging
from .base import BaseTextHandler
from ai_toolkits.llms.openai_provider import create_async_client
import asyncio

class PrintOutTextHandler(BaseTextHandler):
    def __init__(self, text_queue:asyncio.Queue = None):
        super().__init__(text_queue)

    async def do_process(self, text: str) -> str:
        print(f"Transcription: {text}")
        return text

class TranslateTextHandler(BaseTextHandler):
    
    def __init__(self, text_queue:asyncio.Queue = None):
        super().__init__(text_queue)
        self.client = create_async_client()
        self.text_queue = text_queue
        
    async def do_process(self, text: str) -> str:
        translation = await self.client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": f"Translate the following text to English: {text}, do not add any other explanations."}],
        )
        print(f"Translation: {translation.choices[0].message.content}")
        return translation.choices[0].message.content


class ShortAnswerTextHandler(BaseTextHandler):
    
    def __init__(self, text_queue:asyncio.Queue = None):
        super().__init__(text_queue)
        self.client = create_async_client()
        self.text_queue = text_queue
        
    async def do_process(self, text: str) -> str:
        answer = await self.client.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": f"Provide a concise answer to the following text: {text}, do not add any other explanations."}],
        )
        print(f"Short Answer: {answer.choices[0].message.content}")
        return answer.choices[0].message.content
    
    
class ConversationHandler(BaseTextHandler):
    
    def __init__(self, 
                 text_queue:asyncio.Queue = None, 
                 system_prompt: str = "You are a helpful assistant, You provide concise and colloquial style answers."
                ):
        super().__init__(text_queue)
        self.client = create_async_client()
        self.text_queue = text_queue
        self.conversation_history = [{"role": "system", "content": system_prompt}]
        self.turns = 0
        
    async def do_process(self, text: str) -> str:
        sep = f" Turn {self.turns} "
        print(sep.center(80, "="))
        print(f"😏: {text}")
        self.conversation_history.append({"role": "user", "content": text})
        response = await self.client.chat.completions.create(
            model="gpt-4.1",
            messages=self.conversation_history,
        )
        reply = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": reply})
        
        print(f"🤖: {reply}")
        self.turns += 1
        return reply
    
    
class ConversationStreamHandler(BaseTextHandler):
    
    def __init__(self, 
                 text_queue:asyncio.Queue = None, 
                 system_prompt: str = "You are a helpful assistant, You provide concise and colloquial style answers."
                ):
        super().__init__(text_queue)
        self.client = create_async_client()
        self.text_queue = text_queue
        self.conversation_history = [{"role": "system", "content": system_prompt}]
        self.turns = 0
        
    async def do_process(self, text: str) -> str:
        sep = f" Turn {self.turns} "
        print(sep.center(80, "="))
        print(f"😏: {text}")
        self.conversation_history.append({"role": "user", "content": text})
        try:
            # Try streaming if supported by the client
            stream = await self.client.chat.completions.create(
                model="gpt-4.1",
                messages=self.conversation_history,
                stream=True,
            )
            print("🤖: ", end="", flush=True)
            buffer = ""
            async for chunk in stream:
                if hasattr(chunk, "choices") and len(chunk.choices) > 0:
                    if hasattr(chunk.choices[0], "delta"):
                        content = getattr(chunk.choices[0].delta, "content", "")
                        if content:
                            print(content, end="", flush=True)
                            buffer += content
            print()  # New line after completion
            self.conversation_history.append({"role": "assistant", "content": buffer})
        except Exception as e:
            raise e