import discord


async def checkForTriggers(msg, ctx):
    'ALL TRIGGER WORDS'
    if 'simba' in msg.content.lower():
        await ctx.send(file=discord.File('../assets/singed.png'))

