import discord
from discord.ext import commands
from redbot.core import Config, bank
import random
import time
import unicodedata
import asyncio
from .qchecks import QChecks
import logging

class Events:
    
    #ADD MANUAL ID
    
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, 8358350000, force_registration=True)
  
        event_defaults = {
            'Questions': {
                'Categories': {}
                },
            'AQuestions': {
                'Categories': {}
                },
        }
         
  
            
        self.config.register_guild(**event_defaults)
        #self.config.register_guild(**question_defaults)
    # Make it so it stores users reacting before running new code.
    
    @commands.command
    async def qtest(self,ctx):
        pass
    
    @commands.group(autohelp=True)
    async def events(self, ctx):
        """Test doink doink"""
        pass
        
    @events.command()
    async def question(self, ctx, action: str):
        """Some info!"""
        
        instance = await self.get_instance(ctx, settings=True, user=ctx.author)
        
        if action.lower() not in ('create', 'del', 'list','pending', 'appending'):
            return await ctx.send("Must pick create, del, list, appending or pending.")
        
        qm = QuestionManager(ctx, instance)
                
        try:
            await qm.run(action)
        except asyncio.TimeoutError:
            return await ctx.send("Request timed out. Process canceled.")
    
    @commands.command()
    async def startevent(self, ctx):
        # Define what channel.
        eventslist = "List"
        
        question = "Red and white makes what color?"
        answer  = "Pink"
        emojis = ["\u0031\u20E3","\u0032\u20E3","\u0033\u20E3","\u0034\u20E3"]
        
        alternatives = ["Pink","Green","Blue","Yellow"]
        answer_index = alternatives.index("Pink")
        await ctx.send(answer_index)
        correct_react = None
            
        embed_desc = ""
        for i, color in enumerate(alternatives):
            embed_desc = "{}{}. {}\n".format(embed_desc, i+1, color)
            if answer_index == i:
                correct_react = emojis[i]
                
        
        embed = discord.Embed(
            colour=ctx.guild.me.top_role.colour,
            title = question,
            description = embed_desc
            )
            
             
        message = await ctx.send(embed=embed)
        
        for i in emojis:
            await message.add_reaction(i)
            
        def check(reaction, user):
            return (
                reaction.message.id == message.id 
                and user == ctx.message.author
                # and any(e in str(r.emoji) for e in expected)
            )

            
        try:
            (r, u) = await self.bot.wait_for("reaction_add", timeout=12.0, check=check)
        except asyncio.TimeoutError:
            return await self._clear_react(message)
            
        # r_unicode = unicodedata.name(r)
        #client = discord.Client()
        r = r.emoji
        await ctx.send("Let's see...!")
        await ctx.send("{} ANDNDNN {}".format(r, correct_react))
        print("{} ANDNDNN {}".format(r, correct_react))
        
        if r == correct_react:
            await ctx.send("Congrats homie, correctly reacted!")
            
            
            
            
            
    async def get_instance(self, ctx, settings=True, user=None):
    
        if not user:
            user = ctx.author

        """if await self.config.Global():
            if settings:
                return self.config
            else:
                return self.config.user(user)
        else:"""
        if settings:
            return self.config.guild(ctx.guild)
        else:
            return self.config.member(user)
                
                
                
class QuestionManager:

    def __init__(self, ctx, instance):
        self.instance = instance
        self.ctx = ctx
        
        
    async def run(self, action):

        if action.lower() == "create":
            await self.create()
        elif action.lower() == "del":
            await self.delete()
        elif action.lower() == "pending":
            await self.pending()
        elif action.lower() == "appending":
            await self.appending()
        else:
            print("No correct commands")
            
            
    async def appending(self):
        async with self.instance.Questions() as questions:    
            print("Cat prompt")
            await self.ctx.send("Which category?")
            category = await self.ctx.bot.wait_for('message', timeout=25, check=QChecks(self.ctx).same)
            
            dict = questions['Categories'][category.content]['Questions']
            
            print(dict)
            await self.ctx.send("What quest ID?")
            id = await self.ctx.bot.wait_for('message', timeout=25, check=QChecks(self.ctx).same)
            print("QE")
            id = id.content
            
            print(id)
            
            for question, value in dict.items():
                
                if value==id:
                    async with self.instance.AQuestions() as aquestions:   
                        aquestions['Categories'][category]['Questions'][question] = aquestions['Categories'][category]['Questions'][question]
                        print("YOU DID IT CHIEF")
                        return
                else:
                    print("No go bro")
            
    
    async def apend_all(self):
        pass
    
    async def pending(self):
         async with self.instance.Questions() as questions:
         
            
            try:
                (categorynr, categoryarray) = await self.pick('Categories', 'list')
                
                d = categoryarray[categorynr]
              
                
                if not d:
                    return await self.ctx.send("This category is empty!")
              
                
                dict = questions['Categories'][d]['Questions']
                
                nr = 0
                
                for i in dict:
                    nr = nr + 1 
                    await self.ctx.send("{}. {}".format(nr, i))
                
                
                
            except TypeError:
                return

    async def list(self):
         async with self.instance.Questions() as questions:
            
            try:
                (categorynr, categoryarray) = await self.pick('Categories', 'list')
                
                d = categoryarray[categorynr]
                
                if not d:
                    return await self.ctx.send("This category is empty!")
                
                dict = questions['Categories'][d]
                
                nr = 0
                
                for i in dict:
                    nr = nr + 1 
                    await self.ctx.send("{}. {}".format(nr, i))
                
            except TypeError:
                return
            
    async def delete(self):
         async with self.instance.Questions() as questions:
            
            try:
                (categorynr, categoryarray) = await self.pick('Categories', 'del')
                
                categorydel = categoryarray[categorynr]
                
                (questionnr, questionarray) = await self.pick(categorydel, 'del')
                # questions['Categories'][categorydel][
                questiondel = questionarray[questionnr]
            
                del questions['Categories'][categorydel]['Questions'][questiondel]
            
                await self.ctx.send("Question deleted!")
                #await self.id_check('question', categorydel)
                
            except TypeError:
                return
    
    async def pick(self, value, function):
        async with self.instance.Questions() as questions:
        
            nr = 0
            temp_array = []
        
            dbtest = await self.valuetest(value, function)
            if(not dbtest):
               return False
           
            print(" --->" + value + "<----")
            
           
            
            if value == 'Categories':
                await self.ctx.send("Which category number?")
                
                d = questions['Categories']
                
            else:  
                await self.ctx.send("Which question number?")
                
                d = questions['Categories'][value]['Questions']

            for i in d:
                nr = nr + 1
                await self.ctx.send("{}. {}".format(nr, i))
                temp_array.append(i)
                
            
                
            answer = await self.ctx.bot.wait_for('message', timeout=25, check=QChecks(self.ctx).positive)
            answernr = int(answer.content)-1  
            return answernr, temp_array
    
    
    
    async def valuetest(self, value, function):
        async with self.instance.Questions() as questions:
            print(" valuetest --->" + value + "<----")
            try: 
                testint = 0
                if value == 'Categories':
                    d = questions['Categories']
                else:
                    d = questions['Categories'][value]
                for i in d:
                    testint += 1
                
                if testint == 0:
                    raise TypeError
                
                return True
          
            except TypeError:
                    if function == 'del':
                        del questions['Categories'][value]
                        await self.ctx.send("Category deleted!")
                        #await self.id_check('category')
                        return False
                    else:
                        await self.ctx.send("There are no categories?")
                        return False

            except NameError:
                await self.ctx.send("There are no categories!")
                return False
    
    """#why do I have IDs again
    sync def id_check(self, whatremoved, category=None):
        
        if whatremoved is 'categiry':
            categories = self.instance.Questions()['Categories']
            d = categorieas
            counter = 1
            for i in d:
                if i['id'] is not counter:
                    self.instance.Questions()['Categories'][i]['id': counter]
                    
                    
        else:
            questions = self.instance.Questions()['Categories'][category]['Questions']
            d = questions
            counter = 1
            for i in d:
                if i['id'] is not counter:
                    self.instance.Questions()['Categories'][i]['id': counter]"""
                     
       
        
            
                
    async def create(self):
    
        question = await self.set_question()
        
        alternatives = []
        
        for i in range(4):
            alternatives.append(await self.set_alternative(i))
            
        correct_alt_index = await self.set_correct_alt()
        
        id = await self.set_q_id()
        
        data = {'id' : id, 
                'Alternatives': alternatives,
                'Correct_alt_index': correct_alt_index
                }
        
        await self.add(data, question)
        await self.ctx.send("Question added!")
        
    async def add(self, data, question):
    
        async with self.instance.Questions() as questions:
            
            category = 'General'
   
            print(question)
            print(questions)
            print(category)
            
            
            try:
                d = questions['Categories'][category]
                
            except KeyError:
                c_id = 1
                c_d = questions['Categories']
                
                for i in c_d:
                    c_id = c_id + 1
                    
                questions['Categories'][category] = {'id': c_id, 'Questions':{}}
           
            id = 1
            for i in questions['Categories'][category]:
                id = id + 1
           
            data.update({'id': id})
           
            if category not in questions['Categories']:
                questions['Categories'][category]['Questions'] = {question: data}
            
            elif question in questions['Categories'][category]:
                 self.ctx.send("Question already exists!")
                
            else:
                questions['Categories'][category]['Questions'][question] = data
            
            print("END PRINT  ")
            print(questions)
      
            #return await self.instance.set_raw('Questions','Categories', category, new_id, value = data)
            
            
    # def pending_add(self, data):
     #   await self.list()
        
    async def init_check(self, category):
        try:
            await self.instance.get_raw('Questions','Categories', category)
        except AttributeError:
            await self.ctx.send("Key error bro")
            return await self.instance.set_raw('Questions','Categories', category, value = None)  
    
    async def set_q_id(self):
        await self.ctx.send("Plese enter a unique question ID: ")
        id = await self.ctx.bot.wait_for('message', timeout=25, check=QChecks(self.ctx).same)
        return id.content
        
        
    async def set_question(self):

        
        await self.ctx.send("Enter the question:")
        
        question = await self.ctx.bot.wait_for('message', timeout=25, check=QChecks(self.ctx).same)
        
        return question.content
    
    
    async def set_alternative(self, number):
        await self.ctx.send("Set alternative {}:".format(number+1))
        
        alternative = await self.ctx.bot.wait_for('message', timeout=25, check=QChecks(self.ctx).same)
        
        content = alternative.content
        
        if content is None:
            content = 'blank'
        
        return content
        
    async def set_correct_alt(self):
        await self.ctx.send("Which alternative is the correct one? (1-4)")

        correct_alt = await self.ctx.bot.wait_for('message', timeout=25, check=QChecks(self.ctx).alt_nr)
        return int(correct_alt.content) - 1
    
    
    