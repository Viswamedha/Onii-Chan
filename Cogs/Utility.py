import logging
import discord
from discord.ext import commands 
import time
import datetime
import asyncio
import os 

from Core import GuildCog, Embed, Logger
from Core.bot import Bot
from Core.core import DataStore

logger = Logger(__name__, os.path.basename(__file__))()

class Utility(GuildCog):
        

    @commands.command(name = 'ping', help = 'Provides current latency and ping! ')
    async def _ping(self, context: commands.Context, *args):
        # Initial embed
        embed = Embed(title = '🏓 Current Ping 🏓', description = 'Pinging...')
        before_time = time.time()
        # Sending embed
        message = await context.send(embed = embed)
        # Calculating latency
        latency = round(self.bot.latency * 1000)
        elapsed_ms = round((time.time() - before_time) * 1000) - latency
        embed.description = None
        # Editting embed with result
        embed.add_field(name = 'Ping', value = f'{elapsed_ms}ms')
        embed.add_field(name = 'Latency', value = f'{latency}ms')
        await message.edit(embed = embed, delete_after = 30)

    @commands.command(name = 'uptime', help = 'States how long it has been since I last woke up! ')
    async def _uptime(self, context: commands.Context, *args):
        current_time = datetime.datetime.now().replace(microsecond=0)
        # Calculating difference and setting embed
        embed = Embed(title = '📶 Uptime 📶', description=f"Time since I went online: \n`{current_time - self.bot.start_time}`")
        # Semdomg embed
        await context.send(embed = embed, delete_after = 30)

    @commands.command(name = 'starttime', help = 'States the exact time when I last woke up! ')
    async def _starttime(self, context: commands.Context, *args):
        embed = Embed(title = '🌅 Starttime 🌅', description=f"I have been awake since `{self.bot.start_time}`! ")
        # Sending embed with initial start time data
        await context.send(embed = embed, delete_after = 30)

    @commands.command(name = 'invite', help = 'Provides invite link to invite me to another server! ')
    async def _invite(self, context: commands.Context, *args):
        embed = Embed(title = '✉️ Invite ✉️', description = f'[Invite me]({self.bot.invite_url})')
        # Providing invite url in embed
        await context.send(embed = embed, delete_after = 30)
    
    @commands.command(name = 'info', aliases= ['about'], help = 'Provides my application details! ')
    async def _info(self, context: commands.Context, *args):
        embed = Embed(title = f'{self.bot.user.name}')    
        embed.set_thumbnail(url = self.bot.user.avatar_url)
        # Getting owner 
        info = await self.bot.application_info()
        owner = info.owner
        try:
            # Main stats
            embed.add_field(
                name = 'My Stats',
                value = f'''```Guilds: {len(self.bot.guilds)}\nUsers: {len(self.bot.users)}\nShards: {self.bot.shard_count}\nShard ID: {context.guild.shard_id}```''',
                inline = False
            )
            embed.add_field(name = 'Type', value = f'```Language: Python\nVersion: 3.9\nBase: discord.py```', inline = False)
            embed.add_field(name = 'Invite', value = f'[Invite me]({self.bot.invite_url})', inline = False)
            # Setting author and owner in footer
            embed.set_author(name = 'Requested by ' + (context.message.author.nick or context.message.author.name), url = context.message.author.avatar_url)
            embed.set_footer(text = f'Made by {owner}', icon_url = owner.avatar_url)
        except:
            pass
        # Sending embed
        await context.send(embed = embed, delete_after = 30)

    @commands.command(name = 'warn', help = 'Allows authorised users to warn others due to a reason!')
    async def _warn(self, context: commands.Context, members: commands.Greedy[discord.Member], warnings: int = 1):
        
        guild: DataStore = self.bot._guild_cache.get(context.guild.id, None)
        guild_warnings = await guild.get('Warnings')

        for member in members:
            if str(member.id) not in guild_warnings:
                guild_warnings[str(member.id)]  = 0
        
        for member in members:
            guild_warnings[str(member.id)]  += warnings 
        
        await guild.edit('Warnings', guild_warnings)
    
        await context.send('Successfully warned specified users! ')
    
    @commands.command(name = 'allow', help = 'Allows authorised users to unwarn others!')
    async def _allow(self, context: commands.Context, members: commands.Greedy[discord.Member], warnings: int = 1):
        
        guild: DataStore = self.bot._guild_cache.get(context.guild.id, None)
        guild_warnings = await guild.get('Warnings')
        
        for member in members:
            if str(member.id) in guild_warnings:
                guild_warnings[str(member.id)]  -= warnings 

                if guild_warnings[str(member.id)] < 0:
                    guild_warnings[str(member.id)] = 0
        
        for member in members:
            if str(member.id) not in guild_warnings:
                guild_warnings.pop(str(member.id))
        
        await guild.edit('Warnings', guild_warnings)
    
        await context.send('Successfully allowed specified users! ')

    



def setup(bot: Bot):
    bot.add_cog(
        Utility(
            bot,
            logger 
        )
    )








