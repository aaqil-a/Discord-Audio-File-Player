Self-hosted Discord bot to play audio files locally with a simple GUI written in python.

# Hosting
## Setup
Create a [discord application and bot](https://discord.com/developers/applications?new_application=true), and save the Bot authentication token as the variable `TOKEN` in a `config.py` file, or manually set it in `main.py`. Invite the bot to your server.

Install [FFmpeg](https://www.ffmpeg.org/download.html) and ensure it is added to your `PATH` if not done yet.

Install requirements then run the app using 
```bash
pip install -r requirements.txt
python main.py
```

## Audio Files
Store any FFmpeg supported audio files in the `music/` or `sfx/` directory.