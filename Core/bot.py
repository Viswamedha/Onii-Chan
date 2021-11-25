'''

Imports

'''

import datetime
import discord 
import logging 
import os
import sys

from discord.ext import commands 

from .core import Embed, Logger, DataStore
from .help import Help


import settings


'''

Logger Setup

'''


logger = Logger(__name__, os.path.basename(__file__))()


'''

Prefix Callable

'''


def get_prefix(bot, message):
    """
    Adding in hardcoded prefix defaults from .env with inbuilt defaults! 
    Also adding in guild specific prefixes! 
    """

    # Adding in bot mention prefixes (in case a user forgets any of the other prefixes)
    prefixes = settings.PREFIXES + [f'<@!{bot.user.id}> ', f'<@{bot.user.id}> ', f'<@!{bot.user.id}>', f'<@{bot.user.id}>']
    
    # Checking if message is from a guild
    if message.guild:
        # Synchronous request for data due to being in a function! 
        prefixes += bot._prefixes.get_value(str(message.guild.id)) or list()

    return prefixes


'''

Discord Bot

'''


class Bot(commands.Bot):

    def __init__(self, **options):
        '''
        Initialising bot with state variables and setting attributes
        '''

        # Checking if TOKEN is provided in .env 

        if not settings.TOKEN:
            raise OSError('TOKEN is not set in .env! ')
        

        # Super classing default setup for the following settings: prefixes, case sensitivity, timeout, intents and adding in help command

        super().__init__(
            command_prefix = get_prefix,
            case_insensitive = True, # Makes all commands case insensitive to make it easier for users. 
            heartbeat_timeout = 150.0, # Setting a longer timeout for the longer commands before socket closes.
            intents = discord.Intents.all(),  # Allowing bot to access all data it may need! 
            help_command = Help(), # Custom help commands with desired styling  
            **options
        )

        # Hardcoding relevant runtime constants

        self.token = settings.TOKEN
        self.invite_url = settings.INVITE

        # All JSON Managers below

        self._prefixes = DataStore(f'{settings.DATA_DIR}/prefixes.json')
        self._blacklist = DataStore(f'{settings.DATA_DIR}/blacklist.json', default = {'Admin': []})
        self._currencies = DataStore(f'{settings.DATA_DIR}/currencies.json')
        self._shop = DataStore(f'{settings.DATA_DIR}/shop.json')

        # Adding in bot logger

        self._logger = logger

        # Other data 
        self.start_time = datetime.datetime.now().replace(microsecond=0)

        self._user_cache = dict()
        self._guild_cache = dict()

        
    def run(self, *args, **kwargs):
        '''
        Overriding run method to handle token within class. 
        Also adds all cogs before launch! 
        '''
        # Checking whether COG_DIR was passed in accurately
        if os.path.exists(f'./{settings.COG_DIR}'):
            
            for cog in os.listdir(f'./{settings.COG_DIR}'):
                # Verifying that it is a python file
                if cog.endswith('.py'):
                    # Stripping the ".py" part and loading cog
                    self.load_extension(f'{settings.COG_DIR}.{cog[:-3]}')

        else: 
            self._logger.critical('Cog Dir Path Does Not Exist')
        
        return super().run(self.token, *args, **kwargs)

    def reload_values(self):
        '''
        Resets all values from the various json data files! 
        '''
        self._prefixes.load_from_file()
        self._blacklist.load_from_file()
    

    async def add_prefix(self, id: str, prefix: str, *args, check = False, **kwargs):
        # Retrieving prefixes by id
        prefixes = await self.prefixes.get(id) or []
        # For checking if a prefix already exists
        if check and prefix in prefixes:
            return check
        # Prevents exceeding max prefix limit
        if len(prefixes) >= settings.MAX_PREFIXES:
            return False
        # Adds new prefix
        prefixes.append(prefix)
        # Updates file
        await self.prefixes.edit(id, prefixes)
        return True
    
    async def remove_prefix(self, id: str, prefix: str, *args, all = False, **kwargs):
        # Retrieving prefixes by id
        prefixes = await self.prefixes.get(str(id))
        # For deleting all prefixes
        if all and prefix == '': 
            await self.prefixes.remove(str(id))
        # If prefix isn't present
        elif not prefixes or prefix not in prefixes:
            return False
        else:
            # Removes prefix
            prefixes.remove(prefix)
            # Updates file
            await self.prefixes.edit(id, prefixes)
        return True


    async def on_ready(self):
        '''
        On ready event to indicate a connection has been succesfully made. 
        '''
        print(f'{self.user.name} is online! ')
        self._logger.info(f'{self.user.name} is online! ')


    async def on_command_error(self, context, exception):
        '''
        Catching all errors and logging them directly!         
        '''
        self._logger.exception(exception)
        embed = Embed(title = 'OOPS Something failed! ', description = exception)
        # Setting up embed for potential error
        if isinstance(exception, commands.BotMissingPermissions):
            # If bot has not got required permissions
            return await context.send(embed = embed)
        if isinstance(exception, commands.MissingPermissions):
            # If user has not got required permissions
            return await context.send(embed = embed)
        if isinstance(exception, commands.CommandNotFound):
            # If an invalid command is used
            return
        if isinstance(exception, commands.CommandOnCooldown): 
            embed = discord.Embed(title='ZOOOOOOOOOOOOOOOOOOM!!!', description=f"**{context.command}**: `{exception}`")
            await context.send(embed=embed, delete_after=10)
        if isinstance(exception, commands.CommandInvokeError):
            # Command trigger error
            try:
                embed.description = exception.original
                await context.send(embed = embed)
            except Exception as e:
                print(exception)
                self._logger.exception(exception)
                print('Error')
        # return await super().on_command_error(context, exception)
