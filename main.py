from bot import start_bot, music_bot, sfx_bot
from app import App
from config import MUSIC_TOKEN, SFX_TOKEN
import asyncio

# TODO NEXT: Create UI to select music and sfx folders and play audio files from them.

async def start_app(loop: asyncio.AbstractEventLoop):
    await music_bot.wait_until_ready()
    await sfx_bot.wait_until_ready()
    app = App(loop)
    loop.create_task(app.updater())

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot(music_bot, MUSIC_TOKEN))
    loop.create_task(start_bot(sfx_bot, SFX_TOKEN))
    loop.create_task(start_app(loop))
    loop.run_forever()
    loop.close()
