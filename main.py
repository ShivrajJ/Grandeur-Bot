import discord
import sys
import traceback as trace
import os
import asyncio
import json
import requests
import math
from keep_alive import keep_alive



client = discord.Client()

async def UpdateTables():
  guild = discord.utils.get(client.guilds, id = 686858403569860643)
  allChannel = discord.utils.get(guild.channels, id = 752580846292172810)
  heroChannel = discord.utils.get(guild.channels, id = 752580861773217866)
  villainChannel = discord.utils.get(guild.channels, id = 752580877137084466)
  rogueChannel = discord.utils.get(guild.channels, id = 752580888390271036)
  with open("chardatabackup.json", "r") as datasheet:
    data = json.load(datasheet)
  channel = [allChannel, heroChannel, villainChannel, rogueChannel]
  for n, c in enumerate(("All", "Hero", "Villain", "Rogue")):
    async for message in channel[n].history(limit = 6):
      if message.author == client.user:
        await message.delete()
    if c == "All":
      tabledata = {data[i]["Name"]:(data[i]["XP"], data[i]["Alignment"], data[i]["Rank"]) for i in data.keys()}
    elif c == "Hero":
        c = ("Hero", "Sidekick")
        tabledata = {data[i]["Name"]:(data[i]["XP"], data[i]["Alignment"], data[i]["Rank"]) for i in data.keys() if data[i]["Alignment"] in c}    
    else:
      tabledata = {data[i]["Name"]:(data[i]["XP"], data[i]["Alignment"], data[i]["Rank"]) for i in data.keys() if data[i]["Alignment"] == c}
    sortdata = []
    for key, value in sorted(tabledata.items(), key = lambda item: int(item[1][0]), reverse = True):
      sortdata.append((key, value))
      print((key,value))#Sorting Entries by XP. Highest first.
    xpval = []
    for i in tabledata.values():
      xpval.append(i[0])
    print(len(tabledata))
    maxLenSNo = len("      ")
    maxLenName = len(max(tabledata.keys(), key=len)) + 2
    maxLenXP = len(max(xpval, key=len)) + 2
    maxLenAlign = len(" Alignment ")
    maxLenRank = len("      ")
    table = "╔"+"═"*maxLenSNo+"╦" + "═"*maxLenName + "╤" + "═"*maxLenXP +"╤" + "═"*maxLenAlign + "╤"+"═"*maxLenRank+"╗\n║ S.No ║ Name"+" "*(maxLenName-5)+"│ XP"+" "*(maxLenXP-3)+ "│ Alignment │ Rank ║\n╠"+"═"*maxLenSNo+"╬"+"═"*maxLenName+"╪"+"═"*maxLenXP+"╪"+"═"*maxLenAlign+"╪"+"═"*maxLenRank+"╣\n"
    rowlen = len(table)
    for i, x in enumerate(sortdata):
      nameSpaceLen = (maxLenName - len(x[0]))
      xpSpaceLen = (maxLenXP - len(x[1][0]))
      alignSpaceLen = (maxLenAlign - len(x[1][1]))
      if len(table)+rowlen*2<2000:
        table += "║ " + str(i+1) + " "*(maxLenSNo-1-len(str(i+1)))+"║" + " "*int((nameSpaceLen/2)) + x[0] + " "*int((nameSpaceLen/2)+nameSpaceLen%2) + "│" + " "*math.ceil(xpSpaceLen/2) + str(x[1][0]) + " "*int((xpSpaceLen/2)) +"| "+ x[1][1] +" "*(alignSpaceLen-1)+ "│ " + x[1][2] + " "*(maxLenRank-1-len(x[1][2]))+"║\n"
      
      if i+1 < len(sortdata) and len(table)+rowlen*3 < 2000:
        table += "╟"+"─"*maxLenSNo+"╫" + "─"*maxLenName + "┼"+ "─"*maxLenXP + "┼"+ "─"*maxLenAlign +"┼"+"─"*maxLenRank+"╢\n"
      elif i+1 > len(sortdata) or len(table)+rowlen*3>2000:
        table += "╚"+"═"*maxLenSNo+"╩" + "═"*maxLenName + "╧" + "═"*maxLenXP + "╧" + "═"*maxLenAlign + "╧"+"═"*maxLenRank+"╝"
        if len(table)+rowlen*3>2000:
          await channel[n].send("```"+table+"```")
        if i+1 > len(sortdata):
          break
        else:
          table ="╔"+"═"*maxLenSNo+"╦" + "═"*maxLenName + "╤" + "═"*maxLenXP +"╤" + "═"*maxLenAlign + "╤"+"═"*maxLenRank+"╗\n"
    table += "╚"+"═"*maxLenSNo+"╩" + "═"*maxLenName + "╧" + "═"*maxLenXP + "╧" + "═"*maxLenAlign + "╧"+"═"*maxLenRank+"╝"   
    await channel[n].send("```"+table+"```")

@client.event
async def on_ready():
  print("I'm in!")
  print(client.user)
  hoursSinceUp = 0
  while True:
    with open("chardatabackup.json", "w") as backup:
      url = "https://api.jsonbin.io/b/5f43fa5c514ec5112d0d5309/latest/"
      headers = {"secret-key" : "$2b$10$ZQTgjlmx9ABoAWGW.Y06TuFeJvd4YzZomB7T8QRyWWLAG.eEudPNK"}
      req = requests.get(url=url, headers = headers)
      data = json.loads(req.text)
      json.dump(data, backup)
    if hoursSinceUp%24 == 0:
      await UpdateTables()
    await asyncio.sleep(3600)
    hoursSinceUp += 1

@client.event
async def on_error(event, ctx):
  guild = discord.utils.get(client.guilds, id = 686858403569860643)
  tbfile = open("traceback.txt", "w")
  tbfile.write("")
  tbfile = open("traceback.txt", "r+")
  trace.print_exc(file = tbfile)
  tbfile.seek(0)
  output = tbfile.read()
  embed = discord.Embed(title = "Error!", description = "An error has occurred. Please contact the Bot Mechanic(Shivraj#3373) and point them towards this message.", color = 0xff0000)
  embed.add_field(name="Traceback", value="```" + output + "```", inline=False)
  if event == "on_member_join":
    channel = discord.utils.get(guild.channels, id = 740710852671438949)
    await channel.send(discord.utils.get(guild.members, id = 124102469646024704).mention)
    await channel.send(embed=embed)
    await channel.send(str(ctx))
  elif event == "on_message":
    await ctx.channel.send(discord.utils.get(guild.members, id = 124102469646024704).mention)
    await ctx.channel.send(embed=embed)

@client.event
async def on_message_delete(message):
  print("Delete")
  guild = message.guild
  embed = discord.Embed(title="Log")
  embed.add_field(name="\u200b", value="```" + str(message.author) + ":" + message.content + "```", inline=False)
  channel = discord.utils.get(guild.channels, id = 741683445973123132)
  await channel.send(embed=embed)

@client.event
async def on_member_join(member):
  guild = discord.utils.get(client.guilds, id = 686858403569860643)
  await member.edit(roles = [discord.utils.get(guild.roles, id = 740225928529182801)]);
  welcome = "Greetings, " + member.mention + "." + " Welcome to Grandeur. Please start by reading our rules: " + discord.utils.get(guild.channels, id = 740141711493300235).mention + ". Once you have familiarized yourself with the rules, please post a snippet of original creative writing/RP of no less than 200 words in " + discord.utils.get(guild.channels, id=740154990261174303).mention + "."
  embed = discord.Embed(title = "Welcome!", description = welcome)
  channel = discord.utils.get(guild.channels, id = 740159787035000912)
  embed.set_image(url="https://i.imgur.com/IXHUtNM.gif")
  await channel.send(member.mention)
  await channel.send(embed = embed)


@client.event
async def on_message(message):
  if message.author == client.user:
    return
  elif message.content.find("$reverse") == 0:
    await message.channel.send(message.content[-1:8:-1])
  elif message.content.find("$help") == 0:
    embed = discord.Embed(title="Help", description="All commands are listed here, but for the usage of each, type the command and then type help in front of the command. Eg- $char help.", color=0x00ffff)
    embed.add_field(name="$newchar",value="Adds a new Character to the database. Mod Only Command.",inline=True)
    embed.add_field(name="$char",value="Shows the Character's Card",inline=True)
    embed.add_field(name="$modchar",value="Modifies the Character's data. Mod Only Command.",inline=True)
    embed.add_field(name="$xp",value="Shows all the Characters and their XP in table form.",inline=True)
    embed.add_field(name="$approval",value="Creates an Approval Channel. Mod Only Command.",inline=True)
    embed.add_field(name="$remove",value="Removes an Approval Channel. Mod Only Command.",inline=True)
    embed.add_field(name="$purge",value="Purges/Deletes the number of messages mentioned with the command in the channel where it's used.",inline=True)
    embed.add_field(name="$reverse",value="Reverses whatever message is written after the command.",inline=True)  
    await message.channel.send(embed=embed)
  elif message.content.find("$newchar") == 0: #Making Character Entry into JSON file
    guild = message.guild
    exit = 0
    if not message.author.guild_permissions.manage_channels:
      await message.channel.send("You are not permitted to create a Character in the Database! Please contact a Staff Member.")
    elif message.content.find("help") != -1 or len(message.content.strip(" ")) > len("$newchar"):
      await message.channel.send("Just enter the command and follow the instructions the bot posts. Usage- ```$newchar```")
    else:
      MainTemplate = ["UserID", "Name", "Description", "XP", "Alignment", "Money", "Items", "Stats"]
      Parameters = {}
      for n, i in enumerate(MainTemplate):
        await message.channel.send("Enter %s:" % i)
        if n == 7:
          await message.channel.send("Power, Intelligence, Skillfulness, Technique, Speed")
        def check(m):
          return m.author == message.author and m.channel == message.channel
        try:
          reply = await client.wait_for('message', timeout = 120.0, check = check)
          if reply.content == "exit":
            exit = 1
            break
        except asyncio.TimeoutError:
          await message.channel.send("Timed out! Try again.")
          exit = 1
          break
        else:
          Parameters[MainTemplate[n]] = "{.content}".format(reply)
      if not exit:
        Ranks = {"D3":0, "D2":100, "D1":250, "C3":500, "C2":650, "C1":850, "B3":1150, "B2":1350, "B1":1600, "A3":1950, "A2":2200, "A1":2500, "S3":2900, "S2":3200, "S1":3550}
        for i, (k,v) in enumerate(Ranks.items()):
          if int(Parameters["XP"]) >= int(v):
            Parameters["Rank"] = k
        print(Parameters)
        StatTemplate = ["Power", "Intelligence", "Skillfulness", "Technique", "Speed"]
        StatList = Parameters["Stats"].strip("()").replace(" ", "").split(",")
        Parameters["Stats"] = {StatTemplate[i]:StatList[i] for i in range(len(StatList))}
        defaults = ["Undefined", "Undefined", "\u200b", "0", "Undefined", "0", "\u200b", "Stats"]
        Stats = "".join(StatList)
        statfile = open("CompletedCharts.txt", "r")
        statlength = len(statfile.readlines())
        statfile.seek(0)
        for i in range(statlength):
          CompleteStatCharts = statfile.readline()
          if Stats in CompleteStatCharts:
            break
        statfile.seek(0)
        if Stats in statfile.read():
          Parameters["StatImage"] = CompleteStatCharts.replace(Stats + " - ", "").replace("\n", "")
        else:
          Parameters["StatImage"] = "https://i.imgur.com/ur63BX8.png"
          with open("PendingCharts.txt", "a") as pending:
            pending.write("\n" + Stats + " " + str(client.get_user(int(Parameters["UserID"].strip("<@!>")))))
        statfile.close()
        for i, (k, v) in enumerate(Parameters.items()):
          if v == "0":
            Parameters[k] = defaults[i]
        await message.channel.send(str([k + ": " + str(v).strip("{}") for k, v in Parameters.items()]).strip("[]").replace("'", ""))
        await message.channel.send("Is this correct? (yes/no)")
        def check1(m):
          return m.author == message.author and m.channel == message.channel and m.content.lower() in ("yes", "no")
        try:
          reply = await client.wait_for('message', timeout = 120.0, check = check1)
        except asyncio.TimeoutError:
          await message.channel.send("Timed out! Try again.")
        else:
          if "{.content}".format(reply).lower() == "yes":
            url = "https://api.jsonbin.io/b/5f43fa5c514ec5112d0d5309/latest/"
            headers = {"secret-key" : "$2b$10$ZQTgjlmx9ABoAWGW.Y06TuFeJvd4YzZomB7T8QRyWWLAG.eEudPNK"}
            req = requests.get(url=url, headers = headers)
            data = json.loads(req.text)
            data[Parameters["UserID"]] = Parameters
            url = "https://api.jsonbin.io/b/5f43fa5c514ec5112d0d5309/"
            headers = {"content-type" : "application/json", "secret-key" : "$2b$10$ZQTgjlmx9ABoAWGW.Y06TuFeJvd4YzZomB7T8QRyWWLAG.eEudPNK"}
            req = requests.put(url=url, json=data, headers=headers)
            with open("chardatabackup.json", "w") as backup:
              json.dump(data, backup)
            print(req.text)
            if json.loads(req.text)["success"]:
              await message.channel.send("Registered successfully!")
            elif json.loads(req.text)["success"] == False:
              await message.channel.send("Something Went Wrong. Try Again, and if it keeps happening, call for the guy handling the bot.")
          elif "{.content}".format(reply).lower() == "no":
            await message.channel.send("Exited Successfully. Run the command again if you still wish to add a character.")
      else:
        await message.channel.send("Exited Successfully. Run the command again if you still wish to add a character.")
  elif message.content.find("$char") == 0:
    if message.content[6:10] == "help" or len(message.content.strip(" ")) < 6:
      await message.channel.send("Mention the user next to the command, or a character name. Usage: ```$char @abcdef```\nor\n```$char Superman```")
    else:
      with open("chardatabackup.json", "r") as backup:
        data = json.load(backup)
      if message.content[6:] in [data[i]["Name"] for i in data.keys()]:
        for k,v in data.items():
          if v["Name"] == message.content[6:]:
            user = v["UserID"]
            print(user)
      elif message.content[7] == "#":
        await message.channel.send("Mention a valid **user**, or a Character Name next to the command. Usage: ```$char @abcdef```\nor\n```$char Superman```")
      else:
        user = message.content[6:]
        if user[0] != "<" and user[-1] != ">":
          await message.channel.send("Please mention a valid user!")
      print(str(user))
      try:  
        embed = discord.Embed(title = data[user]["Name"], color = 0x00ffff, description = data[user]["Description"])
        embed.set_image(url=data[user]["StatImage"])
        embed.add_field(name = "XP", value = data[user]["XP"], inline = True)
        embed.add_field(name = "Money", value = data[user]["Money"], inline = True)
        embed.add_field(name = "Rank", value = data[user]["Rank"], inline = True)
        embed.add_field(name = "Alignment", value = data[user]["Alignment"], inline = True)
        embed.add_field(name = "Items", value = data[user]["Items"], inline = True)
        embed.add_field(name = "\u200b", value = "\u200b", inline = True)
        embed.add_field(name = "\u200b", value = "\u200b", inline = True)
        embed.add_field(name = "Power", value = data[user]["Stats"]["Power"], inline = True)
        embed.add_field(name = "\u200b", value = "\u200b", inline = True)
        embed.add_field(name = "Speed", value = data[user]["Stats"]["Speed"], inline = True)
        embed.add_field(name = "\u200b", value = "\u200b", inline = True)
        embed.add_field(name = "Intelligence", value = data[user]["Stats"]["Intelligence"], inline = True)
        embed.add_field(name = "Technique", value = data[user]["Stats"]["Technique"], inline = True)
        embed.add_field(name = "\u200b", value = "\u200b", inline = True)
        embed.add_field(name = "Skillfulness", value = data[user]["Stats"]["Skillfulness"], inline = True)
        await message.channel.send(embed=embed)
      except KeyError:
        await message.channel.send("That user does not have a character, or that Character Name is wrong.")
  elif message.content.find("$pending") == 0:
    with open("PendingCharts.txt", "r") as pending:
      await message.channel.send(pending.read())
  elif message.content.find("$modchar") == 0:
    guild = message.guild
    if not message.author.guild_permissions.manage_channels:
      await message.channel.send("You are not permitted to modify characters! Please contact a Staff Member.")
    else:
      if message.content[9:13] == "help" or len(message.content.strip(" ")) > len("$modchar"):
        await message.channel.send("Modify the character sheet. Run the command like such: ```$modchar``` Nothing more, and answer the prompts.")
      else:
        ModData = {}
        url = "https://api.jsonbin.io/b/5f43fa5c514ec5112d0d5309/latest/"
        headers = {"secret-key" : "$2b$10$ZQTgjlmx9ABoAWGW.Y06TuFeJvd4YzZomB7T8QRyWWLAG.eEudPNK"}
        req = requests.get(url=url, headers = headers)
        data = json.loads(req.text)
        url = "https://api.jsonbin.io/b/5f43fa5c514ec5112d0d5309/"
        exit = 0
        ModTemplate = ["Character Name", "Entry", "New Value"]
        ValidEntry = ["Name", "Description", "XP", "Rank", "Alignment", "Money", "Items", "StatImage", "Power", "Intelligence", "Skillfulness", "Technique", "Speed"]
        for n, i in enumerate(ModTemplate):
          await message.channel.send("Enter the {abc}".format(abc=i))
          if n == 1:
            await message.channel.send("Name, Description, XP, Rank, Alignment, Money, Items, StatImage, Stats[Only one from Power, Intelligence, Skillfulness, Technique, Speed]")
          def check2(m):
            return m.author == message.author and m.channel == message.channel
          try:
            reply = await client.wait_for("message", timeout=50.0, check = check2)
            if reply.content.lower() == "exit":
              exit = 1
              break
            elif n == 0:
              if reply.content not in [data[i]["Name"] for i in data.keys()]:
                await message.channel.send("Enter a Valid Character. That Character does not exist.")
                exit = 1
                break
            elif n == 1:
              if reply.content not in ValidEntry:
                await message.channel.send("Enter a valid Entry. Run the command again.")
                exit = 1
                break
          except asyncio.TimeoutError:
            await message.channel.send("Timed Out! Please run the command again.")
            exit = 1
            break
          else:
            ModData[ModTemplate[n]] = "{.content}".format(reply)
        if not exit:
          for k,v in data.items():
            if v["Name"] == ModData["Character Name"]:
              userID = v["UserID"]
          user = str(client.get_user(int(userID.strip("<@!>"))))
          entry = ModData["Entry"].capitalize()
          if entry == "Xp":
            entry = "XP"
          value = ModData["New Value"]
          print(value)
          if entry in ["Power", "Intelligence", "Skillfulness", "Technique", "Speed"]:
            Stats = "".join(data[user]["Stats"].values())
            for i, v in enumerate(["Power", "Intelligence", "Skillfulness", "Technique", "Speed"]):
              if v == entry:
                Stats = Stats[:i] + value + Stats[i+1:]
            statfile = open("CompletedCharts.txt", "r")
            statlength = len(statfile.readlines())
            statfile.seek(0)
            for i in range(statlength):
              CompleteStatCharts = statfile.readline()
              if Stats in CompleteStatCharts:
                break
            statfile.seek(0)
            if Stats in statfile.read():
              data[user]["StatImage"] = CompleteStatCharts.replace(Stats + " - ", "")
            else:
              with open("PendingCharts.txt", "w") as pending:
                pending.write("\n" + Stats)
            data[user]["Stats"][entry] = value
          else:
            data[user][entry] = value
            if entry == "XP":
              Ranks = {"D3":0, "D2":100, "D1":250, "C3":500, "C2":650, "C1":850, "B3":1150, "B2":1350, "B1":1600, "A3":1950, "A2":2200, "A1":2500, "S3":2900, "S2":3200, "S1":3550}
              for i, (k,v) in enumerate(Ranks.items()):
                if int(data[user]["XP"]) >= int(v):
                  data[user]["Rank"] = k
            headers = {"content-type" : "application/json", "secret-key" : "$2b$10$ZQTgjlmx9ABoAWGW.Y06TuFeJvd4YzZomB7T8QRyWWLAG.eEudPNK"}
            req = requests.put(url=url, json=data, headers=headers)
            with open("chardatabackup.json", "w") as backup:
              json.dump(data, backup)
            if entry == "XP":
              await UpdateTables()
            if json.loads(req.text)["success"]:
              await message.channel.send("Done!")
              await message.channel.send(entry + " has been changed to " + str(value))
            elif json.loads(req.text)["success"] == False:
              await message.channel.send("Something Went Wrong. Try Again, and if it keeps happening, call for the guy handling the bot.")
        else:
          await message.channel.send("Exited Successfully. Run the command again if you still wish to modify.")
  elif message.content.find("$xp") == 0:
    if message.content[4:8] == "help":
      await message.channel.send("Enter one of the following after sending the command: All, Hero, Villain, Rogue.")
    else:
      await message.channel.send("All, Hero, Villain or Rogue?")
      def check3(m):
        return m.author == message.author and m.channel == message.channel and m.content.lower().capitalize() in ["All", "Hero", "Villain", "Rogue"]
      try:
        reply = await client.wait_for("message", timeout = 50.0, check = check3)
      except asyncio.TimeoutError:
        await message.channel.send("Timed Out! Please Try Again.")
      else:
        category = reply.content.lower().capitalize()
      print(category)
      with open("chardatabackup.json", "r") as datasheet:
        data = json.load(datasheet)
      if category == "All":
        tabledata = {data[i]["Name"]:(data[i]["XP"], data[i]["Alignment"], data[i]["Rank"]) for i in data.keys()}
      elif category == "Hero":
        category = ("Hero", "Sidekick")
        tabledata = {data[i]["Name"]:(data[i]["XP"], data[i]["Alignment"], data[i]["Rank"]) for i in data.keys() if data[i]["Alignment"] in category}
      else:
        tabledata = {data[i]["Name"]:(data[i]["XP"], data[i]["Alignment"], data[i]["Rank"]) for i in data.keys() if data[i]["Alignment"] == category}
      print("Here is unsorted:\n" + str(tabledata))
      sortdata = []
      for key, value in sorted(tabledata.items(), key = lambda item: int(item[1][0]), reverse = True):
        sortdata.append((key, value))
        print((key,value))#Sorting Entries by XP. Highest first.
      xpval = []
      for i in tabledata.values():
        xpval.append(i[0])
      print(len(tabledata))
      maxLenSNo = len("      ")
      maxLenName = len(max(tabledata.keys(), key=len)) + 2
      maxLenXP = len(max(xpval, key=len)) + 2
      maxLenAlign = len(" Alignment ")
      maxLenRank = len("      ")
      table = "╔"+"═"*maxLenSNo+"╦" + "═"*maxLenName + "╤" + "═"*maxLenXP +"╤" + "═"*maxLenAlign + "╤"+"═"*maxLenRank+"╗\n║ S.No ║ Name"+" "*(maxLenName-5)+"│ XP"+" "*(maxLenXP-3)+ "│ Alignment │ Rank ║\n╠"+"═"*maxLenSNo+"╬"+"═"*maxLenName+"╪"+"═"*maxLenXP+"╪"+"═"*maxLenAlign+"╪"+"═"*maxLenRank+"╣\n"
      rowlen = len(table)
      for i, x in enumerate(sortdata):
        nameSpaceLen = (maxLenName - len(x[0]))
        xpSpaceLen = (maxLenXP - len(x[1][0]))
        alignSpaceLen = (maxLenAlign - len(x[1][1]))
        if len(table)+rowlen*2<2000:
          table += "║ " + str(i+1) + " "*(maxLenSNo-1-len(str(i+1)))+"║" + " "*int((nameSpaceLen/2)) + x[0] + " "*int((nameSpaceLen/2)+nameSpaceLen%2) + "│" + " "*math.ceil(xpSpaceLen/2) + str(x[1][0]) + " "*int((xpSpaceLen/2)) +"| "+ x[1][1] +" "*(alignSpaceLen-1)+ "│ " + x[1][2] + " "*(maxLenRank-1-len(x[1][2]))+"║\n"

        if i+1 < len(sortdata) and len(table)+rowlen*3 < 2000:
          table += "╟"+"─"*maxLenSNo+"╫" + "─"*maxLenName + "┼"+ "─"*maxLenXP + "┼"+ "─"*maxLenAlign +"┼"+"─"*maxLenRank+"╢\n"
        elif i+1 > len(sortdata) or len(table)+rowlen*3>2000:
          table += "╚"+"═"*maxLenSNo+"╩" + "═"*maxLenName + "╧" + "═"*maxLenXP + "╧" + "═"*maxLenAlign + "╧"+"═"*maxLenRank+"╝"
          if len(table)+rowlen*3>2000:
            await message.channel.send("```" + table + "```")
          if i+1 > len(sortdata):
            break
          else:
            table ="╔"+"═"*maxLenSNo+"╦" + "═"*maxLenName + "╤" + "═"*maxLenXP +"╤" + "═"*maxLenAlign + "╤"+"═"*maxLenRank+"╗\n"
      
      table += "╚"+"═"*maxLenSNo+"╩" + "═"*maxLenName + "╧" + "═"*maxLenXP + "╧" + "═"*maxLenAlign + "╧"+"═"*maxLenRank+"╝"   
      await message.channel.send("```"+table+"```")
  elif message.content.find("$approval") == 0:
    guild = message.guild
    if not message.author.guild_permissions.manage_channels:
      await message.channel.send("You are not permitted to create a channel! Please contact a Staff Member.")
    else:
      if message.content[10:14] == "help" or message.content[10] != "<":
        await message.channel.send("Mention the user who you're creating this channel for next to the command. Usage: ```$approval @abcdef```")
      else:
        user = message.content[10:].strip("<@!>")
        staff = 691276640629686334
        category = discord.utils.get(guild.categories, id = 691295206682918992)
        name = str(client.get_user(int(user)))[:-5]
        overwrites = {
          guild.default_role:discord.PermissionOverwrite(read_messages = True, send_messages = False),
          guild.get_member(int(user)):discord.PermissionOverwrite(read_messages = True, send_messages = True),
          guild.get_role(staff):discord.PermissionOverwrite(read_messages = True, send_messages = True)
        }
        channel = await guild.create_text_channel(name, overwrites = overwrites, category=category)
  elif message.content.find("$remove") == 0:
    guild = message.guild
    if not message.author.guild_permissions.manage_channels:
      await message.channel.send("You are not permitted to delete a channel! Please contact a Staff Member.")
    else:
      if message.content[8:12] == "help" or message.content[8] != "<":
        await message.channel.send("Link the channel to be deleted as such: #channelname, next to the command. Usage - ```$remove #channel```")
      else:
        print(message.content[9:])
        channelid = int(message.content[9:].strip("<@!>#"))
        categoryid = 691295206682918992
        channel = discord.utils.get(guild.channels, id = channelid, category_id = categoryid)
        await channel.delete()
        await message.channel.send("Channel Successfully Deleted!")  
  elif message.content.find("$purge") == 0:
    guild = message.guild
    channelID = 741683445973123132 #192319327838535691 
    if not message.author.guild_permissions.manage_messages: 
      await message.channel.send("You're not authorized!")
    else:
      if message.content[7:] == "help" or not message.content[7].isnumeric():
        await message.channel.send("Command to purge messages. Usage: ```$purge 20``` etc.")
      else:
        number = int(message.content[7:])
        if number > 100:
          number = 100
        messageList = await message.channel.history(limit=number).flatten()
        for n, i in enumerate(messageList):
          messageList[n] = str(i.author) + ": " + i.content
        messageList.reverse()
        messageLog = "\n".join(messageList)
        embed = discord.Embed(title = "Log")
        def purgecheck(m):
          return m.channel == message.channel
        await message.channel.purge(limit = number, check=purgecheck)
        if len("\n".join(messageLog)) > 1024:
          n,m = 0, 1018
          while len(messageLog) > 1024:
            content = "```" + messageLog[n:m] + "```"
            embed.add_field(name = "\u200b", value = content, inline=False)
            await discord.utils.get(guild.channels, id = channelID).send(embed=embed)
            embed.clear_fields()
            messageLog = messageLog[m:]
        else:
          embed.add_field(name = "\u200b", value = messageLog)
          await discord.utils.get(guild.channels, id = channelID).send(embed=embed)
        await message.channel.send(str(message.author) + " deleted " + str(number) + " messages.")

keep_alive()
token = os.environ.get("DISCORD_BOT_SECRET")
client.run(token)