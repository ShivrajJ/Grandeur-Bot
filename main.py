import discord
from discord.ext import commands
import sys
import traceback as trace
import os
import asyncio
import json
#import requests
import aiohttp
import math
from tinydb import TinyDB, Query
from tinydb.operations import add, subtract
import typing
from keep_alive import keep_alive
from PIL import Image, ImageDraw, ImageFont
from unidecode import unidecode
import datetime
import calendar
from tabulate import tabulate


intents = discord.Intents.all()
bot = commands.Bot(command_prefix = '$', description = "Just a Bot", intents = intents)

async def UpdateTables():
  tableChannel = discord.utils.get(bot.edenguild.channels, id = 825322069684256780)
  await tableChannel.purge(limit = 3)
  db = TinyDB("JSON Data Files/Characters.json")
  data = []
  characters = db.all()
  for character in characters:
    data.append([character["Name"], character["Rank"], character["XP"], character["Alignment"]])
  data.sort(reverse = True, key = lambda x: int(x[2]))
  allData = [list(i) for i in data]
  for character in allData:
    character.insert(0, allData.index(character)+1)

  await tableChannel.send("**All**\n```" + tabulate(allData, headers=["S.No.", "Name", "Rank", "XP", "Alignment"], showindex="never", tablefmt="fancy_grid") + "```")
  
  imperialData = [list(i) for i in data if i[3] == "Imperial Mage"]
  for character in imperialData:
    character.insert(0, imperialData.index(character)+1)

  await tableChannel.send("**Imperial Mages**\n```" + tabulate(imperialData, headers=["S.No.", "Name", "Rank", "XP", "Alignment"], showindex=False, tablefmt="fancy_grid") + "```")

  darkData = [list(i) for i in data if i[3] == "Dark Mage"]
  for character in darkData:
    character.insert(0, darkData.index(character)+1)

  await tableChannel.send("**Dark Mages**\n```" + tabulate(darkData, headers=["S.No.", "Name", "Rank", "XP", "Alignment"], showindex="never", tablefmt="fancy_grid") + "```")

  # =============================================================

  characters = db.all()
  data = []
  for character in characters:
    data.append([character["Name"], character["Fame Rank"], character["Fame Points"], character["Alignment"]])
  data.sort(reverse = True, key = lambda x: int(x[2]))

  fameChannel = discord.utils.get(bot.edenguild.channels, id = 825322120782807050)
  infamyChannel = discord.utils.get(bot.edenguild.channels, id = 825322263082827816)

  await fameChannel.purge(limit = 1)
  await infamyChannel.purge(limit = 1)

  fameData = [list(i[:3]) for i in data if i[3] == "Imperial Mage"]
  for character in fameData:
    character.insert(0, fameData.index(character)+1)

  infamyData = [list(i[:3]) for i in data if i[3] == "Dark Mage"]
  for character in infamyData:
    character.insert(0, infamyData.index(character)+1)

  await fameChannel.send("**Imperial Mages**\n```" + tabulate(fameData, headers=["S.No.", "Name", "Fame Rank", "Fame Points"], showindex="never", tablefmt="fancy_grid") + "```")
  await infamyChannel.send("**Dark Mages**\n```" + tabulate(infamyData, headers=["S.No.", "Name", "Fame Rank", "Fame Points"], showindex="never", tablefmt="fancy_grid") + "```")

async def UpdateWeather():
  weatherChannel = discord.utils.get(bot.edenguild.channels, id=858011645154558012)
  await weatherChannel.purge(limit=5)
  for country in ["Ironhold", "Alfenheim", "Vanaheim", "Summerwind", "Viridi"]:
    await weather(ctx=weatherChannel, city=country)

@bot.event
async def on_ready():
  print("I'm in!")
  print(bot.user)
  bot.edenguild = discord.utils.get(bot.guilds, name="Edenfell")
  bot.purgeChannel = discord.utils.get(bot.edenguild.channels, id = 825124293230329936)
  hoursSinceUp = 0
  with open("JSON Data Files/WealthStorage.txt", "r") as wealthFile:
    wealthAdded = bool(wealthFile.read())
  today = datetime.datetime.now(datetime.timezone.utc).day
  if today == 1:
    print("DAY TO ADD WEALTH AND SUBTRACT DEBT")
    if not wealthAdded:
      print("NOT ADDED YET")
      db = TinyDB("JSON Data Files/Trade.json")
      table = db.table("Countries")
      query = Query()
      for country in ["Alfenheim", "Vanaheim", "Summerwind", "Viridi"]:
        print(country)
        info = await Trade("see", country = country)
        monthlyProfit = info["Monthly Profit"]
        debt = info["Debt"]
        monthlyInstallment = info["Monthly Installment"]
        print("Monthly Profit:", monthlyProfit)
        print("Debt:", debt)
        print("Monthly Installment:", monthlyInstallment)
        
        print(table.update(add("Wealth", monthlyProfit), query.Country == country))
        print(table.update(subtract("Debt", monthlyInstallment), query.Country == country))
        if debt - monthlyInstallment == 0:
          print(table.update({"Monthly Installment" : 0}, query.Country == country))

      with open("JSON Data Files/WealthStorage.txt", "w") as wealthFile:
        wealthFile.write("True")
  if today == 2:
    with open("JSON Data Files/WealthStorage.txt", "w") as wealthFile:
        wealthFile.write("")

  while True:
    await UpdateWeather()
    await UpdateTables()
    with open("JSON Data Files/Characters.json", "w") as backup:
      url = "https://jsonstorage.net/api/items/be81d9d4-98cb-4aeb-83af-d7620f2af136"
      #url = "https://api.jsonbin.io/v3/b/60882132f6655022c46d52cd/latest"
      #headers = {"X-Master-Key" : "$2b$10$ZQTgjlmx9ABoAWGW.Y06TuFeJvd4YzZomB7T8QRyWWLAG.eEudPNK"}
      async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
          data = await r.json()
      #req = requests.get(url=url, headers = headers)
      #data = json.loads(req.text)
      json.dump(data, backup)
    await asyncio.sleep(6*3600)
    hoursSinceUp += 6

@bot.event
async def on_error(event, ctx):
  tbfile = open("traceback.txt", "w")
  tbfile.write("")
  tbfile = open("traceback.txt", "r+")
  trace.print_exc(file = tbfile)
  tbfile.seek(0)
  output = tbfile.read()
  embed = discord.Embed(title = "Error!", description = "An error has occurred. Please contact the Bot Mechanic(Shivraj#3373) and point them towards this message.", color = 0xff0000)
  embed.add_field(name="Traceback", value="```" + output + "```", inline=False)
  if event == "on_message":
    await ctx.send(discord.utils.get(bot.edenguild.members, id = 124102469646024704).mention)
    await ctx.send(embed=embed)
  else:
    channel = discord.utils.get(bot.edenguild.channels, id = 825114740707688488)
    await channel.send(discord.utils.get(bot.edenguild.members, id = 124102469646024704).mention)
    await channel.send(embed=embed)
    await channel.send(str(ctx))

@bot.event
async def on_message_delete(message):
  if message.author != bot.user:
    print("Delete")
    guild = message.guild
    embed = discord.Embed(title="Log")
    messageLog = "```" + str(message.author) + ":" + message.content + "```"
    if len(messageLog) > 1024:
      n,m = 0, 1018
      while len(messageLog) > 1024:
        content = messageLog[n:m] + "```"
        embed.add_field(name = "\u200b", value = content, inline=False)
        await bot.purgeChannel.send(embed=embed)
        embed.clear_fields()
        messageLog = "```" + messageLog[m:]
      embed.add_field(name = "\u200b", value = messageLog, inline=False)
      await bot.purgeChannel.send(embed=embed)
    else:
      embed.add_field(name="\u200b", value="```" + str(message.author) + ":" + message.content + "```", inline=False)
      await bot.purgeChannel.send(embed=embed)

@bot.event
async def on_member_join(member):
  welcome = "Greetings, " + member.mention + "." + " Welcome to Edenfell. Please start by reading our rules: " + discord.utils.get(bot.edenguild.channels, id = 825123180955041873).mention + ". Once you have familiarized yourself with the rules, get started on your character and come say hello in " + discord.utils.get(bot.edenguild.channels, id=825074522130219030).mention + "!"
  embed = discord.Embed(title = "Welcome!", description = welcome)
  channel = discord.utils.get(bot.edenguild.channels, id = 825124262478086164)
  embed.set_image(url="https://i.imgur.com/r2HARtB.gif")
  await channel.send(member.mention)
  await channel.send(embed = embed)
  
  role1 = discord.utils.get(bot.edenguild.roles, id = 825168051384746016)
  role2 = discord.utils.get(bot.edenguild.roles, id = 825111177759424582)
  role3 = discord.utils.get(bot.edenguild.roles, id = 855522316436242466)
  await member.add_roles(role1, role2, role3, reason = "Passed the Test.")

# @bot.event
# async def on_raw_reaction_add(payload):
#   if payload.message_id == 858040770861596722:
#     member = payload.member
#     reaction = payload.emoji
#     channel = discord.utils.get(bot.edenguild.channels, id = 825123180955041873)
#     message = await channel.fetch_message(858040770861596722)
#     role1 = discord.utils.get(bot.edenguild.roles, id = 825168051384746016)
#     role2 = discord.utils.get(bot.edenguild.roles, id = 825111177759424582)
#     role3 = discord.utils.get(bot.edenguild.roles, id = 855522316436242466)

#     if str(reaction) == "✅":
#       await message.clear_reaction("✅")
#       if role1 not in member.roles:
#         await member.add_roles(role1, role2, role3, reason = "Passed the Test.")

@bot.command()
async def reverse(ctx, *, text):
  '''Reverses text. Usage: $reverse <text>'''
  await ctx.send(text[-1::-1])

''' @bot.command()
async def help(ctx):
  embed = discord.Embed(title="Help", description="All commands are listed here, but for the usage of each, type the command and then type help in front of the command. Eg- $char help.", color=0x00ffff)
  embed.add_field(name="$newchar",value="Adds a new Character to the database. Mod Only Command.",inline=True)
  embed.add_field(name="$char",value="Shows the Character's Card",inline=True)
  embed.add_field(name="$modchar",value="Modifies the Character's data. Mod Only Command.",inline=True)
  embed.add_field(name="$xp",value="Shows all the Characters and their XP in table form.",inline=True)
  embed.add_field(name="$approval",value="Creates an Approval Channel. Mod Only Command.",inline=True)
  embed.add_field(name="$remove",value="Removes an Approval Channel. Mod Only Command.",inline=True)
  embed.add_field(name="$purge",value="Purges/Deletes the number of messages mentioned with the command in the channel where it's used.",inline=True)
  embed.add_field(name="$reverse",value="Reverses whatever message is written after the command.",inline=True)  
  await ctx.send(embed=embed) '''

@bot.command()
async def purge(ctx, *, number : int):
  '''Command to purge messages. Usage: $purge 20'''
  guild = ctx.guild
  channel = bot.purgeChannel 
  if not ctx.author.guild_permissions.manage_messages: 
    await ctx.send("You're not authorized!")
  else:
    if number > 100:
      number = 100
    messageList = await ctx.channel.history(limit=number).flatten()
    for n, i in enumerate(messageList):
      messageList[n] = str(i.author) + ": " + i.content
    messageList.reverse()
    messageLog = "\n".join(messageList)
    embed = discord.Embed(title = "Log")
    def purgecheck(m):
      return m.channel == ctx.channel
    await ctx.channel.purge(limit = number, check=purgecheck)
    if len("\n".join(messageLog)) > 1024:
      n,m = 0, 1018
      while len("```" + messageLog + "```") > 1024:
        content = "```" + messageLog[n:m] + "```"
        embed.add_field(name = "\u200b", value = content, inline=False)
        await channel.send(embed=embed)
        embed.clear_fields()
        messageLog = "```" + messageLog[m:] + "```"
      embed.add_field(name = "\u200b", value = messageLog, inline=False)
      await channel.send(embed=embed)
    else:
      embed.add_field(name = "\u200b", value = "```" + messageLog + "```")
      await channel.send(embed=embed)
    await ctx.send(str(ctx.author) + " deleted " + str(number) + " messages.")

@purge.error
async def purgeError(ctx, error):
  if isinstance(error, commands.BadArgument):
    await ctx.send("That's not a number! Try again.")

@bot.command()
async def approval(ctx, user : discord.Member = None):
  if not ctx.author.guild_permissions.manage_channels:
    await ctx.channel.send("You are not permitted to create a channel! Please contact a Staff Member.")
  else:
    if user == None:
      await message.channel.send("Mention the user who you're creating this channel for next to the command. Usage: ```$approval @abcdef```")
    else:
      staff = 825077295198502923
      guild = bot.edenguild
      category = discord.utils.get(guild.categories, id = 825229308100345927)
      name = str(user)[:-5]
      overwrites = {
        guild.default_role:discord.PermissionOverwrite(read_messages = True, send_messages = False),
        user:discord.PermissionOverwrite(read_messages = True, send_messages = True),
        guild.get_role(staff):discord.PermissionOverwrite(read_messages = True, send_messages = True)
      }
      channel = await guild.create_text_channel(name, overwrites = overwrites, category=category)
      await ctx.send(channel.mention) 

@bot.command()
async def newchar(ctx):
  '''Add a character to the database. Staff Only. Enter 0 for default values.'''
  guild = ctx.guild
  exit = 0
  if not ctx.author.guild_permissions.manage_channels:
    await ctx.send("You are not permitted to create a Character in the Database! Please contact a Staff Member.")
  else:
    MainTemplate = ["UserID", "Name", "Description", "XP", "Fame Points", "Alignment", "Money", "Elixir", "Mana", "Items", "Stats", "Image"]
    Parameters = {}
    for n, i in enumerate(MainTemplate):
      if n != 8:
        await ctx.send("Enter %s:" % i)
      else:
        await ctx.send("Enter Max Mana (Numeric):")
      if n == 10:
        await ctx.send("Physical Power, Physical Speed, Physical Durability, Casting Speed, Perception, Mana Rank")
      def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
      try:
        reply = await bot.wait_for('message', timeout = 120.0, check = check)
        if reply.content == "exit":
          exit = 1
          break
      except asyncio.TimeoutError:
        await ctx.send("Timed out! Try again.")
        exit = 1
        break
      else:
        if n != 8:
          Parameters[MainTemplate[n]] = "{.content}".format(reply)
        else:
          Parameters["Max Mana"] = "{.content}".format(reply)
    if not exit:
      Roles = {"Guardian" : 825373640412889088, "Liberator" : 825373703453540373, "Lightbringer" : 825373756809543680, "Peacekeeper" : 825373803705008158, "Mage" : 825373847678746635, "Sorceror" : 825373911071064115, "Agitator" : 825374042109509654, "Ringleader" : 825374102557687848, "Terror" : 825374139824996362, "Overlord" : 825374199202971648, "Apprentice" :  825374343734362132, "Acolyte" : 825374387858702358, "Disciple" : 825374433081688075, "Magus" : 825374469287575583, "Wizard" : 825374528645496895, "Archwizard" : 825374576280207411, "Grandmaster" : 825374626015608854}

      Ranks = {"Apprentice":0, "Acolyte":500, "Disciple":1200, "Magus":2000, "Wizard":3000, "Archwizard":4500, "Grandmaster":6500}
      for k,v in Ranks.items():
        if int(Parameters["XP"]) >= int(v):
          Parameters["Rank"] = k

      Fame = {"Mage" : 0, "Peacekeeper" : 100, "Lightbringer" : 200, "Liberator" : 300, "Guardian" : 400}
      Infamy = {"Sorceror" : 0, "Agitator" : 100, "Ringleader" : 200, "Terror" : 300, "Overlord" : 400}

      if Parameters["Alignment"] == "Imperial Mage":
        for k,v in Fame.items():
          if int(Parameters["Fame Points"]) >= int(v):
            Parameters["Fame Rank"] = k
      elif Parameters["Alignment"] == "Dark Mage":
        for k,v in Infamy.items():
          if int(Parameters["Fame Points"]) >= int(v):
            Parameters["Fame Rank"] = k

      user = discord.utils.get(bot.edenguild.members, id=int(Parameters["UserID"].strip("<@!>")))
      xpRole = discord.utils.get(bot.edenguild.roles, id = Roles[Parameters["Rank"]])
      fameRole = discord.utils.get(bot.edenguild.roles, id = Roles[Parameters["Fame Rank"]])
      await user.add_roles(xpRole, fameRole, reason = "Character Created.", atomic=True)

      StatTemplate = ["Physical Power", "Physical Speed", "Physical Durability", "Casting Speed", "Perception", "Mana Rank"]
      StatList = Parameters["Stats"].strip("()").replace(" ", "").split(",")
      Parameters["Stats"] = {StatTemplate[i]:StatList[i] for i in range(len(StatList))}
      defaults = ["Undefined", "Undefined", "\u200b", "0", "Undefined", "0", "\u200b", "Stats"]
      Stats = "".join(StatList)

      for i, (k, v) in enumerate(Parameters.items()):
        if v == "0":
          Parameters[k] = defaults[i]
      await ctx.send(str([k + ": " + str(v).strip("{}") for k, v in Parameters.items()]).strip("[]").replace("'", ""))
      await ctx.send("Is this correct? (yes/no)")
      def check1(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ("yes", "no")
      try:
        reply = await bot.wait_for('message', timeout = 120.0, check = check1)
      except asyncio.TimeoutError:
        await ctx.send("Timed out! Try again.")
      if "{.content}".format(reply).lower() == "yes":
        db = TinyDB("JSON Data Files/Characters.json")
        db.insert(Parameters)
        await ctx.send("Character added successfully!")

        url = "https://jsonstorage.net/api/items/be81d9d4-98cb-4aeb-83af-d7620f2af136"
        headers = {'Content-Type': 'application/json'}

        with open("JSON Data Files/Characters.json", "r") as charfile:
          data = json.load(charfile)
        async with aiohttp.ClientSession(headers = headers) as session:
          async with session.put(url, json = data) as r:
            print(r.status)
            responseText = await r.json()
            print(str(responseText))
        #req = requests.put(url, json=data, headers=headers)
        #print(req.status_code)
        #print(req.text)
            if r.status == 201 or r.status == 200:
              await ctx.send("Backed up successfully!")
            else:
              await ctx.send("Wait, that one wasn't backed up correctly!")

      elif "{.content}".format(reply).lower() == "no":
        await ctx.send("Exited Successfully. Run the command again if you still wish to add a character.")
    else:
      await ctx.send("Exited Successfully. Run the command again if you still wish to add a character.")
    

@bot.command()
async def char(ctx, user : typing.Optional[discord.Member], *, name="none"):
  '''Posts the character sheet for a character. Mentions, First Names and Full Names all work. Accents don't matter. Usage: $char <Character-Name>/<User-Mention>'''
  db = TinyDB("JSON Data Files/Characters.json")
  query = Query()
  if name != "none" and user == None:
    print("Name given, not user")
    print(name)
    name = unidecode(name)
    test_func1 = lambda val, name: unidecode(val) == name
    def test_func2(val, name):
      if len(val.split()) > 1:
        return unidecode(val).split()[1] == name
      else:
        return unidecode(val) == name
    if len(name.split()) > 1:
      data = db.search(query.Name.test(test_func1, name))
    else:
      print("First name only")
      data = db.search(query.Name.test(test_func2, name))
  else:
    userID = "<@!" + str(user.id) + ">"
    data = db.search(query.UserID == userID)
  print(data)
  if len(data) == 0:
    await ctx.send("That user doesn't have a character.")
  else:
    try:
      final = Image.new("RGBA", (1200, 840))
      nameBanner = Image.open("Images/Name Banner.png")
      if data[0]["Alignment"] == "Imperial Mage":
        scroll = Image.open("Images/Scroll Template.png")
      elif data[0]["Alignment"] == "Dark Mage":
        scroll = Image.open("Images/Scroll Template Dark.png")
      final.paste(scroll, (int(final.width/2 - scroll.width/2)+10, 0), scroll)

      Title = data[0]["Description"]
      XP, Money, Elixir, Mana, Rank, Fame, PP, PS, PD, P, CS, M = data[0]["XP"], data[0]["Money"], data[0]["Elixir"], data[0]["Max Mana"], data[0]["Rank"], data[0]["Fame Rank"], data[0]["Stats"]["Physical Power"], data[0]["Stats"]["Physical Speed"], data[0]["Stats"]["Physical Durability"], data[0]["Stats"]["Perception"], data[0]["Stats"]["Casting Speed"], data[0]["Stats"]["Mana Rank"]

      url = data[0]["Image"]
      async with aiohttp.ClientSession() as session:
        async with session.get(url) as contents:
          image = open("Images/Temp Image.png", "wb")
          imageData = await contents.content.read()
          image.write(imageData)
          image.close()
      
      im = Image.open("Images/Temp Image.png")
      if im.width < im.height:
        print("Vertical")
        im = im.resize((int(im.width/100) * int(33000/im.height), 330))
      else:
        print("Horizontal")
        im = im.resize((int(im.width/100) * int(33000/im.height), 330))
        im = im.crop(((int(im.width/2) - int(330/2)) , 0, (int(im.width/2) + int(330/2)), 330))
      fnt1 = ImageFont.truetype("Fonts/MedievalSharp-Regular.ttf", 32)
      fnt2 = ImageFont.truetype("Fonts/PERRYGOT.TTF", 35)
      draw1 = ImageDraw.Draw(final)

      draw1.text((305+25, 60+2), Title, font = fnt2, fill = (0,0,0,255))
      draw1.text((378+25, 145+2), XP, font = fnt1, fill = (0,0,0,255))
      draw1.text((430+25, 189+2), Money, font = fnt1, fill = (0,0,0,255))
      draw1.text((403+25, 232+2), Elixir, font = fnt1, fill = (0,0,0,255))
      draw1.text((418+25, 270+2), Mana, font = fnt1, fill = (0,0,0,255))
      draw1.text((407+25, 354+2), Rank, font = fnt1, fill = (0,0,0,255))
      draw1.text((407+25, 397+2), Fame, font = fnt1, fill = (0,0,0,255))
      draw1.text((362+15, 570-10), PP, font = fnt1, fill = (0,0,0,255), anchor = "mt")
      draw1.text((589+15, 570-10), PS, font = fnt1, fill = (0,0,0,255), anchor = "mt")
      draw1.text((815+15, 570-10), PD, font = fnt1, fill = (0,0,0,255), anchor = "mt")
      draw1.text((374+15, 681-10), P, font = fnt1, fill = (0,0,0,255), anchor = "mt")
      # draw1.text((577+15, 691-10), MS, font = fnt1, fill = (0,0,0,255))
      draw1.text((825+15, 681-10), M, font = fnt1, fill = (0,0,0,255), anchor = "mt")
      # draw1.text((462+15, 766-10), P, font = fnt1, fill = (0,0,0,255))
      draw1.text((594+15, 776-10), CS, font = fnt1, fill = (0,0,0,255), anchor = "mt")

      offset = 0
      center = int((838+620)/2)

      while center-int(im.width/2)+10-offset+im.width > 908: #if image overflows, offset more. 908 is the pixel location of the right side of scroll
        offset += 10
      final.paste(im, (center-int(im.width/2)+10-offset, 128+5))
      final.save("Images/Temp Scroll.png")

      txt = Image.new("RGBA", nameBanner.size)

      fntsize = 52
      fnt = ImageFont.truetype(font = "Fonts/Campanile.ttf", size = fntsize)
      while fnt.getlength(data[0]["Name"]) > 354:
        fntsize -= 2
        fnt = ImageFont.truetype(font = "Fonts/Campanile.ttf", size = fntsize)
        print(fntsize)


      draw = ImageDraw.Draw(txt)

      draw.text((int(nameBanner.width/2), 55), data[0]["Name"], font = fnt, fill = (0,0,0,255), anchor = "mm")

      out = Image.alpha_composite(nameBanner, txt)
      out.save("Images/Temp Banner.png")

      Banner = discord.File("Images/Temp Banner.png", filename = data[0]["Name"] + ".png")
      Scroll = discord.File("Images/Temp Scroll.png", filename = "Character Sheet.png")

      print("Reached the end")

      await ctx.send(file=Banner)
      await ctx.send(file=Scroll)
    except KeyError:
      await ctx.send("Something went wrong. Tell Shiv to check it out. (Key Error)")

@char.error
async def charError(ctx, error):
  if isinstance(error, commands.BadArgument):
    await ctx.send("Please mention a valid user!")

@bot.command()
async def charlist(ctx):
  db = TinyDB("JSON Data Files/Characters.json")
  data = db.all()
  message = "```"
  for char in data:
    message += char["Name"] + "\n"
  message += "```"
  await ctx.send(message)

@bot.command()
async def xp(ctx, user : typing.Optional[discord.Member], *, name="none"):
  if not ctx.author.guild_permissions.manage_channels:
    await ctx.send("You're not permitted to edit characters. Contact a Staff Member.")
  else:
    db = TinyDB("JSON Data Files/Characters.json")
    query = Query()
    if name != "none" and user == None:
      print("Name given, not user")
      print(name)
      name = unidecode(name)
      test_func1 = lambda val, name: unidecode(val) == name
      def test_func2(val, name):
        if len(val.split()) > 1:
          return unidecode(val).split()[1] == name
        else:
          return unidecode(val) == name
      if len(name.split()) > 1:
        data = db.search(query.Name.test(test_func1, name))[0]
      else:
        print("First name only")
        data = db.search(query.Name.test(test_func2, name))[0]
    else:
      userID = "<@!" + str(user.id) + ">"
      data = db.search(query.UserID == userID)[0]
    print(data)
    if len(data) == 0:
      await ctx.send("That user doesn't have a character.")
    else:
      xpRoles = {"Apprentice" :  825374343734362132, "Acolyte" : 825374387858702358, "Disciple" : 825374433081688075, "Magus" : 825374469287575583, "Wizard" : 825374528645496895, "Archwizard" : 825374576280207411, "Grandmaster" : 825374626015608854}


      await ctx.send(data["Name"] + " has " + str(data["XP"]) + " XP. How much do you wish to add?")
      exit = 0
      def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
      try:
        reply = await bot.wait_for("message", timeout=60.0, check = check)
        if reply.content.lower() == "exit":
          exit = 1
      except asyncio.TimeoutError:
        await ctx.send("Timed Out! Please run the command again.")
        exit = 1
      if not exit:
        userID = data["UserID"]
        user = discord.utils.get(bot.edenguild.members, id=int(userID.strip("<@!>")))
        XP = int(data["XP"]) + int(reply.content)
        data["XP"] = str(XP)
        Ranks = {"Apprentice":0, "Acolyte":500, "Disciple":1200, "Magus":2000, "Wizard":3000, "Archwizard":4500, "Grandmaster":6500}
        for k,v in Ranks.items():
          if int(XP) >= int(v):
            data["Rank"] = k

        xpRole = discord.utils.get(bot.edenguild.roles, id = xpRoles[data["Rank"]])
        if xpRole not in user.roles:
          for role,roleID in xpRoles.items():
            oldXPRole = discord.utils.get(bot.edenguild.roles, id = roleID)
            if oldXPRole in user.roles:
              await user.remove_roles(oldXPRole, reason = "Updating Character.", atomic=True)
              break
              
          await user.add_roles(xpRole, reason = "Character Updated.", atomic=True)
        db.update(data, query.Name == data["Name"])
        await ctx.send("Updated Successfully.")

        url = "https://jsonstorage.net/api/items/be81d9d4-98cb-4aeb-83af-d7620f2af136"
        headers = {'Content-Type': 'application/json'}

        with open("JSON Data Files/Characters.json", "r") as charfile:
          data = json.load(charfile)
        async with aiohttp.ClientSession(headers = headers) as session:
          print(data)
          async with session.put(url, json = data, headers = headers) as r:
            print(r.status)
            responseText = await r.json()
            print(str(responseText))
            if r.status == 200 or r.status == 201:
              await ctx.send("Backed Up Successfully!")
              await UpdateTables()
            else:
              await ctx.send("Wait, that one wasn't backed up correctly!")
      else:
        await ctx.send("Exited Successfully. Run the command again if you still wish to modify XP.")
        
@bot.command()
async def modchar(ctx):
  '''Modifies a Character Sheet. Staff only.'''
  if not ctx.author.guild_permissions.manage_channels:
    await ctx.send("You're not permitted to edit characters. Contact a Staff Member.")
  else:
    db = TinyDB("JSON Data Files/Characters.json")
    data = db.all()
    query = Query()
    
    exit = 0
    ModData = {}
    ModTemplate = ["Name", "Entry", "New Value"]
    ValidEntry = ["Name", "Description", "XP", "Fame Points", "Alignment", "Money", "Elixir", "Max Mana", "Items", "Physical Power", "Physical Speed", "Physical Durability",  "Casting Speed", "Perception", "Mana Rank", "Image"]
    for n, i in enumerate(ModTemplate):
      await ctx.send("Enter the {abc}".format(abc=i))
      if n == 1:
        await ctx.send("Name, Description, XP, Fame Points, Alignment, Money, Elixir, Max Mana, Items, Image, Stats[Only one from Physical Power, Physical Speed, Physical Durability, Casting Speed, Perception, Mana Rank]")
      def check2(m):
        return m.author == ctx.author and m.channel == ctx.channel
      try:
        reply = await bot.wait_for("message", timeout=50.0, check = check2)
        if reply.content.lower() == "exit":
          exit = 1
          break
        elif n == 0:
          if reply.content not in [i["Name"] for i in data]:
            await ctx.send("Enter a Valid Character. That Character does not exist.")
            exit = 1
            break
        elif n == 1:
          if reply.content not in ValidEntry:
            await ctx.send("Enter a valid Entry. Run the command again.")
            exit = 1
            break
      except asyncio.TimeoutError:
        await ctx.send("Timed Out! Please run the command again.")
        exit = 1
        break
      else:
        ModData[ModTemplate[n]] = "{.content}".format(reply)
    if not exit:
      for i in data:
        if i["Name"] == ModData["Name"]:
          userID = i["UserID"]
          data = i
          break
      user = discord.utils.get(bot.edenguild.members, id=int(userID.strip("<@!>")))
      entry = ModData["Entry"].title()
      if entry == "Xp":
        entry = "XP"
      value = ModData["New Value"]
      if entry in ["Physical Power", "Physical Speed", "Physical Durability", "Casting Speed", "Perception", "Mana Rank"]:
        data["Stats"][entry] = value
      else:
        fameRoles = {"Guardian" : 825373640412889088, "Liberator" : 825373703453540373, "Lightbringer" : 825373756809543680, "Peacekeeper" : 825373803705008158, "Mage" : 825373847678746635, "Sorceror" : 825373911071064115, "Agitator" : 825374042109509654, "Ringleader" : 825374102557687848, "Terror" : 825374139824996362, "Overlord" : 825374199202971648}
        xpRoles = {"Apprentice" :  825374343734362132, "Acolyte" : 825374387858702358, "Disciple" : 825374433081688075, "Magus" : 825374469287575583, "Wizard" : 825374528645496895, "Archwizard" : 825374576280207411, "Grandmaster" : 825374626015608854}

        data[entry] = value
        if entry == "XP":
          Ranks = {"Apprentice":0, "Acolyte":500, "Disciple":1200, "Magus":2000, "Wizard":3000, "Archwizard":4500, "Grandmaster":6500}
          for k,v in Ranks.items():
            if int(value) >= int(v):
              data["Rank"] = k

          xpRole = discord.utils.get(bot.edenguild.roles, id = xpRoles[data["Rank"]])
          if xpRole not in user.roles:
            for role,roleID in xpRoles.items():
              oldXPRole = discord.utils.get(bot.edenguild.roles, id = roleID)
              if oldXPRole in user.roles:
                await user.remove_roles(oldXPRole, reason = "Updating Character.", atomic=True)
                break
                
            await user.add_roles(xpRole, reason = "Character Updated.", atomic=True)
        elif entry == "Fame Points":
          Fame = {"Mage" : 0, "Peacekeeper" : 100, "Lightbringer" : 200, "Liberator" : 300, "Guardian" : 400}
          Infamy = {"Sorceror" : 0, "Agitator" : 100, "Ringleader" : 200, "Terror" : 300, "Overlord" : 400}

          if data["Alignment"] == "Imperial Mage":
            for k,v in Fame.items():
              if int(value) >= int(v):
                data["Fame Rank"] = k
          elif data["Alignment"] == "Dark Mage":
            for k,v in Infamy.items():
              if int(value) >= int(v):
                data["Fame Rank"] = k
          
          fameRole = discord.utils.get(bot.edenguild.roles, id = fameRoles[data["Fame Rank"]])
          if fameRole not in user.roles:
            for role,roleID in fameRoles.items():
              oldFameRole = discord.utils.get(bot.edenguild.roles, id = roleID)
              if oldFameRole in user.roles:
                await user.remove_roles(oldFameRole, reason = "Updating Character.", atomic=True)
                break

            await user.add_roles(fameRole, reason = "Character Updated.", atomic=True)
        elif entry == "Alignment":
          Fame = {"Mage" : 0, "Peacekeeper" : 100, "Lightbringer" : 200, "Liberator" : 300, "Guardian" : 400}
          Infamy = {"Sorceror" : 0, "Agitator" : 100, "Ringleader" : 200, "Terror" : 300, "Overlord" : 400}

          if value == "Imperial Mage":
            for k,v in Fame.items():
              if int(data["Fame Points"]) >= int(v):
                data["Fame Rank"] = k
          elif value == "Dark Mage":
            for k,v in Infamy.items():
              if int(data["Fame Points"]) >= int(v):
                data["Fame Rank"] = k

          fameRole = discord.utils.get(bot.edenguild.roles, id = fameRoles[data["Fame Rank"]])
          if fameRole not in user.roles:
            for role,roleID in fameRoles.items():
              oldFameRole = discord.utils.get(bot.edenguild.roles, id = roleID)
              if oldFameRole in user.roles:
                await user.remove_roles(oldFameRole, reason = "Updating Character.", atomic=True)
                break

            fameRole = discord.utils.get(bot.edenguild.roles, id = fameRoles[data["Fame Rank"]])
            await user.add_roles(fameRole, reason = "Character Updated.", atomic=True)
        elif entry == "Max Mana":
          data["Mana"] = value
      db.update(data, query.Name == ModData["Name"])
      await ctx.send("Updated Successfully.")

      url = "https://jsonstorage.net/api/items/be81d9d4-98cb-4aeb-83af-d7620f2af136"
      headers = {'Content-Type': 'application/json'}

      with open("JSON Data Files/Characters.json", "r") as charfile:
        data = json.load(charfile)
      async with aiohttp.ClientSession(headers = headers) as session:
        print(data)
        async with session.put(url, json = data, headers = headers) as r:
          print(r.status)
          responseText = await r.json()
          print(str(responseText))
      #req = requests.put(url, json=data, headers=headers)
      #print(req.status_code)
      #print(req.text)
          if r.status == 200 or r.status == 201:
            await ctx.send("Backed Up Successfully!")
            await UpdateTables()
          else:
            await ctx.send("Wait, that one wasn't backed up correctly!")
    else:
      await ctx.send("Exited Successfully. Run the command again if you still wish to modify a character.")



async def Trade(operation, **kwargs):
  db = TinyDB('JSON Data Files/Trade.json')
  tradeTable = db.table("Trade")
  #relationsTable = db.table("Relations")
  countriesTable = db.table("Countries")
  country = kwargs["country"]
  query = Query()

  if operation == "see":
    countriesOutput = countriesTable.search(query.Country == country)
    exportOutput = tradeTable.search(query["Imported From"] == country)
    importOutput = tradeTable.search(query["Exported To"] == country)
    #relationOutput = relationsTable.search(query.Country1 == country)
    countryData = {"Country": "", "Wealth": "", "Tax" : "", "Debt" : "", "Monthly Installment" : "", "Commodities Exported" : [], "Gross Income" : "", "Commodities Imported" : [], "Expenditure" : "", "Monthly Profit" : ""}
    
    for k,v in countriesOutput[0].items():
      countryData[k] = v

    commodityList, incomeSum = [], 0
    for i in exportOutput:
      for k,v in i.items():
        if k == "Commodity":
          commodityList.append(v)
        elif k == "Total Cost":
          incomeSum += v
    countryData["Commodities Exported"] = commodityList
    countryData["Gross Income"] = incomeSum

    commodityList, costSum = [], 0
    for i in importOutput:
      for k,v in i.items():
        if k == "Commodity":
          commodityList.append(v)
        elif k == "Total Cost":
          costSum += v
    countryData["Commodities Imported"] = commodityList
    countryData["Expenditure"] = costSum

    countryData["Monthly Profit"] = countryData["Gross Income"] - countryData["Expenditure"] - countryData["Tax"] - countryData["Monthly Installment"]

    # relations = {}
    # for i in relationOutput:
    #   country2, relation = "", ""
    #   for k,v in i.items():
    #     if k == "Country2":
    #       country2 = v
    #     elif k == "Relation":
    #       relation = v
    #   relations[country2] = relation
    # countryData["Relations"] = relations

    return countryData
  elif operation == "export" or operation == "import":
    if operation == "export":
      output = tradeTable.search(query["Imported From"] == country)
    elif operation == "import":
      output = tradeTable.search(query["Exported To"] == country)

    countryData = {"Country" : country, "Commodity" : [], "Quantity" : [], "Price" : []}

    commodityList, quantityList, priceList, exportList, importList= [], [], [], [], []

    for i in output:
      for k,v in i.items():
        if k == "Commodity":
          commodityList.append(str(v))
        elif k == "Quantity":
          quantityList.append(str(v))
        elif k == "Price":
          priceList.append(str(v))
        elif k == "Exported To":
          exportList.append(v)
        elif k == "Imported From":
          importList.append(v)

    if commodityList:
      countryData["Commodity"] = commodityList
    else:
      countryData["Commodity"] = ["\u200b"]
    if quantityList:
      countryData["Quantity"] = quantityList
    else:
      countryData["Quantity"] = ["\u200b"]
    if priceList:
      countryData["Price"] = priceList
    else:
      countryData["Price"] = ["\u200b"]
    if operation == "export":
      if exportList:
        countryData["Exported To"] = exportList
      else:
        countryData["Exported To"] = ["\u200b"]
    elif operation == "import":
      if importList:
        countryData["Imported From"] = importList
      else:
        countryData["Imported From"] = ["\u200b"]
    return countryData

@bot.group(name="tradeInfo", aliases = ["tradeinfo", "TradeInfo"], invoke_without_command = True)
async def tradeInfo(ctx, country):
    guild = ctx.guild
    author = ctx.author
    country = country.capitalize()
    colors = {'Alfenheim' : 0x228b22, 'Vanaheim' : 0xa2d2df, 'Viridi' : 0x257ca3, 'Summerwind' : 0xe7c496, "Ironhold" : 0x808080}
    descriptions = {'Alfenheim' : 'The Elven Nation', 'Vanaheim' : 'The Nordic Nation', 'Viridi' : 'The Fish Nation', 'Summerwind' : 'The Human Nation', "Ironhold" : "The Imperial Capital"}
    if discord.utils.get(bot.edenguild.roles, id = 825168015016067113) not in author.roles and discord.utils.get(bot.edenguild.roles, id = 825167943972159509) not in author.roles:
      await ctx.send("You aren't permitted to see trade information.")
    else:
      if country.capitalize() in ["Alfenheim", "Vanaheim", "Viridi", "Summerwind", "Ironhold"]:
        info = await Trade("see", country = country)
        print(info)
        embed = discord.Embed(title = country, color = colors[country], description = descriptions[country])
        # switcher = True
        for n, i in enumerate(["Wealth", "Tax", "Debt", "Monthly Installment", "Commodities Exported", "Gross Income", "Commodities Imported", "Expenditure", "Monthly Profit"]):
          if i == "Commodities Exported" or i == "Commodities Imported":
            embed.add_field(name = i, value = str(", ".join(info[i])), inline = True)            
          # elif i == "Relations":
          #   relString = ", ".join([": ".join(r) for r in info[i].items()])
          #   embed.add_field(name = i, value = str(relString), inline = True)
          else:
            embed.add_field(name = i, value = str(info[i]), inline = True)
          if (n+1)%2 == 0:
            embed.add_field(name = "\u200b", value = "\u200b", inline = True)
          # if switcher:
          #   embed.add_field(name = "\u200b", value = "\u200b", inline = True)
          # switcher = not switcher
        await ctx.send(embed=embed)
      else:
        await ctx.send("That Country doesn't exist. Pick one from Ironhold, Alfenheim, Vanaheim, Viridi and Summerwind.")

@tradeInfo.command(name = "export", aliases= ["Export"])
async def exportInfo(ctx, country):
  guild = ctx.guild
  author = ctx.author
  country = country.capitalize()
  colors = {'Alfenheim' : 0x228b22, 'Vanaheim' : 0xa2d2df, 'Viridi' : 0x257ca3, 'Summerwind' : 0xe7c496, "Ironhold" : 0x808080}
  info = await Trade("export", country = country)
  print(info)

  embed = discord.Embed(title = "Export Commodities", color = colors[country], description = "Commodities Exported by " + country + ".")
  embed.add_field(name = "Commodities", value = "\n".join(info["Commodity"]), inline = True)
  embed.add_field(name = "Exported To", value = "\n".join(info["Exported To"]), inline = True)
  embed.add_field(name = "Quantity", value = "\n".join(info["Quantity"]), inline = True)
  embed.add_field(name = "Price", value = "\n".join(info["Price"]), inline = True)
  await ctx.send(embed=embed)

@tradeInfo.command(name = "import", aliases=["Import"])
async def importInfo(ctx, country):
  guild = ctx.guild
  author = ctx.author
  country = country.capitalize()
  colors = {'Alfenheim' : 0x228b22, 'Vanaheim' : 0xa2d2df, 'Viridi' : 0x257ca3, 'Summerwind' : 0xe7c496, "Ironhold" : 0x808080}
  info = await Trade("import", country = country)
  print(info)

  embed = discord.Embed(title = "Import Commodities", color = colors[country], description = "Commodities Imported by " + country + ".")
  embed.add_field(name = "Commodities", value = "\n".join(info["Commodity"]), inline = True)
  embed.add_field(name = "Imported From", value = "\n".join(info["Imported From"]), inline = True)
  embed.add_field(name = "Quantity", value = "\n".join(info["Quantity"]), inline = True)
  embed.add_field(name = "Price", value = "\n".join(info["Price"]), inline = True)
  await ctx.send(embed=embed)

@bot.group(name="modTrade", aliases = ["modtrade", "ModTrade"], invoke_without_command=True)
async def modTrade(ctx, country):
  guild = ctx.guild
  author = ctx.author
  country = country.capitalize()
  colors = {'Alfenheim' : 0x228b22, 'Vanaheim' : 0xa2d2df, 'Viridi' : 0x257ca3, 'Summerwind' : 0xe7c496, "Ironhold" : 0x808080}
  descriptions = {'Alfenheim' : 'The Elven Nation', 'Vanaheim' : 'The Nordic Nation', 'Viridi' : 'The Fish Nation', 'Summerwind' : 'The Human Nation', "Ironhold" : "The Imperial Capital"}
  if discord.utils.get(bot.edenguild.roles, id = 825077295198502923) not in author.roles:
      await ctx.send("You aren't permitted to edit trade information.")
  else:
    exit = 0
    ModData = {}
    ModTemplate = ["Entry", "New Value"]
    ValidEntry = ["Wealth", "Tax"]

    for n, i in enumerate(ModTemplate):
      def check1(m):
        return m.author == author and m.channel == ctx.channel and (m.content.capitalize() in ValidEntry or n == 1)
      await ctx.send(", ".join(ValidEntry))
      try:
        reply = await bot.wait_for("message", timeout = 120.0, check = check1)
        ModData[ModTemplate[n]] = "{.content}".format(reply)
        print(reply.content)
        if reply.content == "exit":
          exit = 1
          break
      except asyncio.TimeoutError:
        await ctx.send("Timed Out! Please run the command again.")
        exit = 1
        break

    if exit == 0:
      entry = ModData["Entry"].capitalize()
      value = ModData["New Value"]    
      if entry == "Wealth" or entry == "Tax":
        db = TinyDB("JSON Data Files/Trade.json")
        countriesTable = db.table("Countries")
        query = Query()

        countriesTable.update({entry : int(value)}, query.Country == country)

      # if entry == "Relations":
      #   country2 = value.capitalize()
      #   db = TinyDB("JSON Data Files/Trade.json")
      #   relationsTable = db.table("Relations")
      #   query = Query()

      #   def check1(m):
      #     return m.author == author and m.channel == ctx.channel and m.content.title() in ["Amicable", "Tensions Rising", "At War"]
      #   await ctx.send("Enter the new Relation. (Amicable/Tensions Rising/At War)")
      #   try:
      #     reply = await bot.wait_for("message", timeout = 120.0, check=check1)
      #     value = reply.content.title()
      #   except asyncio.TimeoutError:
      #     await ctx.send("Timed Out! Please run the command again.")
      #     exit = 1
        
      #   if exit == 0:
      #     relationsTable.update({"Relation" : value}, (query.Country1 == country) & (query.Country2 == country2))
      #   else:
      #     await ctx.send("Exited Successfully.")

    elif exit == 1:
      await ctx.send("Exited Successfully.")
    await ctx.send("Updated Successfully.")
          
@modTrade.command(name="export", aliases=["Export"])
async def modExport(ctx, country):
  country = country.capitalize()
  guild = ctx.guild
  author = ctx.author
  colors = {'Alfenheim' : 0x228b22, 'Vanaheim' : 0xa2d2df, 'Viridi' : 0x257ca3, 'Summerwind' : 0xe7c496, "Ironhold" : 0x808080}
  exit = 0
  
  await ctx.send("Add, Remove or Edit?")
  def check1(m):
    return m.author == author and m.channel == ctx.channel and m.content.capitalize() in ["Add", "Remove", "Edit"]
  try:
    reply = await bot.wait_for("message", timeout=120.0, check = check1)
  except asyncio.TimeoutError:
    await ctx.send("Timed Out! Please run the command again.")
    exit = 1
  reply = reply.content.capitalize()
  
  if reply == "Add" and exit == 0:
    db = TinyDB("JSON Data Files/Trade.json")
    commodityTable = db.table("Commodities")
    query = Query()
    commodityList, priceList = [], []

    data = commodityTable.search(query.Source == country)
    for commodity in data:
      commodityList.append(commodity["Commodity"])
      priceList.append(str(commodity["Price"]))
    
    embed = discord.Embed(title = "Export Commodities", color = colors[country], description = "Commodities Which Can Be Exported by " + country + ".")
    embed.add_field(name = "Commodities", value = "\n".join(commodityList), inline = True)
    embed.add_field(name = "\u200b", value = "\u200b", inline = True)
    embed.add_field(name = "Price", value = "\n".join(priceList), inline = True)
    await ctx.send(embed=embed)

    info = await Trade("export", country=country)

    embed = discord.Embed(title = "Export Commodities", color = colors[country], description = "Commodities Exported by " + country + ".")
    embed.add_field(name = "Commodities", value = "\n".join(info["Commodity"]), inline = True)
    embed.add_field(name = "Exported To", value = "\n".join(info["Exported To"]), inline = True)
    embed.add_field(name = "Quantity", value = "\n".join(info["Quantity"]), inline = True)
    embed.add_field(name = "Price", value = "\n".join(info["Price"]), inline = True)
    await ctx.send(embed=embed)

    await ctx.send("Which Commodity do you wish to add? Pick from the table, or just enter a new one.")

    def check1(m):
      return m.author == author and m.channel == ctx.channel
    try:
      reply = await bot.wait_for("message", timeout=120.0, check=check1)
    except asyncio.TimeoutError:
      await ctx.send("Timed Out! Please run the command again.")
      exit = 1
    commodityName = reply.content.title()

    ModData = {}
    ModTemplate = ["Quantity", "Second Country"]
    if commodityName not in commodityList:
      ModTemplate.append("Price")
    for n, i in enumerate(ModTemplate):
      await ctx.send("Enter {0}.".format(i))
      try:
        reply = await bot.wait_for("message", timeout=120.0, check=check1)
        ModData[ModTemplate[n]] = reply.content.title()
      except asyncio.TimeoutError:
        await ctx.send("Timed Out! Please run the command again.")
        exit = 1
    
    if exit == 0:
      if commodityName in commodityList:
        for commodity in data:
          if commodity["Commodity"] == commodityName:
              ModData["Price"] = commodity["Price"]
      
      secondCountry, quantity, price = ModData["Second Country"], int(ModData["Quantity"]), int(ModData["Price"])

      tradeTable = db.table("Trade")
      tradeTable.insert({"Commodity" : commodityName, "Imported From" : country, "Exported To" : secondCountry, "Quantity" : quantity, "Price" : price, "Total Cost" : price*quantity})

      if commodityName not in commodityList:
        commodityTable.insert({"Commodity" : commodityName, "Source" : country, "Price" : price })

    elif exit == 1:
      await ctx.send("Exited Successfully.")

  elif reply == "Remove" and exit == 0:
    db = TinyDB("JSON Data Files/Trade.json")
    tradeTable = db.table("Trade")
    query = Query()

    info = await Trade("export", country=country)

    embed = discord.Embed(title = "Export Commodities", color = colors[country], description = "Commodities Exported by " + country + ".")
    embed.add_field(name = "Commodities", value = "\n".join(info["Commodity"]), inline = True)
    embed.add_field(name = "Exported To", value = "\n".join(info["Exported To"]), inline = True)
    embed.add_field(name = "Quantity", value = "\n".join(info["Quantity"]), inline = True)
    embed.add_field(name = "Price", value = "\n".join(info["Price"]), inline = True)
    await ctx.send(embed=embed)

    await ctx.send("Which Commodity do you wish to remove?")

    def check1(m):
      return m.author == author and m.channel == ctx.channel
    try:
      reply = await bot.wait_for("message", timeout=120.0, check=check1)
    except asyncio.TimeoutError:
      await ctx.send("Timed Out! Please run the command again.")
      exit = 1
    commodityName = reply.content.title()

    tradeBatches = tradeTable.search((query.Commodity == commodityName) & (query["Imported From"] == country))
    print(tradeBatches)
    print(len(tradeBatches))

    if len(tradeBatches) > 1 and exit == 0:
      await ctx.send("Remove from being exported to which country?")
      countryList = []
      for batch in tradeBatches:
        countryList.append(batch["Exported To"])
      await ctx.send(", ".join(countryList))
      
      def check1(m):
        return m.author == author and m.channel == ctx.channel and m.content.capitalize() in countryList
      try:
        reply = await bot.wait_for("message", timeout=120.0, check=check1)
        country2 = reply.content.capitalize()
      except asyncio.TimeoutError:
        await ctx.send("Timed Out! Please run the command again.")
        exit = 1
    elif not len(tradeBatches) > 1 and exit == 0:
      country2 = tradeBatches[0]["Exported To"]
    
    tradeRelation = tradeTable.get((query.Commodity == commodityName) & (query["Exported To"] == country2) & (query["Imported From"] == country))
    tradeRelation = tradeRelation.doc_id

    tradeTable.remove(doc_ids=[tradeRelation])

  elif reply == "Edit" and exit == 0:
    db = TinyDB("JSON Data Files/Trade.json")
    tradeTable = db.table("Trade")
    query = Query()

    info = await Trade("export", country=country)

    embed = discord.Embed(title = "Export Commodities", color = colors[country], description = "Commodities Exported by " + country + ".")
    embed.add_field(name = "Commodities", value = "\n".join(info["Commodity"]), inline = True)
    embed.add_field(name = "Exported To", value = "\n".join(info["Exported To"]), inline = True)
    embed.add_field(name = "Quantity", value = "\n".join(info["Quantity"]), inline = True)
    embed.add_field(name = "Price", value = "\n".join(info["Price"]), inline = True)
    await ctx.send(embed=embed)

    await ctx.send("Which Commodity do you wish to edit?")

    def check1(m):
      return m.author == author and m.channel == ctx.channel
    try:
      reply = await bot.wait_for("message", timeout=120.0, check=check1)
    except asyncio.TimeoutError:
      await ctx.send("Timed Out! Please run the command again.")
      exit = 1
    commodityName = reply.content.title()

    tradeBatches = tradeTable.search(query.Commodity == commodityName)

    if len(tradeBatches) > 1 and exit == 0:
      await ctx.send("Edit the exports to which country?")
      countryList = []
      for batch in tradeBatches:
        countryList.append(batch["Exported To"])
      await ctx.send(", ".join(countryList))
      
      def check1(m):
        return m.author == author and m.channel == ctx.channel and m.content.capitalize() in countryList
      try:
        reply = await bot.wait_for("message", timeout=120.0, check=check1)
        country2 = reply.content.capitalize()
      except asyncio.TimeoutError:
        await ctx.send("Timed Out! Please run the command again.")
        exit = 1
    elif not len(tradeBatches) > 1 and exit == 0:
      country2 = tradeBatches[0]["Exported To"]

    await ctx.send("Enter new Quantity.")
    
    def check1(m):
      return m.author == author and m.channel == ctx.channel
    try:
      reply = await bot.wait_for("message", timeout=120.0, check=check1)
    except asyncio.TimeoutError:
      await ctx.send("Timed Out! Please run the command again.")
      exit = 1
    quantity = reply.content
    price = tradeTable.search((query.Commodity == commodityName) & (query["Exported To"] == country2) & (query["Imported From"] == country))[0]["Price"]

    tradeTable.update({"Quantity" : int(quantity), "Total Cost" : int(quantity) * int(price)}, (query.Commodity == commodityName) & (query["Exported To"] == country2) & (query["Imported From"] == country))
    
  elif exit == 1:
      await ctx.send("Exited Successfully.")
  await ctx.send("Updated Successfully.")

@modTrade.command(name="import", aliases=["Import"])
async def modImport(ctx, country):
  country = country.capitalize()
  guild = ctx.guild
  author = ctx.author
  colors = {'Alfenheim' : 0x228b22, 'Vanaheim' : 0xa2d2df, 'Viridi' : 0x257ca3, 'Summerwind' : 0xe7c496, "Ironhold" : 0x808080}
  exit = 0
  
  await ctx.send("Add, Remove or Edit?")
  def check1(m):
    return m.author == author and m.channel == ctx.channel and m.content.capitalize() in ["Add", "Remove", "Edit"]
  try:
    reply = await bot.wait_for("message", timeout=120.0, check = check1)
  except asyncio.TimeoutError:
    await ctx.send("Timed Out! Please run the command again.")
    exit = 1
  reply = reply.content.capitalize()
  
  if reply == "Add" and exit == 0:
    db = TinyDB("JSON Data Files/Trade.json")
    commodityTable = db.table("Commodities")
    query = Query()
    commodityList, priceList, countryList = [], [], []

    data = commodityTable.all()
    for commodity in data:
      commodityList.append(commodity["Commodity"])
      priceList.append(str(commodity["Price"]))
      countryList.append(commodity["Source"])
    
    embed = discord.Embed(title = "Import Commodities", color = colors[country], description = "Commodities Which Can Be Imported by " + country + ".")
    embed.add_field(name = "Commodities", value = "\n".join(commodityList), inline = True)
    embed.add_field(name = "From", value = "\n".join(countryList), inline = True)
    embed.add_field(name = "Price", value = "\n".join(priceList), inline = True)
    await ctx.send(embed=embed)

    info = await Trade("import", country=country)

    embed = discord.Embed(title = "Import Commodities", color = colors[country], description = "Commodities Imported by " + country + ".")
    embed.add_field(name = "Commodities", value = "\n".join(info["Commodity"]), inline = True)
    embed.add_field(name = "Imported From", value = "\n".join(info["Imported From"]), inline = True)
    embed.add_field(name = "Quantity", value = "\n".join(info["Quantity"]), inline = True)
    embed.add_field(name = "Price", value = "\n".join(info["Price"]), inline = True)
    await ctx.send(embed=embed)

    await ctx.send("Which Commodity do you wish to add? Pick from the table.")

    def check1(m):
      return m.author == author and m.channel == ctx.channel
    try:
      reply = await bot.wait_for("message", timeout=120.0, check=check1)
    except asyncio.TimeoutError:
      await ctx.send("Timed Out! Please run the command again.")
      exit = 1
    commodityName = reply.content.title()

    ModData = {}
    ModTemplate = ["Quantity", "Second Country"]
    for n, i in enumerate(ModTemplate):
      await ctx.send("Enter {0}.".format(i))
      try:
        reply = await bot.wait_for("message", timeout=120.0, check=check1)
        ModData[ModTemplate[n]] = reply.content.title()
      except asyncio.TimeoutError:
        await ctx.send("Timed Out! Please run the command again.")
        exit = 1
    
    tradeRelation = commodityTable.search((query.Commodity == commodityName) & (query.Source == ModData["Second Country"]))
    if len(tradeRelation) == 0:
      exit = 1
      await ctx.send("That country does not export that good! Run the Command again, or run the export command from that country to add that good to that country's list of exports.")

    if exit == 0:
      ModData["Price"] = tradeRelation[0]["Price"]
      
      secondCountry, quantity, price = ModData["Second Country"], int(ModData["Quantity"]), int(ModData["Price"])

      tradeTable = db.table("Trade")
      tradeTable.insert({"Commodity" : commodityName, "Imported From" : secondCountry, "Exported To" : country, "Quantity" : quantity, "Price" : price, "Total Cost" : price*quantity})

    elif exit == 1:
      await ctx.send("Exited Successfully.")

  elif reply == "Remove" and exit == 0:
    db = TinyDB("JSON Data Files/Trade.json")
    tradeTable = db.table("Trade")
    query = Query()

    info = await Trade("import", country=country)

    embed = discord.Embed(title = "Import Commodities", color = colors[country], description = "Commodities Imported by " + country + ".")
    embed.add_field(name = "Commodities", value = "\n".join(info["Commodity"]), inline = True)
    embed.add_field(name = "Imported From", value = "\n".join(info["Imported From"]), inline = True)
    embed.add_field(name = "Quantity", value = "\n".join(info["Quantity"]), inline = True)
    embed.add_field(name = "Price", value = "\n".join(info["Price"]), inline = True)
    await ctx.send(embed=embed)

    await ctx.send("Which Commodity do you wish to remove?")

    def check1(m):
      return m.author == author and m.channel == ctx.channel
    try:
      reply = await bot.wait_for("message", timeout=120.0, check=check1)
    except asyncio.TimeoutError:
      await ctx.send("Timed Out! Please run the command again.")
      exit = 1
    commodityName = reply.content.capitalize()

    tradeBatches = tradeTable.search((query.Commodity == commodityName) & (query["Exported To"] == country))
    print(tradeBatches)
    print(len(tradeBatches))

    if len(tradeBatches) > 1 and exit == 0:
      await ctx.send("Remove from being imported from which country?")
      countryList = []
      for batch in tradeBatches:
        countryList.append(batch["Imported From"])
      await ctx.send(", ".join(countryList))
      
      def check1(m):
        return m.author == author and m.channel == ctx.channel and m.content.capitalize() in countryList
      try:
        reply = await bot.wait_for("message", timeout=120.0, check=check1)
        country2 = reply.content.capitalize()
      except asyncio.TimeoutError:
        await ctx.send("Timed Out! Please run the command again.")
        exit = 1
    elif not len(tradeBatches) > 1 and exit == 0:
      country2 = tradeBatches[0]["Imported From"]
    
    tradeRelation = tradeTable.get((query.Commodity == commodityName) & (query["Imported From"] == country2) & (query["Exported To"] == country))
    tradeRelation = tradeRelation.doc_id

    tradeTable.remove(doc_ids=[tradeRelation])

  elif reply == "Edit" and exit == 0:
    db = TinyDB("JSON Data Files/Trade.json")
    tradeTable = db.table("Trade")
    query = Query()

    info = await Trade("import", country=country)

    embed = discord.Embed(title = "Import Commodities", color = colors[country], description = "Commodities Imported by " + country + ".")
    embed.add_field(name = "Commodities", value = "\n".join(info["Commodity"]), inline = True)
    embed.add_field(name = "Imported From", value = "\n".join(info["Imported From"]), inline = True)
    embed.add_field(name = "Quantity", value = "\n".join(info["Quantity"]), inline = True)
    embed.add_field(name = "Price", value = "\n".join(info["Price"]), inline = True)
    await ctx.send(embed=embed)

    await ctx.send("Which Commodity do you wish to edit?")

    def check1(m):
      return m.author == author and m.channel == ctx.channel
    try:
      reply = await bot.wait_for("message", timeout=120.0, check=check1)
    except asyncio.TimeoutError:
      await ctx.send("Timed Out! Please run the command again.")
      exit = 1
    commodityName = reply.content.capitalize()

    tradeBatches = tradeTable.search((query.Commodity == commodityName) & (query["Exported To"] == country))

    if len(tradeBatches) > 1 and exit == 0:
      await ctx.send("Edit the imports from which country?")
      countryList = []
      for batch in tradeBatches:
        countryList.append(batch["Imported From"])
      await ctx.send(", ".join(countryList))
      
      def check1(m):
        return m.author == author and m.channel == ctx.channel and m.content.capitalize() in countryList
      try:
        reply = await bot.wait_for("message", timeout=120.0, check=check1)
        country2 = reply.content.capitalize()
      except asyncio.TimeoutError:
        await ctx.send("Timed Out! Please run the command again.")
        exit = 1
    elif not len(tradeBatches) > 1 and exit == 0:
      country2 = tradeBatches[0]["Imported From"]

    await ctx.send("Enter new Quantity.")
    
    def check1(m):
      return m.author == author and m.channel == ctx.channel
    try:
      reply = await bot.wait_for("message", timeout=120.0, check=check1)
    except asyncio.TimeoutError:
      await ctx.send("Timed Out! Please run the command again.")
      exit = 1
    quantity = reply.content
    price = tradeTable.search((query.Commodity == commodityName) & (query["Imported From"] == country2) & (query["Exported To"] == country))[0]["Price"]

    tradeTable.update({"Quantity" : int(quantity), "Total Cost" : int(quantity) * int(price)}, (query.Commodity == commodityName) & (query["Imported From"] == country2) & (query["Exported To"] == country))
    
  elif exit == 1:
    await ctx.send("Exited Successfully.")
  await ctx.send("Updated Successfully.")

async def myCalendar(ctx, includeToday = False, month = datetime.datetime.now(tz = datetime.timezone.utc).month, year = datetime.datetime.now(tz = datetime.timezone.utc).year, festivalInclude = True, multiFestival = True):
  Cal = calendar.Calendar()
  if includeToday:
    today = datetime.datetime.now(tz=datetime.timezone.utc)
  else:
    today = datetime.datetime(year, month, 1)
  monthName = today.strftime("%B")
  print(monthName)
  with open("JSON Data Files/Festivals.json", "r") as festivalFile:
    bot.festivals = json.load(festivalFile)
  festivals = bot.festivals[monthName]

  final = Image.new("RGBA", (1200, 634))
  nameBanner = Image.open("Images/Name Banner.png")
  scroll = Image.open("Images/Calendar Template.png")
  blank = final.paste(scroll, (int(final.width/2 - scroll.width/2)+10, 0), scroll)

  days = Cal.monthdayscalendar(year, month)
  dayList = []
  while len(days) < 6:
    days.append([0, 0, 0, 0, 0, 0, 0])
  for week in days:
    dayList.extend(week)
  del days
  days = iter(dayList)
  verticalMids = [163.6, 236.6, 309.6, 382.6, 455.6, 528.6]
  horizontalMids = [199.4, 302.5, 410.3, 517.3, 613.6, 707.2, 803.4]

  fnt1 = ImageFont.truetype("Fonts/Campanile.ttf", 48)

  draw1 = ImageDraw.Draw(final)

  for vm in verticalMids:
    for hm in horizontalMids:
      day = next(days)
      if day != 0:
        if day not in [int(i) for i in festivals.keys()]:
          draw1.text((hm+110, vm), str(day), font = fnt1, fill = (0,0,0,255), anchor="mm")
        else:
          draw1.text((hm+110, vm), str(day), font = fnt1, fill = (255,0,0,255), anchor="mm")
        if day == today.day and includeToday:
          circle = Image.open("Images/Circle.png")
          newSize = max(fnt1.getsize(str(day))) + 20
          circle = circle.resize((newSize, newSize))
          final.paste(circle, (int(hm+112-circle.width/2), int(vm+2-circle.height/2)), circle)
          circle.close()
        elif day < today.day and includeToday:
          line = Image.open("Images/Line.png")
          newSize = max(fnt1.getsize(str(day))) + 20
          line = line.resize((newSize, newSize))
          final.paste(line, (int(hm+112-line.width/2), int(vm-line.height/2)), line)
          line.close()

  final.save("Images/Temp Calendar.png")
  final.close()
  scroll.close()

  txt = Image.new("RGBA", nameBanner.size)
  fntsize = 48
  fnt = ImageFont.truetype(font = "Fonts/Campanile.ttf", size = fntsize)
  name =  monthName + " " + str(year)
  while fnt.getlength(name) > 354:
    fntsize -= 2
    fnt = ImageFont.truetype(font = "Fonts/Campanile.ttf", size = fntsize)

  draw = ImageDraw.Draw(txt)

  draw.text((int(nameBanner.width/2), 55), name, font = fnt, fill = (0,0,0,255), anchor = "mm")

  out = Image.alpha_composite(nameBanner, txt)
  out.save("Images/Temp Calendar Banner.png")
  nameBanner.close()
  
  Banner = discord.File("Images/Temp Calendar Banner.png", filename = "Banner.png")
  Scroll = discord.File("Images/Temp Calendar.png", filename = "Calendar.png")

  Banner = await ctx.send(file=Banner)
  Scroll = await ctx.send(file=Scroll)
  
  if festivalInclude == True and len(festivals) > 0:
    festivalScroll = Image.open("Images/Calendar Scroll Body.png")
    fnt2 = ImageFont.truetype("Fonts/Campanile.ttf", 42)
    
    if multiFestival or len(festivals) <= 8:
      festivalMessage = "\n".join([str(festival[0]) + " - " + festival[1] for festival in festivals.items()])
    else:
      festivalMessage = "\n".join([str(festival[0]) + " - " + festival[1] for festival in list(festivals.items())[:8]])

    if len(festivals) <= 8 or not multiFestival:
      final = Image.new("RGBA", (1200, 560))
      draw1 = ImageDraw.Draw(final)
      blank = final.paste(festivalScroll, (int(final.width/2 - festivalScroll.width/2)+10, 0), festivalScroll)
      draw1.multiline_text((int(final.width/2) + 10, int(final.height/2)), festivalMessage, font = fnt2, fill = (0,0,0,255), spacing=14, anchor = "mm", align = "center")
      
      final.save("Images/Temp Festival.png")
      final.close()
      festScroll = discord.File("Images/Temp Festival.png", filename = "Festivals.png")
      festScroll = await ctx.send(file=festScroll)
    else:
      while len(festivalMessage.split("\n")) > 8:
        final = Image.new("RGBA", (1200, 560))
        draw1 = ImageDraw.Draw(final)
        blank = final.paste(festivalScroll, (int(final.width/2 - festivalScroll.width/2)+10, 0), festivalScroll)
        draw1.multiline_text((int(final.width/2) + 10, int(final.height/2)), "\n".join(festivalMessage.split("\n")[:8]), font = fnt2, fill = (0,0,0,255), spacing=14, anchor = "mm", align = "center")

        festivalMessage = "\n".join(festivalMessage.split("\n")[8:])      
        final.save("Images/Temp Festival.png")
        final.close()
        festScroll = discord.File("Images/Temp Festival.png", filename = "Festivals.png")
        await ctx.send(file=festScroll)
      else:
        final = Image.new("RGBA", (1200, 560))
        draw1 = ImageDraw.Draw(final)
        blank = final.paste(festivalScroll, (int(final.width/2 - festivalScroll.width/2)+10, 0), festivalScroll)
        draw1.multiline_text((int(final.width/2) + 10, int(final.height/2)), festivalMessage, font = fnt2, fill = (0,0,0,255), spacing=14, anchor = "mm", align = "center")
      
        final.save("Images/Temp Festival.png")
        final.close()
        festScroll = discord.File("Images/Temp Festival.png", filename = "Festivals.png")
        await ctx.send(file=festScroll)
  return Banner, Scroll, festScroll

@bot.group(name = "calendar", aliases = ["Calendar", "cal", "Cal"], invoke_without_command = True)
async def calendarCommand(ctx):
  today = datetime.datetime.now(tz = datetime.timezone.utc)
  month = today.month
  year = today.year
  await myCalendar(ctx, includeToday = True, month = month, year = year, festivalInclude = True)
  
@calendarCommand.command(name = "month", aliases = ["Month", "m", "M"])
async def calendarMonth(ctx, monthint : typing.Optional[int] = 0, *, month = "Nothing"):
  print(monthint)
  if month != "Nothing" and monthint == 0:
    month = month.capitalize()
    monthint = datetime.datetime.strptime("01/" + month + "/2021 00:00", "%d/%B/%Y %H:%M").month
  await myCalendar(ctx, includeToday = False, month = monthint, festivalInclude = True)

@calendarCommand.command(name = "year", aliases = ["Year"])
async def calendarYear(ctx, year : typing.Optional[int] = 0):
  author = ctx.author
  channel = ctx.channel
  keepGoing = True
  leftArrow, rightArrow = u"\u2B05", u"\u27A1"
  today = datetime.datetime.now(datetime.timezone.utc)
  monthInt = today.month

  while keepGoing:  
    if year != 0:
      if monthInt == today.month:
        Banner, Scroll, festScroll = await myCalendar(ctx, includeToday = True, month = monthInt, year = year, multiFestival = False)  
      else:
        Banner, Scroll, festScroll = await myCalendar(ctx, month = monthInt, year = year, multiFestival = False)
    else:
      if monthInt == today.month:
        Banner, Scroll, festScroll = await myCalendar(ctx, includeToday = True, month = monthInt, multiFestival = False)
      else:
        Banner, Scroll, festScroll = await myCalendar(ctx, month = monthInt, multiFestival = False)
    
    if monthInt > 1:
      await festScroll.add_reaction(leftArrow)
    if monthInt < 12:
      await festScroll.add_reaction(rightArrow)
    def monthCheck(reaction, user):
      return user == author and str(reaction.emoji) in [leftArrow, rightArrow] and reaction.message == festScroll
    try:
      reaction = await bot.wait_for("reaction_add", timeout=180, check=monthCheck)
      if str(reaction[0].emoji) == leftArrow:
        monthInt -= 1
      elif str(reaction[0].emoji) == rightArrow:
        monthInt += 1
      
      await Banner.delete()
      await Scroll.delete()
      await festScroll.delete()
    except asyncio.TimeoutError:
      await ctx.send("Calendar Timed Out.")
      keepGoing = False
  
@bot.group(name="Weather", aliases=["weather"])
async def weather(ctx, *, city: typing.Optional[str] = "Ironhold"):
  city = city.title()
  cityDict = {"Ironhold" : "Los%20Angeles,us", "Vanaheim" : "Reykjavik,grl", "Summerwind" : "Cairo,eg", "Alfenheim" : "Manaus,br", "Viridi" : "Hawaii,us"}
  if city not in cityDict.keys():
    ctx.send("Enter a valid Kingdom!")
  else:
    async with aiohttp.ClientSession() as session:
      async with session.get(f"http://api.openweathermap.org/data/2.5/weather?q={cityDict[city]}&APPID=7aa7fa6666c419c855da254003c97194") as r:
        data = await r.json()
        embed = discord.Embed(title=city, description = data["weather"][0]["main"]+ ", " + data["weather"][0]["description"].title())
        embed.set_thumbnail(url = "http://openweathermap.org/img/wn/"+data["weather"][0]["icon"]+"@4x.png")
        embed.add_field(name="Temperature: ", value=str(round(data["main"]["temp"] - 273.15, 1))+"°C, " + str(round(((data["main"]["temp"] - 273.15)*(9/5)+32), 1)) + "°F")
        await ctx.send(embed=embed)

  #textCal = calendar.calendar(year)

  # await ctx.send("```" + textCal[:textCal.find("July")] + "```")
  # await ctx.send("```" + textCal[textCal.find("July"):] + "```")

keep_alive()
token = os.environ.get("DISCORD_BOT_SECRET")
bot.run(token)