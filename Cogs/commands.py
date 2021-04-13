from discord.ext import commands
from discord import Embed
import json
import asyncio
from exts.db import DB
from datetime import datetime as dt
import pytz


class BotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DB()
        self.tz_name = 'America/New_York'
        self.tz = pytz.timezone(self.tz_name)

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
            year = int(event[2].split('/')[0])
            month = int(event[2].split('/')[1])
            day = int(event[2].split('/')[2])
            hour = int(event[3].split(':')[0])
            minute = int(event[3].split(':')[1])
            event_time = dt(year, month, day, hour, minute, tzinfo=self.tz)
            left = event_time - dt.now(tz=self.tz)
            left = str(left).split('.')[0]
            embed.add_field(name='Title', value=event[1])
            embed.add_field(name='Currency', value=event[4])
            embed.add_field(name='Time', value=f'{event[2]} {event[3]}')
            embed.add_field(name='Time Left', value=left, inline=False)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(BotCommands(bot))
    print('Commands extension loaded!')
