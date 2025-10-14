from .base import BaseTextHandler
from ai_toolkits.llms.openai_provider import create_async_client
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
import subprocess
import string
import concurrent.futures

def speak_mac(text):
    subprocess.call(['say', text, "-r", "200", "-v", "Tingting"])

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
        self.console = Console()
        
    async def do_process(self, text: str) -> str:
        # Beautiful user message in a panel
        user_panel = Panel(
            text, 
            title="😊 User", 
            title_align="left",
            border_style="green",
            padding=(0, 1)
        )
        self.console.print(user_panel)
        
        self.conversation_history.append({"role": "user", "content": text})
        response = await self.client.chat.completions.create(
            model="gpt-4.1",
            messages=self.conversation_history,
        )
        reply = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": reply})
        
        # Beautiful assistant message in a panel
        assistant_panel = Panel(
            reply, 
            title="🤖 Assistant", 
            title_align="left",
            border_style="blue",
            padding=(0, 1)
        )
        self.console.print(assistant_panel)
        
        self.turns += 1
        return reply
    
    
class ConversationStreamHandler(BaseTextHandler):
    
    def __init__(self, 
                 text_queue:asyncio.Queue = None, 
                 system_prompt: str = "You are a helpful assistant, You provide concise and colloquial style answers.",
                 async_client = None,
                 extra_body:dict = None
                ):
        super().__init__(text_queue)
        
        if async_client is None:
            self.client = create_async_client()
        else:
            self.client = async_client
            
        self.text_queue = text_queue
        self.conversation_history = [{"role": "system", "content": system_prompt}]
        self.turns = 0
        self.extra_body = extra_body
        self.console = Console()
        self.do_cancel = asyncio.Event()
        
    async def cancel(self):
        await self.do_cancel.set()
        
    async def do_process(self, text: str) -> bool:
        # Beautiful user message in a panel
        user_panel = Panel(
            text, 
            title="😊 User", 
            title_align="left",
            border_style="green",
            padding=(0, 1)
        )
        self.console.print(user_panel)

        self.conversation_history.append({"role": "user", "content": text})
        try:
            # Try streaming if supported by the client
            stream = await self.client.chat.completions.create(
                model="gpt-4.1",
                messages=self.conversation_history,
                stream=True,
                extra_body=self.extra_body
            )

            buffer = ""
            panel_title = "🤖 Assistant (streaming)"
            with Live(Panel("", 
                            title=panel_title, 
                            title_align="left", 
                            border_style="blue", 
                            padding=(0, 1)), 
                      console=self.console, 
                      refresh_per_second=10, 
                      transient=True) as live:
                
                async for chunk in stream:
                    if self.do_cancel.is_set():
                        break
                    
                    # Extract content with early returns to avoid nested ifs
                    if not (hasattr(chunk, "choices") and len(chunk.choices) > 0):
                        continue
                    
                    if not hasattr(chunk.choices[0], "delta"):
                        continue
                    
                    content = getattr(chunk.choices[0].delta, "content", "")
                    if not content:
                        continue
                    await asyncio.sleep(0.005)
                    # Update buffer and display
                    buffer += content
                    display_text = Text(buffer, overflow='fold', no_wrap=False)
                    live.update(Panel(display_text, title=panel_title, title_align="left", border_style="blue", padding=(0, 1)))
            
            if self.do_cancel.is_set():
                self.do_cancel.clear()
            
            # After Live context ends, display a permanent final panel
            final_text = Text(buffer, overflow='fold', no_wrap=False)
            final_panel = Panel(
                final_text, 
                title="🤖 Assistant", 
                title_align="left", 
                border_style="blue", 
                padding=(0, 1)
            )
            self.console.print(final_panel)

            self.conversation_history.append({"role": "assistant", "content": buffer})

            return buffer
        except Exception as e:
            raise e
        finally:
            self.turns += 1
            
            

class SpeakOutStreamHandler(BaseTextHandler):
    
    def __init__(self, 
                 text_queue:asyncio.Queue = None, 
                 system_prompt: str = "You are a helpful assistant, You provide concise and colloquial style answers.",
                 async_client = None,
                 extra_body:dict = None
                ):
        super().__init__(text_queue)
        
        if async_client is None:
            self.client = create_async_client()
        else:
            self.client = async_client
            
        self.text_queue = text_queue
        self.conversation_history = [{"role": "system", "content": system_prompt}]
        self.turns = 0
        self.extra_body = extra_body
        
    async def do_process(self, text: str) -> bool:
        print(f"Answering user query {text}...")
        self.conversation_history.append({"role": "user", "content": text})
        try:
            # Try streaming if supported by the client
            stream = await self.client.chat.completions.create(
                model="gpt-4.1",
                messages=self.conversation_history,
                stream=True,
                extra_body=self.extra_body
            )

            complete_reply = ""
            buffer = ""
            async for chunk in stream:
                # Extract content with early returns to avoid nested ifs
                if not (hasattr(chunk, "choices") and len(chunk.choices) > 0):
                    continue
                
                if not hasattr(chunk.choices[0], "delta"):
                    continue
                
                content = getattr(chunk.choices[0].delta, "content", "")
                if not content:
                    continue
                
                # Update buffer and complete reply
                buffer += content
                complete_reply += content
                
                # if content is a punctuation, speak out the buffer
                puncts = {',', '!', '?', '.', '。', '…', '...'}
                if content and (content in puncts) and len(buffer.strip()) > 5:
                    to_speak = buffer.strip()
                    if to_speak:
                        # Use asyncio.to_thread for non-blocking TTS
                        await asyncio.to_thread(speak_mac, to_speak)
                    buffer = ""
            # Speak any remaining buffer content at the end
            if buffer.strip():
                await asyncio.to_thread(speak_mac, buffer.strip())
                
            # Fix: Add complete_reply to conversation history, not buffer
            self.conversation_history.append({"role": "assistant", "content": complete_reply})

            return complete_reply
        except Exception as e:
            raise e
        finally:
            self.turns += 1