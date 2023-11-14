import discord
import subprocess

from discord.opus import Encoder as OpusEncoder
from typing import Callable
from utils import add_audio_bytes

bot = discord.Client(intents=discord.Intents.default())

class OverlayingFFmpegPCMAudio(discord.FFmpegPCMAudio):
    def __init__(self, path):
        super().__init__(source=path)
        self._second_stdout = None

    def overlay(self, path):
        # From discord.FFmpegPCMAudio
        args = ['ffmpeg', '-i', path, '-f', 's16le', '-ar', '48000', '-ac', '2', '-loglevel', 'warning', 'pipe:1']
        kwargs = {'stdout': subprocess.PIPE, 'stdin': subprocess.DEVNULL, 'stderr': None}
        process = self._spawn_process(args, **kwargs)
        self._second_stdout = process.stdout

    def read(self):
        ret = self._stdout.read(OpusEncoder.FRAME_SIZE)

        if self._second_stdout:
            ret_second = self._second_stdout.read(OpusEncoder.FRAME_SIZE)
            if len(ret_second) != OpusEncoder.FRAME_SIZE:
                self._second_stdout = None
            elif len(ret) != OpusEncoder.FRAME_SIZE:
                self._stdout = self._second_stdout
                self._second_stdout = None
                ret = ret_second
            else:
                # Overlay audio
                ret = add_audio_bytes(ret, ret_second, OpusEncoder.SAMPLE_SIZE)

        if len(ret) != OpusEncoder.FRAME_SIZE:
            return b''
        return ret

def play_audio_file(voice_client: discord.VoiceClient, file_path: str, after: Callable):
    if voice_client.is_playing():
        source = voice_client._player.source
        if isinstance(source, OverlayingFFmpegPCMAudio):
            source.overlay(file_path)
            return True
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

async def join_voice(channel_id: int):
    channel = bot.get_channel(channel_id)

    try:
        return await channel.connect()
    except:
        return None

async def start_bot(bot: discord.Client, token: str):
    await bot.login(token)
    await bot.connect()