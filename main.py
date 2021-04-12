from discord.ext import commands
import discord
import json
import multiprocessing as mp
from exts.scraper import Scraper
import asyncio
from models.models import Event
import os

config = json.load(open('config.json'))

prefix = config.get('COMMAND_PREFIX')
bot = commands.Bot(command_prefix=prefix)

BOT_TOKEN = config.get("BOT_TOKEN")

queue = mp.Queue()


if os.path.exists('events.db'):
    os.remove('events.db')


def _create_embed(event: Event):
    embed = discord.Embed()
    embed.title = event.title
    embed.add_field(name='Currency', value=event.currency, inline=False)
    embed.add_field(name='Time', value='In 1 hour', inline=False)
    embed.add_field(name='Exact Time', value=event.time, inline=False)
    return embed


async def send_updates(target_channel):
    print('Queue running ...')
    while True:
        while queue.empty():
            await asyncio.sleep(3)
        event = queue.get(block=False)
        print('Got event in queue')
        embed = _create_embed(event)
        await target_channel.send(embed=embed)


@bot.event
async def on_ready():
    channels = bot.guilds[0].channels
    channel_id = config.get("NOTIFICATIONS_CHANNEL_ID")
    target_channel = discord.utils.get(channels, id=channel_id)
    bot.loop.create_task(send_updates(target_channel))
    bot.load_extension('Cogs.commands')
    print('We have logged in as {0.user}'.format(bot))

sc = Scraper(bot)
mp.Process(target=sc.start, args=(queue,)).start()


bot.run(BOT_TOKEN)
