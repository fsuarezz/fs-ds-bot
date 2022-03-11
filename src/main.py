import time

import discord
import asyncio
from asyncio import sleep,run
from discord.ext import commands,tasks
from play_cmd import YTDLSource,FFMPEG_OPTS
from triggerword import checkForTriggers
from dotenv.main import load_dotenv
import os



def main():
    bot = commands.Bot(command_prefix='!', description='Beep Boop')
    queue = []
    load_dotenv()

    'EVENTS'


    @bot.event
    async def on_ready():
        print('R')


    @bot.event
    async def on_message(msg):
        await checkForTriggers(msg, await bot.get_context(msg))
        await bot.process_commands(msg)


    '------'


    async def join(ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client is None:
            if not ctx.message.author.voice:
                await ctx.send("{} no estas conectado a un canal de voz".format(ctx.message.author.name))
                return False
            else:
                channel = ctx.message.author.voice.channel
                await channel.connect()
                return True
        else:
            return True

    async def leave(ctx):
        voice_client = ctx.message.guild.voice_client
        if not (voice_client is None):
            await voice_client.disconnect()

    async def playNext(ctx):
        if len(queue) > 0:
            queue.pop(0)
        if len(queue) > 0:
            server = ctx.message.guild
            voice_channel = server.voice_client
            song = queue[0]
            # Recursive
            if not (voice_channel is None):
                voice_channel.play(discord.FFmpegPCMAudio(
                    song['url'], **FFMPEG_OPTS), after=lambda e: run(playNext(ctx))
                       )

    'COMMANDS USE !'


    @bot.command(name='test', help='Checkea respuesta bot')
    async def test(ctx):
        await ctx.send('Hello World')


    @bot.command(name='play', help='Reproducir musica')
    async def play(ctx, url):
        try:
            connect = await join(ctx)
            if connect:
                server = ctx.message.guild
                voice_channel = server.voice_client
                async with ctx.typing():
                    song = await YTDLSource.from_url(url, loop=bot.loop)
                    queue.append(song)
                    if len(queue) == 1:
                        queue.append(song)
                        await ctx.send('**Reproduciendo:** {}'.format(song['filename']))
                        await playNext(ctx)


                    # Recursive
                    else:
                        await ctx.send("Se agrego a la queue: " + song['filename'])
                while voice_channel.is_playing():
                    await asyncio.sleep(60)
                await leave(ctx)
        except Exception as m:
            await ctx.send(m)


    @bot.command(name='pause', help='Pausar musica')
    async def pause(ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_playing():
            await voice_client.pause()
        else:
            await ctx.send("The bot is not playing anything at the moment.")


    @bot.command(name='resume', help='Resumir musica')
    async def resume(ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_paused():
            await voice_client.resume()
        else:
            await ctx.send("The bot was not playing anything before this. Use play_song command")


    @bot.command(name='stop', help='Desconectar bot')
    async def stop(ctx):
        voice_client = ctx.message.guild.voice_client
        if voice_client.is_connected():
            queue.clear()
            await ctx.send("Bye")
            await leave(ctx)
        else:
            await ctx.send("No estoy conectado a un canal de voz.")


    @bot.command(name='skip', help='Proxima cancion')
    async def skip(ctx):
        if len(queue) > 0:
            voice_client = ctx.message.guild.voice_client
            voice_client.stop()
            await playNext(ctx)

    '--------'

    bot.run(os.getenv("DISCORD_TOKEN"))


if __name__ == '__main__':
    main()


