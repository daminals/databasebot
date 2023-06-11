# bot.py
# Daniel Kogan

from discord.ext import commands
from dotenv import load_dotenv
import discord, os


intents = discord.Intents.all()
load_dotenv()
TOKEN = os.environ.get('TOKEN', 3)
DBLINK = os.environ.get('DBLINK', 3)

import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("leaderboard-key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': DBLINK,
})

bot = commands.Bot(command_prefix="m-", intents=intents)

# get the data
data = db.reference("/")

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    # loop through every guild and create a new key for it
    # only run once if necessary
    # for guild in bot.guilds:
    #     # loop through every member and create a new key for it
    #     member_object = {}
    #     for member in guild.members:
    #       member_object[member.id] = 0
    #     data.child(str(guild.id)).set(member_object)

# on guild join, create a new key for it
@bot.event
async def on_guild_join(guild):
    # loop through every member and create a new key for it
    member_object = {}
    for member in guild.members:
      member_object[member.id] = 0
    data.child(str(guild.id)).set(member_object)

@bot.command()
async def ping(ctx):
    await ctx.send("pong")
    
# on message increase count by 1
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    # get the guild id
    guild_id = str(message.guild.id)
    # get the member id
    member_id = str(message.author.id)
    # check if member object exists
    if data.child(guild_id).child(member_id).get() == None:
        # create a new member object
        data.child(guild_id).child(member_id).set(0)
    # get the member object
    member_object = data.child(guild_id).child(member_id).get()
    # increase the count by 1
    member_object += 1
    # update the count
    data.child(guild_id).child(member_id).set(member_object)
    await bot.process_commands(message)    
    
# create a leaderboard command
@bot.command()
async def leaderboard(ctx):
    # get leaderboard data
    leaderboard_data = data.child(str(ctx.guild.id)).get()
    # sort the leaderboard data
    leaderboard_data = dict(sorted(leaderboard_data.items(), key=lambda item: item[1], reverse=True))
        
    embed = discord.Embed(title="Leaderboard", color=discord.Color.blue())
    embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/5987/5987898.png")

    # limit the leaderboard to 10 entries
    count = 0
    # Add fields to the embed for each leaderboard entry
    for index, entry in enumerate(leaderboard_data, start=1):
      count += 1
      # get the name of the member
      name = bot.get_user(int(entry)).name
      # get the score of the member
      score = leaderboard_data[entry]
      # add the field to the embed
      embed.add_field(name=f"#{index} - {name}", value=fscore, inline=False)
      if count == 10:
        break

    await ctx.send(embed=embed)

# create a command that shows the user's score in the leaderboard
@bot.command()
async def me(ctx):
    # get the guild id
    guild_id = str(ctx.guild.id)
    # get the member id
    member_id = str(ctx.author.id)
    # check if member object exists
    if data.child(guild_id).child(member_id).get() == None:
        # create a new member object
        data.child(guild_id).child(member_id).set(0)
    # get the member object
    member_object = data.child(guild_id).child(member_id).get()
    # get members name
    name = bot.get_user(int(member_id)).name
    # create the embed
    embed = discord.Embed(title=name, color=discord.Color.blue())
    # embed icon
    embed.set_thumbnail(url=ctx.author.avatar_url)
    # embed score
    embed.add_field(name=member_object, value="", inline=False)
    await ctx.send(embed=embed)

bot.run(TOKEN)