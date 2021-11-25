import discord, os
from discord.ext import commands
import logging  
from Core import Bot, HiddenCog
import settings 


class Owner(HiddenCog, command_attrs = dict(hidden = True)):

    async def cog_check(self, context: commands.Context):
        return await self.bot.is_owner(context.message.author)

    def reload_or_load_extension(self, module):
        try:
            self.bot.reload_extension(f'{settings.COG_DIR}.{module}')
        except commands.ExtensionNotLoaded:
            self.bot.load_extension(f'{settings.COG_DIR}.{module}')

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded")

    @commands.command(name = 'shutdown', aliases = ['sd'])
    async def _shutdown(self, context: commands.Context):
        if self.logger is not None:
            self.logger.info('Bot shut down from command! ')
        await context.send(':wave:')
        await self.bot.close()

    @commands.command(name = 'dcall')
    async def _dcall(self, context: commands.Context):
        if context.message.author.voice:
            vc = context.message.author.voice.channel
            for member in vc.members:
                await member.move_to(None)

    @commands.command(name = 'load')
    async def _load(self, context: commands.Context, *, module: str):
        try:
            async with context.typing():
                self.reload_or_load_extension(module)
        except commands.ExtensionError as e:
            await context.send(f'{e.__class__.__name__}: {e}')
        else:
            await context.send('\N{OK HAND SIGN}')

    @commands.command(name = 'unload')
    async def _unload(self, context: commands.Context, *, module: str):
        try:
            async with context.typing():
                self.bot.unload_extension(module)
        except commands.ExtensionError as e:
            await context.send(f'{e.__class__.__name__}: {e}')
        else:
            await context.send('\N{OK HAND SIGN}')
    
    @commands.group(name = 'reload', invoke_without_command = True)
    async def _reload(self, context: commands.Context, *, module: str):
        try:
            async with context.typing():
                self.reload_or_load_extension(module)
        except commands.ExtensionError as e:
            await context.send(f'{e.__class__.__name__}: {e}')
        else:
            await context.send('\N{OK HAND SIGN}')

    @_reload.command(name = 'all')
    async def _reload_all(self, context: commands.Context):
        try:
            async with context.typing():
                for cog in os.listdir('./' + settings.COG_DIR):
                    if cog.endswith('.py'):
                        self.reload_or_load_extension(f'{cog[:-3]}')
        except commands.ExtensionError as e:
            await context.send(f'{e.__class__.__name__}: {e}')
        else:
            await context.send('\N{OK HAND SIGN}')
    
    @commands.command(name = 'datareload')
    async def _datareload(self, context: commands.Context, *args):
        self.bot.reload_values()
        await context.send(':thumbsup:')
    
def setup(bot: Bot):
    bot.add_cog(
        Owner(
            bot,
            logging.getLogger('bot')
        )
    )
