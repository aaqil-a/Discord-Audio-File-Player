from bot import start_bot, bot
from app import App
from config import TOKEN
import asyncio

# TODO Create UI to select music and sfx folders and play audio files from them.
# TODO Image viewer

async def start_app(loop: asyncio.AbstractEventLoop):
    await bot.wait_until_ready()
    app = App(loop)
    loop.create_task(app.updater())

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(start_bot(bot, TOKEN))
    loop.create_task(start_app(loop))
    loop.run_forever()
    loop.close()
