'''

Imports

'''

import logging 
import os 
import sys
import uuid

from discord.ext import commands

from .bot import Bot


'''

Accessing root

'''

sys.path.append(os.path.abspath(os.path.join('..', '')))

import settings


'''

Abstract Guild Cog

'''


class GuildCog(commands.Cog):

    def __init__(self, bot: Bot, logger: logging.Logger = None):
        '''

        Setting up reference attribute to bot client object... 
        
        '''
        self.bot = bot 
        self.logger = logger

        # Logging must be set for cogs
        if logger is None:
            raise Exception('Logger Not Set')
            

    async def cog_check(self, context):
        '''

        Initial check for every command in this cog...

        '''
        return context.guild # Checking that the command was triggered in a Discord Guild rather than by DMs

        # Only allows commands in this cog to be run if a True is returned! 

    '''
    
    Cog Events 
    
    '''


    @commands.Cog.listener()
    async def on_ready(self):
        '''
        
        Ran as soon as bot is ready to receive messages

        '''
        self.logger.info(f"{self.__class__.__name__} cog has been loaded")
        print(f"{self.__class__.__name__} cog has been loaded")

        # Logged to show when the cog is loaded! 


'''

Abstract Hidden Cog

'''


class HiddenCog(commands.Cog, command_attrs = dict(hidden = True)):

    '''

    The command attrs set makes every command present in this cog hidden in the help command! 

    '''


    def __init__(self, bot: Bot, logger: logging.Logger = None):
        '''

        Setting up reference attribute to bot client object... 
        
        '''
        self.bot = bot 
        self.logger = logger

        # Logging must be set for cogs
        if logger is None:
            raise Exception('Logger Not Set')
            
            
    '''
    
    Cog Events 
    
    '''

    @commands.Cog.listener()
    async def on_ready(self):
        '''
        
        Ran as soon as bot is ready to receive messages

        '''
        self.logger.info(f"{self.__class__.__name__} cog has been loaded")

        # Logged to show when the cog is loaded!


