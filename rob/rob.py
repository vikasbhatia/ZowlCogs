import discord
from discord.ext import commands
from redbot.core import Config, bank
import random
# from redbot.core.shop.ShopManager import remove

class Rob:

    defaults = {
        "base_rob_def": 0
        }

    def __init__(self):
        self.config = Config.get_conf(self, 8358350000, force_registration=True)
        
        defaults = {
            "base_rob_def": 0
        }
        
        self.config.register_guild(**defaults)



    """
    robs the specified user

    Arguments:
        ctx: context in the form of a d.py member object
        victim: the discord member to rob


    """
    @commands.command()
    async def rob(self, ctx, victim: discord.Member):
        shop = ctx.bot.get_cog('Shop')
        cooldowns = ctx.bot.get_cog('Cooldowns')
        robber = ctx.author
        robber_inventory = await shop.inv_hook(ctx.author)
        robber_bal = await bank.get_balance(ctx.author)
        victim_inventory = await shop.inv_hook(victim)

        # check if the user is robbing themselves
        if ctx.author.id == victim.id:
            return await ctx.send('You are an idiot.')

        # check if the user has a general cooldown
        general_cooldown = await cooldowns.get_current_cooldown(ctx, "Rob", victim.id, ['base'])
        if general_cooldown is not 0:
            return await ctx.send('🕒 Sorry, you have to wait {} before robbing again.'.format(general_cooldown))


        # check the user-to-user cooldown
        utu_cooldown = await cooldowns.get_current_cooldown(ctx, "Rob", victim.id, ['utu', str(victim.id)])
        if utu_cooldown is not 0:
            return await ctx.send('🕒 Sorry, you have to wait {} before robbing this person again.'.format(utu_cooldown))


        try:
            # if the user has a robbery kit
            if (robber_inventory['Robbery Kit']['Qty'] >= 1):

                # make sure the victim has money
                victim_bal = await bank.get_balance(victim)
                if victim_bal <= 0:
                    return await ctx.send('<@!{}>, is broke. You cannot rob people who have no <:Schmeckles:437751039093899264>'.format(victim.id))


                # calculate probability of failing
                #rob_chance = robber_bal / (victim_bal + robber_bal)/1.3
                rob_chance = 0.2            

                # account for the victims rob defense   
                try:
                    rob_def = await self.rob_def_get(ctx,victim)
                    rob_def = rob_def/3
                except KeyError:
                    rob_def = 0

                rob_chance -= rob_def

                await shop.item_remove(ctx, "Robbery Kit")
                await cooldowns.start_cooldown(ctx, 'Rob', victim.id)

                if random.random() > rob_chance:
                    await bank.deposit_credits(victim, 10)
                    await ctx.send('👮🏼 Your robbery attempt failed! <@!{}> has recieved 10 <:Schmeckles:437751039093899264>'.format(victim.id))
                else:
                    steal = int(victim_bal * 0.30)

                    await bank.withdraw_credits(victim, steal)
                    await bank.deposit_credits(robber, steal)
                    await ctx.send('You stole {} <:Schmeckles:437751039093899264> from <@!{}> !'.format(steal, victim.id))

        except KeyError:
            await ctx.send('You need a Robbery Kit. You can purchase it with `=shop`')


    # helper functions for getting safe defense

    async def rob_def_get(self, ctx, user: discord.Member=None):
        self.gconf = self.config.guild(ctx.guild)
    
        if user is None:
            user = ctx.author
            
        await self.rob_def_check(ctx,user)
          #  WORK
        cooldowns = ctx.bot.get_cog('Cooldowns')
        safe_cooldown = await cooldowns.get_current_cooldown(ctx, "Safe", ctx.author.id)
        print("Cooldown atm")
        print(safe_cooldown)
        
        if safe_cooldown != 0:
            rob_def = await self.gconf.get_raw(user,"rob_def")
            return rob_def, safe_cooldown
        
        else:
            base_rob_def = await self.gconf.get_raw('base_rob_def')
            await self.rob_def_set(ctx, user, base_rob_def)
            return base_rob_def, safe_cooldown
        
        
            
    async def rob_def_check(self, ctx, user):
        self.gconf = self.config.guild(ctx.guild)
        
        try:
            await self.gconf.get_raw(user, 'rob_def')
        
        except KeyError:
            rob_def = await self.gconf.get_raw('base_rob_def')
            await self.gconf.set_raw(user, "rob_def", value = rob_def)
            
            
    async def rob_def_increase(self, ctx, number):
        
        current_rob_def, safe_cooldown = await self.rob_def_get(ctx)
        user = ctx.author.id
        new_rob_def = current_rob_def + number
        current_points = new_rob_def*10
        increased_points  = number*10
        
        
        if current_rob_def != 0:
            await ctx.send('🕒 Sorry, you have to wait {} seconds before redeeming a safe again.'.format(safe_cooldown))
            return False
        else:
            await self.rob_def_set(ctx, user, new_rob_def)
            await ctx.send('Rob Defence was increased by +{} and is now {}!'.format(increased_points, int(current_points)))
            cooldowns = ctx.bot.get_cog('Cooldowns')
            await cooldowns.start_cooldown(ctx,'Safe')
            return True
            

    async def rob_def_set(self, ctx, user, number):
        cooldowns = ctx.bot.get_cog('Cooldowns')
        self.gconf = self.config.guild(ctx.guild)
        await self.gconf.set_raw(user, "rob_def", value = number)
        await cooldowns.start_cooldown(ctx, 'Safe')
