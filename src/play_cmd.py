import asyncio
import youtube_dl
import discord

youtube_dl.utils.bug_reports_message = lambda: ''

FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
ytdl_format_options = {
    'format': 'bestaudio',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}



ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
        formatedUrl="https://youtu.be/"
        if "=" in url:
            start = url.index("=")
            formatedUrl += url[start+1:start+12]
            url=formatedUrl
        if 'entries' not in data:

            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch:{url}", download=False))
        data = data['entries'][0]
        return {'url':data['formats'][0]['url'],'filename': data['title']}

