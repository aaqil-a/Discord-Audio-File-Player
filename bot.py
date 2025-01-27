import discord
import subprocess

from discord.opus import Encoder as OpusEncoder
from typing import Callable

bot = discord.Client(intents=discord.Intents.default())

class OverlayingFFmpegPCMAudio(discord.FFmpegPCMAudio):
    def __init__(self, path):
        super().__init__(source=path)
        self._second_stdout = None
        self.overlaying = False

    def overlay(self, path):
        # From discord.FFmpegPCMAudio
        args = ['ffmpeg', '-i', path, '-f', 's16le', '-ar', '48000', '-ac', '2', '-loglevel', 'warning', 'pipe:1']
        kwargs = {'stdout': subprocess.PIPE, 'stdin': subprocess.DEVNULL, 'stderr': None}
        process = self._spawn_process(args, **kwargs)
        self._second_stdout = process.stdout
        self.overlaying = True
    
    def skip(self):
        if self.overlaying:
            self.overlaying = False
            self._second_stdout = None
            return True
        return False
            
    def read(self):
        if self.overlaying:
            ret = self._second_stdout.read(OpusEncoder.FRAME_SIZE)
            if len(ret) != OpusEncoder.FRAME_SIZE:
                self.overlaying = False
                self._second_stdout = None
                ret = self._stdout.read(OpusEncoder.FRAME_SIZE) 
        else:
            ret = self._stdout.read(OpusEncoder.FRAME_SIZE) 

        if len(ret) != OpusEncoder.FRAME_SIZE:
            return b''
        return ret

def play_audio_file(voice_client: discord.VoiceClient, file_path: str, after: Callable):
    if voice_client.is_playing():
        source = voice_client._player.source
        if isinstance(source, OverlayingFFmpegPCMAudio):
            source.overlay(file_path)
            return
    source = OverlayingFFmpegPCMAudio(file_path)
    voice_client.play(source, after=after)

def stop_playing(voice_client: discord.VoiceClient):
    if voice_client.is_playing() or voice_client.is_paused():
        voice_client.stop()

def pause_playing(voice_client: discord.VoiceClient):
    if voice_client.is_playing():
        voice_client.pause()

def resume_playing(voice_client: discord.VoiceClient):
    if voice_client.is_paused():
        voice_client.resume()

def skip(voice_client: discord.VoiceClient):
    if voice_client.is_playing():
        source = voice_client._player.source
        if isinstance(source, OverlayingFFmpegPCMAudio):
            if source.overlaying:
                source.overlaying = False
                source._second_stdout = None  
                return
        voice_client._player.stop()

async def join_voice(channel_id: int):
    channel = bot.get_channel(channel_id)

    try:
        return await channel.connect()
    except:
        return None

async def start_bot(bot: discord.Client, token: str):
    await bot.login(token)
    await bot.connect()