import os
import random
from discord.ext import commands 
import discord 

from Core import GuildCog
from Core.bot import Bot
from Core.constants import *
from Core.core import DataStore, Embed, Logger
from settings import DATA_DIR

logger = Logger(__name__, os.path.basename(__file__))()


class Economy(GuildCog):



    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild:
            return 

        if message.author.bot:
            return 

        if message.author.id not in self.bot._user_cache:

            self.bot._user_cache[message.author.id] = DataStore(
                f'{DATA_DIR}/Users/{message.author.id}.json',
                default = USER_TEMPLATE.copy()
            )
        
        if message.guild.id not in self.bot._guild_cache:
            
            self.bot._guild_cache[message.guild.id] = DataStore(
                f'{DATA_DIR}/Guilds/{message.guild.id}.json',
                default = GUILD_TEMPLATE.copy()
            )
            
    @commands.command(name = 'profile', help = 'Shows user profile! ')
    async def _profile(self, context: commands.Context, member: discord.Member = None):

        user = member or context.author
        user_data: DataStore = self.bot._user_cache.get(user.id , None)
        guild_data: DataStore = self.bot._guild_cache.get(context.guild.id, None)
        
        if user_data is None:
            return 

        user_settings = await user_data.get('Settings')
        
        guild_warnings: dict = await guild_data.get('Warnings')
        guild_caps: dict = await guild_data.get('Caps')
        user_warnings = guild_warnings.get(str(context.author.id), '0')
        warning_limit = guild_caps.get('Warnings', '0')

        storage = await user_data.get('Storage')
        cash = str(storage['Cash']) + ' ' + storage['Current']
        bank = '\n'.join([
            currency + ' : ' + str(value)
            for currency, value in storage['Bank'].items()
        ])

        if not user_settings['public'] and ((member is None) or (member.id == context.author.id)):
            return await context.send('User account not public! ')
        
        embed = Embed(
            title = f'Profile for `{context.author.name}`'
        )

        embed.add_field(
            name = 'ID',
            value = f'`{context.author.id}`' 
        )
        embed.add_field(
            name = 'Warnings',
            value = f'`{user_warnings}/{warning_limit}`'
        )
        embed.add_field(
            name = 'Cash',
            value = f'`{cash}`'
        )
        if bank:
            embed.add_field(
                name = 'Bank',
                value = f'```{bank}```'
            )
        embed.set_thumbnail(url = user.avatar_url)
        embed.set_footer(text = f'Requested by {(user.nick or user.name) if user.id != context.author.id else "you"}! ')
       
        await context.send(embed = embed)
    
    @commands.command(name = 'beg', help = 'Allows a user to beg for money! ')
    async def _beg(self, context: commands.Context):
        
        user_data: DataStore = self.bot._user_cache.get(context.author.id , None)

        if user_data is None:
            return 
        storage = await user_data.get('Storage')

        cash = random.randint(200, 2000)
        storage['Cash'] += cash 

        await user_data.edit('Storage', storage)        
        await context.send(f'You received `{cash}`!')

    @commands.command(name = 'bet', help = 'Allows a user to bet some money! ')
    async def _bet(self, context: commands.Context, cash: int = 50):
        
        user_data: DataStore = self.bot._user_cache.get(context.author.id , None)

        if user_data is None:
            return 
        storage = await user_data.get('Storage')

        if cash < 50:
            return await context.send('Not enough cash specified! ')

        if cash > storage['Cash']:
            return await context.send('You specified more cash than you have! ')


        embed = Embed(
            title = f'Bet for {context.author.nick or context.author.name}'
        )
        embed.add_field(name = 'Rolling...', value = 'Rolling...')

        message: discord.Message = await context.send(embed = embed)

        b, u = random.randint(1,12), random.randint(1,12)
        while b == u:
            b, u = random.randint(1,12), random.randint(1,12)   
        if b > u:
            result = f'I rolled higher and you owe me {cash} Cash. Tough luck! '
            storage['Cash'] -= cash
        else:
            result = f'You rolled higher and you get {cash} Cash. Nicely played! '
            storage['Cash'] += cash

        embed = Embed(
            title = f'Bet for {context.author.nick or context.author.name}'
        )
        embed.add_field(name = context.message.author.nick or context.message.author.name, value = f'`{str(u)}`')
        embed.add_field(name = 'Onii-Chan', value = f'`{str(b)}`')
        embed.add_field(name = 'Result', value = f'`{result}`', inline = False)
        await message.edit(embed = embed)

        await user_data.edit('Storage', storage)        

    @commands.command(name = 'changecurrency', help = 'Allows a user to change the currency of their cash! ')
    async def _changecurrency(self, context: commands.Context):

        user_data: DataStore = self.bot._user_cache.get(context.author.id , None)

        if user_data is None:
            return 
        
        storage = await user_data.get('Storage')

        currencies = self.bot._currencies.get_keys()
        
        currencies.remove(storage['Current'])
        current = storage['Current']
        cmapping = {
            CHOICE_EMOJIS[count]: c
            for count, c in enumerate(currencies)
        }
        
        description = '\n'.join(
            [
                a + ' : ' + b for a,b in cmapping.items()
            ]
        )

        embed = Embed(
            title =  f'Select a currency to change to from `{current}`', 
            description = description
        )
        
        message: discord.Message = await context.send(embed = embed)
        for reaction in cmapping.keys():
            await message.add_reaction(reaction)
        
        def check(reaction, user):
            return str(reaction.emoji) in cmapping.keys() and user.id == context.author.id and reaction.message.id == message.id
        
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout = 30.0, check = check)
        except:
            await context.send('You did not pick an option! ', delete_after = True)
            await message.delete()
            return None 
        
        await message.delete()

        choice = cmapping[str(reaction.emoji)]

        
        storage['Cash'] = round(float(storage['Cash']) * float(self.bot._currencies.data[current][choice]))
        storage['Current'] = choice

        await user_data.edit('Storage', storage)   
        await context.send(f'Changed to {choice}')

    @commands.command(name = 'deposit', help = 'Allows you to deposit money to your bank in your cash currency! ')
    async def _deposit(self, context: commands.Context, cash: int = 50):

        user_data: DataStore = self.bot._user_cache.get(context.author.id , None)

        if user_data is None:
            return 
        storage = await user_data.get('Storage')

        if cash < 50:
            return await context.send('Not enough cash specified! ')

        if cash > storage['Cash']:
            return await context.send('You specified more cash than you have! ')

        if storage['Current'] not in storage['Bank']:
            storage['Bank'][storage['Current']] = 0
        storage['Bank'][storage['Current']] += cash 
        storage['Cash'] -= cash 

        await context.send(f'Transferred `{cash}` {storage["Current"]} into bank! ')
        await user_data.edit('Storage', storage)  

    @commands.command(name = 'withdraw', help = 'Allows you to withdraw money from your bank to your cash! You will need to change currency to access other currencies! ')
    async def _withdraw(self, context: commands.Context, cash: int = 50):

        user_data: DataStore = self.bot._user_cache.get(context.author.id , None)

        if user_data is None:
            return 
        storage = await user_data.get('Storage')

        if cash < 50:
            return await context.send('Not enough cash specified! ')

        if cash > storage['Bank'][storage['Current']]:
            return await context.send('You specified more cash than you have! ')

        storage['Bank'][storage['Current']] -= cash 
        storage['Cash'] += cash 
        
        if storage['Bank'][storage['Current']] == 0:
            storage['Bank'].remove(storage['Current'])
        
        await context.send(f'Transferred `{cash}` {storage["Current"]} from bank! ')
        await user_data.edit('Storage', storage)  

    @commands.command(name = 'shop', help = 'Allows a user to view the shop inventory! ')
    async def _shop(self, context: commands.Context, page: int = 1):

        pages = (len(self.bot._shop.data) // 10) + 1
        
        if page < 1 or page > pages:
            return await context.send('Page doesnt exist! ')
        page -= 1
        after = self.bot._shop.get_keys()[page*10:]

        if len(after) > 10:
            after = after[:10]
        
        after = {
            key: self.bot._shop.data[key]
            for key in after
        }

        c = []
        for item, data in after.items():
            
            total = data["Stock"] + data["Bought"]
            price = data["Base Price"] * ((data["Stock"] / total))

            c.append(
                f'**{item}**\nID: `{data["ID"]}` Stock: `{data["Stock"]}` Price: `{price}` {data["Currency"]}'
            )
        
        description = '\n'.join(c)

        embed = Embed(
            title = 'Shop Inventory',
            description = description
        )

        await context.send(embed = embed)

    @commands.command(name = 'buy', help = 'Allows a user to buy items from the shop! ')
    async def _buy(self, context: commands.Context, item_id: int, quantity: int = 1):

        user_data: DataStore = self.bot._user_cache.get(context.author.id , None)

        if user_data is None:
            return

        storage = await user_data.get('Storage')
        
        hits = [ (i, self.bot._shop.data[i]) for i in self.bot._shop.data if self.bot._shop.data[i]['ID'] == item_id]
        
        if len(hits) < 1:
            return await context.send('Item not found!')
        
        item, data = hits[0]

        total = data["Stock"] + data["Bought"]
        price = data["Base Price"] * ((data["Stock"] / total))

        total_price = quantity * price

        if storage['Current'] != data['Currency']:
            return await context.send('You are in the wrong currency for this purchase! ')
            
        if storage['Cash'] < total_price:
            return await context.send('You do not have enough cash on hand to pay for the item(s) requested! ')
        
        storage['Cash'] -= total_price
        
        if item not in storage['Inventory']:
            storage['Inventory'][item] = 0
        
        storage['Inventory'][item] += quantity
        data['Stock'] -= 1
        data['Bought'] += 1
        print(item)
        print(data)
        await self.bot._currencies.edit(item, data)


        await context.send(f'You have successfully bought {quantity} {item}(s)! ')

        await user_data.edit('Storage', storage)  

    @commands.command()
    @commands.is_owner()
    async def clearusers(self, context: commands.Context):

        for file in os.listdir(f'{DATA_DIR}/Users'):
            
            if str(file).endswith('.json'):
                os.remove(f'{DATA_DIR}/Users/'+file)
        
        for file in os.listdir(f'{DATA_DIR}/Guilds'):
            
            if str(file).endswith('.json'):
                os.remove(f'{DATA_DIR}/Guilds/'+file)
        
        self.bot._user_cache = dict()
        self.bot._guild_cache = dict()
     







def setup(bot: Bot):
    bot.add_cog(
        Economy(
            bot, 
            logger
        )
    )