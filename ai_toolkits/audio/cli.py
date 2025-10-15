import uuid
import json
import click
from ai_toolkits.audio.audio_apps import create_streaming_conversation_bot
from ai_toolkits.audio.audio_apps import create_translator
from ai_toolkits.audio.audio_apps import create_siri_bot
from ai_toolkits.audio.audio_apps import create_note_taking_bot

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
@click.option('--duration', default=120, help='Duration in seconds for the note-taking bot.')
def note(duration:int = 120):
    
    def save_memory(bot):
        memory = bot.text_handler.memory
        fp = f"note_taking_memory_{str(uuid.uuid4())[:5]}.json"
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=4)
        print(f"Shut down service, note saved to {fp}... exit.")

    try:
        bot = create_note_taking_bot(duration_seconds=duration)
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