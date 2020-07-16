import discord
import sys
import traceback as trace
import os
import json
import math
from keep_alive import keep_alive

client = discord.Client()

@client.event
async def on_ready():
  print("I'm in!")
  print(client.user)

@client.event
async def on_error(on_message, ctx):
  tbfile = open("traceback.txt", "w")
  tbfile.write("")
  tbfile = open("traceback.txt", "r+")
  trace.print_exc(file = tbfile)
  tbfile.seek(0)
  output = tbfile.read()
  embed = discord.Embed(title = "Error!", description = "An error has occurred. Please contact the Bot Mechanic(Shivraj#3373) and point them towards this message.", color = 0xff0000)
  embed.add_field(name="Traceback", value="```" + output + "```", inline=False)
  await ctx.channel.send(embed=embed)

@client.event
async def on_message(message):
  if message.author == client.user:
    return
  if message.content.find("$reverse") != -1:
    await message.channel.send(message.content[-1:8:-1])
  if message.content.find("$help") != -1:
    embed = discord.Embed(title="Help", description="All commands are listed here, but for the usage of each, type the command and then type help in front of the command. Eg- $char help.", color=0x00ffff)
    embed.add_field(name="$newchar",value="Adds a new Character to the database. Mod Only Command.",inline=True)
    embed.add_field(name="$char",value="Shows the Character's Card",inline=True)
    embed.add_field(name="$modchar",value="Modifies the Character's data. Mod Only Command.",inline=True)
    embed.add_field(name="$xp",value="Shows all the Characters and their XP in table form.",inline=True)
    embed.add_field(name="$approval",value="Creates an Approval Channel. Mod Only Command.",inline=True)
    embed.add_field(name="$remove",value="Removes an Approval Channel. Mod Only Command.",inline=True)
    embed.add_field(name="$reverse",value="Reverses whatever message is written after the command.",inline=True)  
    await message.channel.send(embed=embed)
  if message.content.find("$newchar") != -1: #Making Character Entry into JSON file
    guild = message.guild
    if message.author.roles[-1] < guild.get_role(691276640629686334):
      await message.channel.send("You are not permitted to create a Character in the Database! Please contact a Staff Member.")
    else:
      if message.content[9:13] == "help":
        await message.channel.send("Enter Character Details in the format: Username(Mention)|Name|Description|XP|Rank|Alignment(Hero, Villain or Rogue)|Money|Items|StatImage(URL)|Stats(Power, Speed, Intelligence, Technique, Skillfulness). Manually default to 0 for blank.")
      else:
        template1 = ["UserID", "Name", "Description", "XP", "Rank", "Alignment", "Money", "Items", "StatImage", "Stats"]
        Parameters = []
        for i in template1:
          await message.channel.send("Enter %s:" % i)
          
          def check(m):
              return m.author == message.author and m.channel == message.channel
          try:
            reply = await client.wait_for('message', timeout = 50.0, check = check)
          except asyncio.TimeoutError:
              await message.channel.send("Timed out! Try again.")
          else:
              Parameters.append("{.content}".format(reply))
        print(Parameters)
        #  template2 = ["Power", "Speed", "Intelligence", "Technique", "Skillfulness"]
        #  defaults = ["Undefined", "Undefined", "\u200b", "0", "D", "Undefined", "0", "\u200b", "https://i.imgur.com/xUWfFdw.png", "Stats"]
        #  for i, e in enumerate(x):
        #   if e == "0":
        #      x[i] = defaults[i]
        #  x[9] = {template2[i]:x[9].strip("()").replace(" ", "").split(",")[i] for i in range(0, len(x[9].strip("()").replace(" ", "").split(",")))}
        
        #  chardetails = {template1[i]:x[i] for i in range(1, len(x))}

        #  await message.channel.send(str(chardetails))
        #  with open("chardata.json", "r") as datasheet:
        #    data = json.load(datasheet)
        #  data[str(client.get_user(int(x[0].strip("<@!>"))))] = chardetails
        #  with open("chardata.json", "w") as datasheet:
        #    json.dump(data, datasheet)
  if message.content.find("$char") != -1:
    if message.content[6:10] == "help":
      await message.channel.send("Mention the user next to the command.")
    else:
      user = message.content[6:]
      if user[0] != "<" and user[-1] != ">":
        await message.channel.send("Please enter a valid user!")
      else:
        user = str(client.get_user(int(user.strip("<@!>"))))
        with open("chardata.json", "r") as datasheet:
          data = json.load(datasheet)
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
  if message.content.find("$modchar") != -1:
    guild = message.guild
    if message.author.roles[-1] < guild.get_role(691276640629686334):
      await message.channel.send("You are not permitted to modify characters! Please contact a Staff Member.")
    else:
      if message.content[9:13] == "help":
        await message.channel.send("Mention the user, list the entry to be change, then new value: as such -> MENTION|ENTRY(Anything from Name, Description, XP, Rank, Alignment, Money, Items, StatImage, Stats[Only one from Power, Speed, Intelligence, Technique, Skillfulness]|NEW VALUE. \n Ex. $modchar @ABC|Stats[Power]|2")
      else:
        x = message.content[10:].split("|")
        user = str(client.get_user(int(x[0].strip("<@!>"))))
        with open("chardata.json", "r") as datasheet:
          data = json.load(datasheet)
        entry = x[1]
        value = x[2]
        print(value)
        if "[" in entry:
          entry = entry.strip("]").split("[")
          data[user][entry[0]][entry[1]] = value
        else:
          data[user][entry] = value
        with open("chardata.json", "w") as datasheet:
          json.dump(data, datasheet)
        await message.channel.send("Done!")
        await message.channel.send(x[1] + " has been changed to " + str(x[2]))
  if message.content.find("$xp") != -1:
    if message.content[4:8] == "help":
      await message.channel.send("Enter one of the following next to the commands: All, Hero, Villain, Rogue.")
    else:
      category = message.content[4:].lower()
      category = category[0].upper() + category[1:]
      with open("chardata.json", "r") as datasheet:
        data = json.load(datasheet)
      if category == "All":
        tabledata = {data[i]["Name"]:(data[i]["XP"], data[i]["Alignment"], data[i]["Rank"]) for i in data.keys()}
      else:
        tabledata = {data[i]["Name"]:(data[i]["XP"], data[i]["Alignment"], data[i]["Rank"]) for i in data.keys() if data[i]["Alignment"] == category}
      sortdata = []
      for key, value in sorted(tabledata.items(), key = lambda item: item[1][0], reverse = True):
        sortdata.append((key, value))
      xpval = []
      for i in tabledata.values():
        xpval.append(i[0])
      maxlenname = len(max(tabledata.keys(), key=len)) + 2
      maxlenxp = len(max(xpval, key=len)) + 2
      print(tabledata.items())
      maxlenalign = len(" Alignment ")
      table = "╔══════╦" + "═"*maxlenname + "╤" + "═"*maxlenxp +"╤" + "═"*maxlenalign + "╤══════╗\n║ S.No ║ Name"+" "*(maxlenname-5)+"│ XP"+" "*(maxlenxp-3)+ "│ Alignment │ Rank ║\n╠══════╬"+"═"*maxlenname+"╪"+"═"*maxlenxp+"╪═══════════╪══════╣\n"
      for i, x in enumerate(sortdata):
        table += "║ " + str(i+1) + "    ║" + " "*int(((maxlenname - len(x[0]))/2)) + x[0] + " "*int(((maxlenname - len(x[0]))/2)) + "│" + " "*math.ceil((maxlenxp - len(x[1][0]))/2) + str(x[1][0]) + " "*int(((maxlenxp - len(x[1][0]))/2)) +"| "+ x[1][1] +" "*(maxlenalign-len(x[1][1])-1)+ "│ " + x[1][2] + "    ║\n"

        print(math.ceil((maxlenxp - len(x[1][0]))/2))
        if i+1 < len(sortdata):
          table += "╟──────╫" + "─"*maxlenname + "┼"+ "─"*maxlenxp + "┼"+ "─"*maxlenalign +"┼──────╢\n"
        else:
          table += "╚══════╩" + "═"*maxlenname + "╧" + "═"*maxlenxp + "╧" + "═"*maxlenalign + "╧══════╝"
      await message.channel.send("```" + table + "```")
  if message.content.find("$approval") != -1:
    guild = message.guild
    if message.author.roles[-1] < guild.get_role(691276640629686334):
      await message.channel.send("You are not permitted to create a channel! Please contact a Staff Member.")
    else:
      if message.content[10:14] == "help":
        await message.channel.send("Mention the user who you're creating this channel for next to the command.")
      else:
        user = message.content[11:].strip("<@!>")
        staff = 691276640629686334
        category = discord.utils.get(guild.categories, id = 691295206682918992)
        name = str(client.get_user(int(user)))[:-5]
        overwrites = {
          guild.default_role:discord.PermissionOverwrite(read_messages = False, send_messages = False),
          guild.get_member(int(user)):discord.PermissionOverwrite(read_messages = True, send_messages = True),
          guild.get_role(staff):discord.PermissionOverwrite(read_messages = True, send_messages = True)
        }
        channel = await guild.create_text_channel(name, overwrites = overwrites, category=category)
  if message.content.find("$remove") != -1:
    guild = message.guild
    if message.author.roles[-1] < guild.get_role(691276640629686334):
      await message.channel.send("You are not permitted to delete a channel! Please contact a Staff Member.")
    else:
      if message.content[8:12] == "help":
        await message.channel.send("Link the channel to be deleted as such: #channelname, next to the command.")
      else:
        channelid = int(message.content[9:].strip("<@!>#"))
        categoryid = 691295206682918992
        channel = discord.utils.get(guild.channels, id = channelid, category_id = categoryid)
        await channel.delete()
        await message.channel.send("Channel Successfully Deleted!")    

keep_alive()
token = os.environ.get("DISCORD_BOT_SECRET")
client.run(token)