import discord
from typing import Callable
import functools

music_bot = discord.Client(intents=discord.Intents.default())
sfx_bot = discord.Client(intents=discord.Intents.default())

def play_audio_file(voice_client: discord.VoiceClient, file_path: str, after: Callable):
    try:
        voice_client.stop()
        source = discord.FFmpegPCMAudio(source=file_path)
        voice_client.play(source, after=after)
        return True
    except:
        return False
    
def stop_playing(voice_client: discord.VoiceClient):
    if voice_client.is_playing() or voice_client.is_paused():
        voice_client.stop()

def pause_playing(voice_client: discord.VoiceClient):
    if voice_client.is_playing():
        voice_client.pause()

def resume_playing(voice_client: discord.VoiceClient):
    if voice_client.is_paused():
        voice_client.resume()

async def join_voice(channel_id: int):
    channels = (music_bot.get_channel(channel_id), sfx_bot.get_channel(channel_id))

    try:
        voice_clients = [await c.connect() for c in channels]
        return voice_clients
    except:
        return None

async def start_bot(bot: discord.Client, token: str):
    await bot.login(token)
    await bot.connect()