import asyncio
import re

import discord
from discord.ext import commands
import asyncio

from discord.utils import get

free_nitro_regex = r'(FR)?\s?([GIF]+)?\s?DIS.+\s?NI'
from discord.ext.commands import UserConverter, UserNotFound

activity = discord.Game(name="Terminating rogue messages")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="terminator ", intents=intents, activity=activity, help_command=None)

with open("config.json","r") as f:
    config = json.load(f)


def unicode_escape(s):
    strs = []
    for char in s:
        if ord(char) > 127:
            strs.append(rf"\u{ord(char):04x}")
        else:
            strs.append(char)
    return "".join(strs)


@bot.command()
@commands.has_role("Admins")
async def terminate(ctx, arg: discord.Member):
    async for message in ctx.channel.history():
        if message.author == arg:
            await message.delete()
            await asyncio.sleep(1)
    await ctx.send(f"I have deleted all messages from {arg} in this channel")


@bot.command()
@commands.has_role("Admins")
async def terminateall(ctx, arg):
    fallback = False
    await ctx.send(f"Purging messages from {arg}")
    try:
        arg = await UserConverter().convert(ctx, argument=arg)
    except UserNotFound:
        print("User probably deleted, falling back on string comparison")
        fallback = True
        pass
    guild = ctx.channel.guild
    for channel in guild.channels:
        if type(channel) == discord.TextChannel:
            async for message in channel.history():
                print(f"Author: {message.author}, target: {arg}")
                if fallback:
                    if str(message.author) == arg:
                        await message.delete()
                        await asyncio.sleep(1)
                else:
                    if message.author == arg:
                        await message.delete()
                        await asyncio.sleep(1)
    await ctx.send(f"I have deleted all messages from {arg}")


@bot.command()
@commands.has_role("Admins")
async def removedeletedusermessages(ctx):
    async for message in ctx.channel.history():
        if str(message.author) == "Deleted User#0000":
            print("Removing message")
            await message.delete()
            await asyncio.sleep(1)


@bot.command()
async def getmessageauthors(ctx):
    async for message in ctx.channel.history():
        await ctx.send(f"Author is: {message.author}")
        await asyncio.sleep(1)


@bot.event
async def on_ready():
    for guild in bot.guilds:
        print(
            f'{bot.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'

        )


@bot.event
async def on_message(message):
    # print(repr(message.content))
    ascii_message = str(message.content.encode('ascii', 'ignore'))
    ascii_message.replace(" ", '')
    if type(message.channel) == discord.TextChannel:
        if re.search(free_nitro_regex, ascii_message, flags=re.IGNORECASE):
            print(ascii_message)
            print("Deleting potential nitro scam")
            bot.guilds[0].fetch_members()
            user = bot.guilds[0].get_member_named("gnations#5314")
            await user.send(f"I found a potential scam message with content: {unicode_escape(message.content)} and deleted it")
            await message.delete()
    await bot.process_commands(message)


@terminate.error
async def info_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("You are not authorized!")


bot.run(config.token)
