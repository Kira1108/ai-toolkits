import click
from ai_toolkits.audio.audio_apps import create_streaming_conversation_bot

@click.group()
def cli():
    """A simple CLI tool."""
    pass

@cli.command()
@click.option('--duration', default=300, help='Duration in seconds for the streaming bot.')
def start(duration):
    """Starts the streaming conversation bot."""
    bot = create_streaming_conversation_bot(duration_seconds=duration)
    bot.run_app()
