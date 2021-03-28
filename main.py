import discord
import sys
import traceback as trace
import os
import asyncio
import json
import requests
import math
import sqlite3
from keep_alive import keep_alive


intents = discord.Intents.all()
client = discord.Client(intents = intents)
global guild
guild = discord.utils.get(client.guilds, id = 825074522130219028)
global purgeChannelID
purgeChannelID = 825124293230329936

''' async def UpdateTables():
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
  # =============================Writing Table Starts Here========================
  writingChannel = discord.utils.get(guild.channels, id = 771807764367671357)
  with open("writingScoreBackup.json", "r") as writing:
    writingData = json.load(writing)
  async for message in writingChannel.history(limit = 6):
    if message.author == client.user:
      await message.delete()
    
  writingTableData = {writingData[i]["Username"]:(str(writingData[i]["Score"]), str(writingData[i]["noParticipated"])) for i in writingData.keys()}
  writingSortData = []
  for key, value in sorted(writingTableData.items(), key = lambda item: int(item[1][0]), reverse = True):
    writingSortData.append((key,value))
    
  maxLenScore = len(str(writingSortData[0][1][0])) + 2
  maxLenWritingName = len(max(writingTableData.keys(), key = len)) + 2
  maxLenParticipated = len(" No. of Participations ")
  writingTable = "╔"+"═"*maxLenSNo+"╦" + "═"*maxLenWritingName + "╤" + "═"*maxLenScore +"╤" +"═"*maxLenParticipated+"╗\n║ S.No ║ Name"+" "*(maxLenWritingName-5)+"│ Score"+" "*(maxLenScore-6)+ "│ No. of Participations ║\n╠"+"═"*maxLenSNo+"╬"+"═"*maxLenWritingName+"╪"+"═"*maxLenScore+"╪"+"═"*maxLenParticipated+"╣\n"
  writingRowLen = len(writingTable)
 
  for i, x in enumerate(writingSortData):
    nameSpaceLen = (maxLenWritingName - len(x[0]))
    scoreSpaceLen = (maxLenScore - len(x[1][0]))
    participatedSpaceLen = (maxLenParticipated - len(x[1][1]))
    if len(writingTable)+writingRowLen*2<2000:
      writingTable += "║ " + str(i) + " "*(maxLenSNo-1-len(str(i+1)))+"║" + " "*int((nameSpaceLen/2)) + x[0] + " "*int((nameSpaceLen/2)+nameSpaceLen%2) + "│" + " "*math.ceil(scoreSpaceLen/2) + str(x[1][0]) + " "*int((scoreSpaceLen/2)) +"| "+ x[1][1] +" "*(participatedSpaceLen-1)+"║\n"
      
    if i+1 < len(writingSortData) and len(writingTable)+rowlen*3 < 2000:
      writingTable += "╟"+"─"*maxLenSNo+"╫" + "─"*maxLenWritingName + "┼"+ "─"*maxLenScore + "┼"+"─"*maxLenParticipated+"╢\n"
    elif i+1 > len(writingSortData) or len(writingTable)+rowlen*3>2000:
      writingTable += "╚"+"═"*maxLenSNo+"╩" + "═"*maxLenWritingName + "╧" + "═"*maxLenScore + "╧"+"═"*maxLenParticipated+"╝"
      if len(writingTable)+rowlen*3>2000:
        await writingChannel.send("```"+writingTable+"```")
      if i+1 > len(writingSortData):
        break
      else:
        writingTable ="╔"+"═"*maxLenSNo+"╦" + "═"*maxLenWritingName + "╤" + "═"*maxLenScore +"╤" + "╤"+"═"*maxLenParticipated+"╗\n"
  writingTable += "╚"+"═"*maxLenSNo+"╩" + "═"*maxLenWritingName + "╧" + "═"*maxLenScore + "╧"+"═"*maxLenParticipated+"╝"   
  await writingChannel.send("```"+writingTable+"```")
 '''

async def Trade(operation, **kwargs):
  conn = sqlite3.connect('Trade.db')
  c = conn.cursor()
  
  conn.close() 

@client.event
async def on_ready():
  print("I'm in!")
  print(client.user)
  # hoursSinceUp = 0
  ''' while True:
    with open("chardatabackup.json", "w") as backup:
      url = "https://api.jsonbin.io/b/5f43fa5c514ec5112d0d5309/latest/"
      headers = {"secret-key" : "$2b$10$ZQTgjlmx9ABoAWGW.Y06TuFeJvd4YzZomB7T8QRyWWLAG.eEudPNK"}
      req = requests.get(url=url, headers = headers)
      data = json.loads(req.text)
      json.dump(data, backup)
    # if hoursSinceUp%24 == 0:
      # await UpdateTables()
     await asyncio.sleep(3600)
    hoursSinceUp += 1 '''

@client.event
async def on_error(event, ctx):
  #guild = discord.utils.get(client.guilds, id = 686858403569860643)
  tbfile = open("traceback.txt", "w")
  tbfile.write("")
  tbfile = open("traceback.txt", "r+")
  trace.print_exc(file = tbfile)
  tbfile.seek(0)
  output = tbfile.read()
  embed = discord.Embed(title = "Error!", description = "An error has occurred. Please contact the Bot Mechanic(Shivraj#3373) and point them towards this message.", color = 0xff0000)
  embed.add_field(name="Traceback", value="```" + output + "```", inline=False)
  if event == "on_member_join":
    channel = discord.utils.get(guild.channels, id = 825229116282372117)
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
  channel = discord.utils.get(guild.channels, id = 825124293230329936)
  await channel.send(embed=embed)

'''@client.event
async def on_member_join(member):
  guild = discord.utils.get(client.guilds, id = 686858403569860643)
  await member.edit(roles = [discord.utils.get(guild.roles, id = 740225928529182801)]);
  welcome = "Greetings, " + member.mention + "." + " Welcome to Edenfell. Please start by reading our rules: " + discord.utils.get(guild.channels, id = 825123180955041873).mention + ". Once you have familiarized yourself with the rules, please post a snippet of original creative writing/RP of no less than 200 words in " + discord.utils.get(guild.channels, id=825074522130219030).mention + "."
  embed = discord.Embed(title = "Welcome!", description = welcome)
  channel = discord.utils.get(guild.channels, id = 825124262478086164)
  embed.set_image(url="https://i.imgur.com/IXHUtNM.gif")
  await channel.send(member.mention)
  await channel.send(embed = embed) '''


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
  elif message.content.find("$purge") == 0:
    guild = message.guild
    channelID = purgeChannelID 
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
  elif message.content.find("$trade") == 0:
    guild = message.guild
    author = message.author
    
  ''' elif message.content.find("$wxp") == 0:
    guild = message.guild
    if message.content[5:9] == "help":
      await message.channel.send("Mention the User, then enter their score (out of 10). \n Eg: \n ```$wxp @Shivraj 8```")
    else:
      userID = message.content[5:-2]
      user = guild.get_member(int(userID.strip("<@!>")))
      username = user.name
      score = int(message.content[-1])*100
      parameters = {"userID" : userID, "Username" : username, "Score" : score, "noParticipated" : 0}
      with open("writingScoreBackup.json", "r") as backup:
        data = json.load(backup)
      if userID not in data.keys():
        data[userID] = parameters
      else:
        data[userID]["Score"] += score
      data[userID]["noParticipated"] += 1
      with open("writingScoreBackup.json", "w") as datasheet:
        json.dump(data, datasheet)
      await message.channel.send("Score has been updated!")
      await UpdateTables() '''



keep_alive()
token = os.environ.get("DISCORD_BOT_SECRET")
client.run(token)