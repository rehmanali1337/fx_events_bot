from discord.ext import commands
from discord import Embed
import json
import asyncio
from exts.db import DB
from datetime import datetime as dt


class BotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DB()

    @commands.command(name='today')
    async def today(self, ctx):
        d = dt.now()
        date_today = f'{d.year}/{d.month}/{d.day}'
        events = self.db.get_events_by_date(date_today)
        embed = Embed()
        embed.title = 'Today\'s Events'
        if len(events) == 0:
            embed.description = 'No Restricted Events Today!'
        for event in events:
            embed.add_field(name='Title', value=event[1])
            embed.add_field(name='Currency', value=event[4])
            embed.add_field(name='Time', value=f'{event[2]} {event[3]}')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(BotCommands(bot))
    print('Commands extension loaded!')
