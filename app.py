import customtkinter
import asyncio
from bot import join_voice, play_audio_file, stop_playing, pause_playing, resume_playing
import os
import discord
from typing import Callable
import functools

class MusicFrame(customtkinter.CTkFrame):
    def __init__(self, app, master):
        super().__init__(master)
        self.app = app
        self.songs = {}
        self.queue = []
        self.music_frame = customtkinter.CTkScrollableFrame(self, label_text='Music')
        self.queue_frame = customtkinter.CTkScrollableFrame(self, label_text='Queue')
        self.music_frame.grid(row=0, column=0)
        self.queue_frame.grid(row=0, column=1)

    def add_song(self, name, path):
        button = customtkinter.CTkButton(self.music_frame, text=name, 
                                         command=functools.partial(self.add_to_queue, name=name, path=path))
        button.grid(row=len(self.songs), column=0)
        self.songs[name] = button

    def add_to_queue(self, name, path):
        label = customtkinter.CTkLabel(self.queue_frame, text=name, bg_color='gray', width=140)
        label.grid(row=len(self.queue), column=0)

        if len(self.queue) == 0:
            self.app.play_song(path)

        self.queue.append((label, path))
        
    def clear_queue(self):
        while len(self.queue):
            label = self.queue.pop(0)[0]
            label.destroy()

    async def next_song(self):
        if len(self.queue):
            last_song = self.queue.pop(0)
            last_song[0].destroy()
            # Update rows of next songs
            for i, (label, _) in enumerate(self.queue):
                label.grid(row=i, column=0)
        
        if len(self.queue):
            self.app.play_song(self.queue[0][1])
        else:
            self.app.response_label.configure(text='')
            self.app.pause_button.configure(state='disabled')

class App(customtkinter.CTk):
    def __init__(self, loop: asyncio.AbstractEventLoop):
        super().__init__()

        self.loop = loop
        self.music_voice_client = None
        self.sfx_voice_client = None
        self.protocol('WM_DELETE_WINDOW', lambda: loop.create_task(self.close()))
        self.title('Parama Bot')
        self.geometry('800x400')

        self.entry = customtkinter.CTkEntry(self, placeholder_text='Input voice channel ID', width=200)
        self.entry.grid(row=0, column=0)
        
        self.button = customtkinter.CTkButton(self, text='Connect', 
                                              command=self.parse_channel_id)
        self.button.grid(row=0, column=1)

        self.button = customtkinter.CTkButton(self, text='Disconnect', 
                                              command=lambda: loop.create_task(self.disconnect()))
        self.button.grid(row=0, column=2)

        self.connection_label = customtkinter.CTkLabel(self, text='')
        self.connection_label.grid(row=1, column=0, columnspan=4)

        self.controls_frame = customtkinter.CTkFrame(self)
        self.pause_button = customtkinter.CTkButton(self.controls_frame, text='Pause', state='disabled', command=self.pause_song)
        self.pause_button.grid(row=0, column=0)
        self.stop_button = customtkinter.CTkButton(self.controls_frame, text='Clear Queue', command=self.clear_queue)
        self.stop_button.grid(row=0, column=1)
        self.music_frame = MusicFrame(self, self.controls_frame)
        self.music_frame.grid(row=1, column=0, columnspan=3)
        self.music_frame.add_song('Save Me', 'music/session0/saveme.mp3')
        self.music_frame.add_song('Scarlet Police', 'music/session0/ghettopatrol.mp3')
        self.music_frame.add_song('Idk', 'music/session0/audio.mp3')
        self.music_frame.add_song('Rampage', 'sfx/session0/rampage.mp3')

        self.response_label = customtkinter.CTkLabel(self, text='')
        self.response_label.grid(row=3, column=0, columnspan=4)

    def pause_song(self):
        pause_playing(self.music_voice_client)
        self.pause_button.configure(text='Resume', command=self.resume_song)
        
    def resume_song(self):
        resume_playing(self.music_voice_client)
        self.pause_button.configure(text='Pause', command=self.pause_song)

    def play_song(self, path: str):
        self.play_audio(self.music_voice_client, path, 
                        after=functools.partial(after_callback, app=self, loop=self.loop))
        self.pause_button.configure(text='Pause', state='normal', command=self.pause_song)

    def clear_queue(self):
        stop_playing(self.music_voice_client)
        self.music_frame.clear_queue()
        self.pause_button.configure(text='Pause', state='disabled', command=self.pause_song)
        self.response_label.configure(text='')

    def play_audio(self, voice_client: discord.VoiceClient, file_path: str, after: Callable=None):
        if os.path.isfile(file_path):
            if voice_client:
                if play_audio_file(voice_client, file_path=file_path, after=after):
                    self.response_label.configure(text=f'Now playing: {file_path}') 
                    return
            self.response_label.configure(text=f'Error playing audio: {file_path}')
        else:
            self.response_label.configure(text=f'Error retrieving file: {file_path}')

    def parse_channel_id(self):
        channel_id = self.entry.get()
        try:
            channel_id = int(channel_id)
            self.loop.create_task(self.connect_to_channel(channel_id))
        except:
            self.connection_label.configure(text=f'Error parsing channel ID: {channel_id}')

    async def connect_to_channel(self, channel_id: int):
        if self.music_voice_client or self.sfx_voice_client:
            await self.disconnect()

        voice_clients = await join_voice(channel_id)
        if voice_clients:
            self.music_voice_client = voice_clients[0]
            self.sfx_voice_client = voice_clients[1]
            self.connection_label.configure(text=f'Connected to server {voice_clients[0].guild.name} in channel {voice_clients[0].channel.name}')
            self.controls_frame.grid(row=2, column=0, columnspan=4)
        else:
            self.connection_label.configure(text=f'Error connecting to channel ID: {channel_id}')

    async def disconnect(self):
        self.clear_queue()
        if self.music_voice_client:
            await self.music_voice_client.disconnect()
        if self.sfx_voice_client:
            await self.sfx_voice_client.disconnect()
        self.controls_frame.grid_forget()
        self.connection_label.configure(text='')

    # Custom TKinter updater for compatibility with discord.py
    async def updater(self):
        while True:
            self.update()
            await asyncio.sleep(1/128)
    
    async def close(self):
        if self.music_voice_client:
            await self.music_voice_client.disconnect()
        if self.sfx_voice_client:
            await self.sfx_voice_client.disconnect()
        self.loop.stop()

# Callback for continuing to next song, used to allow calling from
# a separate thread from the main GUI thread.
def after_callback(_, app: App, loop: asyncio.AbstractEventLoop):
    loop.create_task(app.music_frame.next_song())
