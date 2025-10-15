import uuid
import json
import click
from ai_toolkits.audio.audio_apps import create_streaming_conversation_bot
from ai_toolkits.audio.audio_apps import create_translator
from ai_toolkits.audio.audio_apps import create_siri_bot
from ai_toolkits.audio.audio_apps import create_note_taking_bot
from ai_toolkits.llms.openai_provider import create_sync_client

@click.group()
def cli():
    """A simple CLI tool."""
    pass

@cli.command()
@click.option('--duration', default=300, help='Duration in seconds for the streaming bot.')
def chat(duration):
    """Starts the streaming conversation bot."""
    bot = create_streaming_conversation_bot(duration_seconds=duration)
    bot.run_app()


@cli.command()
def translate():
    """Starts the translator bot."""
    bot = create_translator()
    bot.run_app()
    
    
@cli.command()
@click.option(
    '--duration', 
    default=120, 
    help='Duration in seconds for the note-taking bot.')
def note(duration:int = 120):
    
    def save_memory(bot):
        memory = bot.text_handler.memory
        fp = f"note_taking_memory_{str(uuid.uuid4())[:5]}.json"
        summary = (
            "You are given a conversation memory in json format."
            "You task is to summarize the key points discussed in the conversation."
            "Try to be detailed, do not miss any important points."
            "Try to be fluent and coherent, try your best to make it like a human-written summary."
        )
        
        client = create_sync_client()
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": summary},
                {"role": "user", "content": json.dumps(memory, ensure_ascii=False, indent=4)}
            ],
        )
        
        info = {
            "summary": response.choices[0].message.content,
            "raw_memory": memory
        }
        
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(info, f, ensure_ascii=False, indent=4)
        print(f"Shut down service, note saved to {fp}... exit.")

    try:
        bot = create_note_taking_bot(
            duration_seconds=duration)
        bot.run_app()
        save_memory(bot)
    except Exception as e:
        print(f"Error occurred: {e}")
        save_memory(bot)


@cli.command()
def siri():
    """Starts the Siri bot."""
    bot = create_siri_bot()
    bot.run_app()