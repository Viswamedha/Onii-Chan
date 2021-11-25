import logging
import discord
import typing
import asyncio
from discord.ext import commands

from Core import Bot, GuildCog

class Moderation(GuildCog):

    async def cog_check(self, context: commands.Context):
        return context.guild
    
    async def cog_after_invoke(self, context: commands.Context):
        try:
            await context.message.add_reaction('👍')
        except:
            pass

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded")
    
    
    @commands.command(name = 'ban', help = 'Bans all specified users! ', brief = 'Ban Members')
    @commands.bot_has_permissions(ban_members = True)
    @commands.has_permissions(ban_members = True)
    async def _ban(self, context: commands.Context, users: commands.Greedy[discord.Member] = None, days: typing.Optional[int] = 1, *, reason: str = None):
        if users is None:
            # Checking that users were actually specified
            try:
                await context.reply('You need to specify at least one user! ', delete_after = 15)
                # Runs if message still exists! 
            except:
                await context.send('You need to specify at least one user! ', delete_after = 15)
                # Runs if message gets deleted! 
            return 
        
        message = await context.send('Do you really want to **ban** the specified user(s)? ')
        await message.add_reaction('👍')
        # Confirmation in order to avoid accidents! 

        def check(reaction, user):
            return reaction.message == message and str(reaction.emoji) == '👍' and user.id == context.message.author.id
        # Check callable for user reaction

        try:
            await self.bot.wait_for('reaction_add', check = check, timeout = 20)
            # 20 wait time for reaction
        except:
            return await context.send('Oh, was that by accident then? Request cancelled! 😅')
            # False request

        success, fail = [], []
        for user in users:
            try:
                await user.ban(reason = reason, delete_message_days = days)
                # Banning users with reason and days
                success.append(user.nick or user.name)
            except:
                fail.append(user.nick or user.name)
        # Adding attempts onto corresponding lists

        success = "\n".join(success) or "None"
        fail = "\n".join(fail) or "None"

        embed = discord.Embed(title = 'Ban Request', colour = discord.Color.random())
        embed.add_field(name = 'Delete Days', value=f'`{str(days)}`')
        embed.add_field(name = 'Reason', value = f'`{reason}`')
        embed.set_footer(text = f'Requested by {context.message.author.nick or context.message.author.name}')
        # Setting up embed with default data
        
        try:
            full = embed
            full.add_field(name = 'Successful Changes', value = f'```{success}```', inline = False)
            full.add_field(name = 'Failed Changes', value = f'```{fail}```', inline = False)
            await context.reply(embed = full)
            # Sending maximum details in embed
        except:
            await context.send(embed = embed)
            # Sending alternative default embed


    @commands.command(name = 'kick', help = 'Kicks all specified users! ', brief = 'Kick Members')
    @commands.bot_has_permissions(kick_members = True)
    @commands.has_permissions(kick_members = True)
    async def _kick(self, context: commands.Context, users: commands.Greedy[discord.Member] = None,  *, reason: str = None):
        if users is None:
            # Checking that users were actually specified
            try:
                await context.reply('You need to specify at least one user! ', delete_after = 15)
                # Runs if message still exists! 
            except:
                await context.send('You need to specify at least one user! ', delete_after = 15)
                # Runs if message gets deleted! 
            return 
        
        message = await context.send('Do you really want to **ban** the specified user(s)? ')
        await message.add_reaction('👍')
        # Confirmation in order to avoid accidents! 

        def check(reaction, user):
            return reaction.message == message and str(reaction.emoji) == '👍' and user.id == context.message.author.id
        # Check callable for user reaction

        try:
            await self.bot.wait_for('reaction_add', check = check, timeout = 20)
            # 20 wait time for reaction
        except:
            return await context.send('Oh, was that by accident then? Request cancelled! 😅')
            # False request

        success, fail = [], []
        for user in users:
            try:
                await user.kick(reason = reason)
                # Kicking users with reason specified
                success.append(user.nick or user.name)
            except:
                fail.append(user.nick or user.name)
        # Adding attempts onto corresponding lists
        
        success = "\n".join(success) or "None"
        fail = "\n".join(fail) or "None"

        embed = discord.Embed(title = 'Kick Request', colour = discord.Color.random())
        embed.add_field(name = 'Reason', value = f'`{reason}`')
        embed.set_footer(text = f'Requested by {context.message.author.nick or context.message.author.name}')
        # Setting up embed with default data    
        
        try:
            full = embed
            full.add_field(name = 'Successful Changes', value = f'```{success}```', inline = False)
            full.add_field(name = 'Failed Changes', value = f'```{fail}```', inline = False)
            await context.reply(embed = full)
            # Sending maximum details in embed
        except:
            await context.send(embed = embed)
            # Sending alternative default embed

    @commands.command(name = 'bans', aliases = ['banlist'], help = 'Shows all banned users of the server! ')
    @commands.bot_has_permissions(ban_members = True)
    @commands.has_permissions(ban_members = True)
    async def _bans(self, context: commands.Context, *args):
        members = await context.guild.bans()
        users = '\n'.join([str(num+1) + ') ' + (user.user.name + '#' + user.user.discriminator).ljust(20) + str(user.reason).rjust(5) for num, user in enumerate(members) if not user.user.bot])
        # Fetching relevant data and processing into format
        
        embed = discord.Embed(title = 'Banned Users Request', colour = discord.Color.random())
        embed.add_field(name = context.guild.name, value = f'```{users or "No banned users! "}```' )
        embed.set_footer(text = f'Requested by {context.message.author.nick or context.message.author.name}')
        # Setting up embed

        try:
            await context.reply(embed = embed)
        except:
            await context.send(embed = embed)
        # Sending response as a reply or direct

    @commands.command(name = 'unban', aliases = ['revokeban'], help = 'Unbans a specified user from banlist! ', brief = 'Ban Members')
    @commands.bot_has_permissions(ban_members = True)
    @commands.has_permissions(ban_members = True)
    async def _unban(self, context: commands.Context, userint: typing.Optional[int] = 0, *, reason: str = None):
        members = await context.guild.bans()
        count = len(members)
        # Getting total bans and count
        
        if count == 0:
            return await context.send('No banned users! ')
        
        if userint < 1 or userint > count:
            return await context.send(f'User integer needs to be in range up to `{str(count)}`! ')
        
        userint -= 1
        user = await self.bot.fetch_user(members[userint].user.id)
        await context.guild.unban(user, reason=reason)

        try:
            await context.reply(f'Requested user `{user.name}` has been unbanned! ')
        except:
            await context.send(f'Requested user `{user.name}` has been unbanned! ')

    @commands.command(name = 'leaveserver', aliases = ['bye', 'byebye'], help = 'Makes me leave the server! ', brief = 'Administrator')
    @commands.has_permissions(administrator = True)
    async def _leaveserver(self, context: commands.Context):
        try:
            message = await context.reply('Do you really want me to go? ')
        except:
            message = await context.send('Do you really want me to go? ')
        
        await message.add_reaction('👍')
        
        def check(reaction, user):
            return reaction.message == message and str(reaction.emoji) == '👍' and user.id == context.message.author.id
        
        try:
            await self.bot.wait_for('reaction_add', check = check, timeout = 20)
        except:
            return await context.send('Oh, was that by accident then? Request cancelled! 😅')

        try:
            await context.reply('Bye Bye! ')
        except:
            await context.send('Bye Bye! ')

        await context.guild.leave()

    @commands.command(name = 'purge', aliases = ['clear', 'prune'], help = 'Deletes specified number of messages by specified users! If no users are specified, it deletes any message. Default value is 100!', brief = 'Manage Messages')
    @commands.bot_has_permissions(manage_messages = True)
    @commands.has_permissions(manage_messages = True)
    async def _purge(self, context: commands.Context, messages: typing.Optional[int] = 100, params: commands.Greedy[typing.Union[discord.Member, discord.Role]] = None, exclude_pins: typing.Optional[bool] = False, reverse: typing.Optional[bool] = False, *args):
        if params:
            users = []
            for param in params:    
                if isinstance(param, discord.Member):
                    users.append(param)
                else:
                    for member in param.members:
                        users.append(member) if member not in users else ''
                
            def check(message):
                return message.author in users and not (exclude_pins and message.pinned)
        else:
            def check(message):
                return True
        
        request = await context.channel.purge(limit = messages, check = check, oldest_first = reverse)
        count = len(request)

        embed = discord.Embed(title = 'Message Delete Request', description = f'Deleted `{str(count)}` messages! ')
        embed.set_footer(text = f'Requested by {context.message.author.nick or context.message.author.name}')

        try:
            await context.reply(embed = embed)
        except:
            await context.send(embed = embed)
        
    @commands.command(name = 'clearpins', help = 'Removes all pinned messages from pins! Can specify a limit to clear up to and a boolean on whether to start from reverse.', brief = 'Manage Messages')
    @commands.bot_has_permissions(manage_messages = True)
    @commands.has_permissions(manage_messages = True)
    async def _clearpins(self, context: commands.Context, limit: typing.Optional[int] = 0, reverse: typing.Optional[bool] = False, *args):
        pins = list(enumerate(await context.channel.pins()))
        
        if reverse: 
            pins = pins[::-1]
        
        for count, pin in pins:
            await pin.unpin()
            if limit - 1 == count:
                break

    @commands.command(name = 'nickname', aliases = ['nick', 'rename', 'nname'], help = 'Changes nicknames of all specified users and roles. If no nickname is specified, it resets the nickname! Affects request user by default! ', brief = 'Mange Nicknames')
    @commands.bot_has_permissions(manage_nicknames = True)
    @commands.has_permissions(manage_nicknames = True)
    async def _nickname(self, context: commands.Context, params: commands.Greedy[typing.Union[discord.Member, discord.Role]] = None, *, name: str = None):
        if name and len(name) > 32:
            return await context.send('Nickname is too long. Must be within `32` characters! ')

        action = 'Change' if name else 'Reset'
        
        if params:
            users = []
            for param in params:    
                if isinstance(param, discord.Member):
                    users.append(param)
                else:
                    for member in param.members:
                        users.append(member) if member not in users else ''
        else:
            users = [context.message.author]
        
        success, fail = [], []
        for user in users:
            try:
                await user.edit(nick = name)
                success.append(user.name)
            except:
                fail.append(user.name)
        
        success = "\n".join(success) or "None"
        fail = "\n".join(fail) or "None"

        embed = discord.Embed(title = f'Nickname {action} Request', colour = discord.Color.random())
        embed.set_footer(text = f'Requested by {context.message.author.nick or context.message.author.name}')
        
        try:
            full = embed
            full.add_field(name = 'Successful Changes', value = f'```{success}```', inline = False)
            full.add_field(name = 'Failed Changes', value = f'```{fail}```', inline = False)
            await context.reply(embed = full)
        except:
            await context.send(embed = embed)

    @commands.group(name = 'role', help = 'Provides role management commands! ', brief = 'Manage Roles', invoke_without_command = True)
    async def _role(self, context: commands.Context):
        await context.send(f'Missing subcommands! Possible subcommands `{", ".join([command.name for command in context.command.walk_commands()])}`')
    
    @_role.command(name = 'give', aliases = ['add'], help = 'Gives all specified roles to all specified users! ', brief = 'Manage Roles')
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def _role_give(self, context: commands.Context, params: commands.Greedy[typing.Union[discord.Member, discord.Role]] = None, *, reason = None):
        users, roles = [], []
        for param in params:
            if isinstance(param, discord.Member):
                users.append(param)
            else:
                roles.append(param)
        
        if not users or not roles:
            return await context.send('You need to specify at least one user and role! ')

        success, fail = [], []
        for user in users:
            try:
                await user.add_roles(*roles, atomic = True, reason = reason)
                success.append(str(user.nick or user.name)+" - "+', '.join([str(role.name) for role in roles]))
            except:
                fail.append(str(user.nick or user.name)+" - "+', '.join([str(role.name) for role in roles]))

        success = '\n'.join(success) or 'None'
        fail = '\n'.join(fail) or 'None'

        embed = discord.Embed(title = 'Role Add Request', colour = discord.Color.random())
        embed.add_field(name = 'Reason', value = reason)
        embed.add_field(name = 'Successful Changes', value = f'```{success}```', inline = False)
        embed.add_field(name = 'Failed Changes', value = f'```{fail}```', inline = False)
        embed.set_footer(text = f'Requested by {context.message.author.nick or context.message.author.name}')
        
        try:
            await context.reply(embed = embed)
        except:
            await context.send(embed = embed)
        
    @_role.command(name = 'take', aliases = ['remove'], help = 'Removes all specified roles from all specified users! ', brief = 'Manage Roles')
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def _role_take(self, context: commands.Context, params: commands.Greedy[typing.Union[discord.Member, discord.Role]] = None, *, reason = None):
        users, roles = [], []
        for param in params:
            if isinstance(param, discord.Member):
                users.append(param)
            else:
                roles.append(param)
        
        if not users or not roles:
            return await context.send('You need to specify at least one user and role! ')

        success, fail = [], []
        for user in users:
            try:
                await user.remove_roles(*roles, atomic = True, reason = reason)
                success.append(str(user.nick or user.name)+" - "+', '.join([str(role.name) for role in roles]))
            except:
                fail.append(str(user.nick or user.name)+" - "+', '.join([str(role.name) for role in roles]))

        success = '\n'.join(success) or 'None'
        fail = '\n'.join(fail) or 'None'

        embed = discord.Embed(title = 'Role Remove Request', colour = discord.Color.random())
        embed.add_field(name = 'Reason', value = reason)
        embed.add_field(name = 'Successful Changes', value = f'```{success}```', inline = False)
        embed.add_field(name = 'Failed Changes', value = f'```{fail}```', inline = False)
        embed.set_footer(text = f'Requested by {context.message.author.nick or context.message.author.name}')
        
        try:
            await context.reply(embed = embed)
        except:
            await context.send(embed = embed)

    @_role.command(name = 'list', help = 'Lists all roles of specified user, defaulting to request user! ')
    async def _role_list(self, context: commands.Context, user: discord.Member = None, *args):
        user = user or context.message.author
        rolelist = [role.name for role in user.roles]
        
        embed = discord.Embed(title = 'Roles', colour = discord.Color.random())
        embed.set_author(name = user.nick or user.name, icon_url = user.avatar_url)
        embed.set_footer(text = f'Requested by {context.message.author.nick or context.message.author.name}! ')
        
        try:
            roles = '\n'.join(rolelist)
            embed.description = f'```{roles}```'
            await context.reply(embed = embed)
        except:
            string = ''
            
            for role in rolelist:
                if len(string) < 800:
                    string += role + '\n'
                else:
                    embed.description = f'```{string}```'
                    await context.send(embed = embed)
                    string = ''   
            
            embed.description = f'```{string}```'
            await context.send(embed = embed)  
    
    @_role.command(name = 'serverlist', aliases = ['server'], help = 'Lists all roles of server! ')
    async def _role_serverlist(self, context: commands.Context, *args):
        
        rolelist = [role.name for role in context.guild.roles]
        
        embed = discord.Embed(title = 'Roles', colour = discord.Color.random())
        embed.set_footer(text = f'Requested by {context.message.author.nick or context.message.author.name}! ')
        
        try:
            roles = '\n'.join(rolelist)
            embed.description = f'```{roles}```'
            await context.reply(embed = embed)
        except:
            string = ''
            
            for role in rolelist:
                if len(string) < 800:
                    string += role + '\n'
                else:
                    embed.description = f'```{string}```'
                    await context.send(embed = embed)
                    string = ''   
            
            embed.description = f'```{string}```'
            await context.send(embed = embed)  
    
    @commands.command(name = 'blacklist', help = 'Prevents a user from using my commandset! Using it on an existing user removes them from the list! Shows all blacklisted users if no user if specified! ')
    @commands.has_permissions(administrator = True)
    async def _blacklist(self, context: commands.Context, user: discord.Member = None, *args):
        if user and user.bot:
            return await context.send('You cannot blacklist bots! ')

        server = await self.bot.blacklist.get(str(context.guild.id))

        if not server:
            server = []

        if not user:
            server = [str(await self.bot.fetch_user(user)) for user in server] if server else ['None']
        
            server = '\n'.join(server)

            embed = discord.Embed(
                title = 'Blacklisted Users',
                description = f'```{server}```',
                colour = discord.Color.random()
            )
            
            return await context.send(embed = embed)

        if user.id not in server:
            server.append(user.id)
        else:
            server.remove(user.id)

        await self.bot.blacklist.edit(str(context.guild.id), server)

    @commands.command(name = 'voiceclear', aliases = ['vclear'], help = 'Kicks every user out of a voice channel of request user! ')
    @commands.has_guild_permissions(move_members = True)
    @commands.bot_has_guild_permissions(move_members = True)
    async def _voiceclear(self, context: commands.Context):
        if context.message.author.voice:

            for member in context.message.author.voice.channel.members:
                await member.move_to(None)

        else:
            await context.send('You are not in a voice channel!')

def setup(bot: Bot):
    bot.add_cog(
        Moderation(
            bot,
            logging.getLogger('bot')
        )
    )
