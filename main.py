import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import asyncio
import requests





from crypto_api import get_crypto_prices

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8',mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

test_role = 'Tester'

@bot.event
async def on_ready():
    print(f' {bot.user.name} Is running.')

@bot.event
async  def on_member_join(member):
        channel = bot.get_channel(1373400703661375571)
        if channel:
            await channel.send(f'{member.mention} Wszedl na serwer')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if 'test' in message.content.lower():
        await asyncio.sleep(1)
        await message.delete()
        await message.channel.send(f'{message.author.mention} Test accepted')


    await bot.process_commands(message)

@bot.command()
async def Witam(ctx):
    await ctx.send(f"Hello {ctx.author.mention}")

@bot.command()
async def assign(ctx, member: discord.Member):
    role = discord.utils.get(ctx.guild.roles, name=test_role)
    if role:
        await member.add_roles(role)
        await ctx.send(f'Role assigned to {member.mention}')
    else:
        await ctx.send(f'Role doesnt exist')


@bot.command()
async def remove(ctx, member: discord.Member = None):
    if not member:
        await ctx.send('Please specify a member')
        return

    role = discord.utils.get(ctx.guild.roles, name=test_role)
    if not role:
        await ctx.send(f"Role doesn't exist")
        return

    if role not in member.roles:
        await ctx.send(f"{member.mention} doesn't have the required role")
        return

    await member.remove_roles(role)
    await ctx.send(f"Role removed from {member.mention}")


@bot.command()
@commands.has_role(test_role)
async def tescik(ctx):
    await ctx.send(f"Hello {ctx.author.mention}")

@tescik.error
async def tescik_error(ctx, error):
    await ctx.send(f"Something went wrong. {error}")


@bot.command()
async def dm(ctx):
    await ctx.author.send(f"PDW")



@bot.command()
async def crypto(ctx):
    prices = get_crypto_prices()
    if prices:
        for symbol, info in prices.items():
            await ctx.send(f"{info['name']} ({symbol}): ${info['price']:.2f}")
    else:
        await ctx.send("Error")


@bot.command()
async def Bitcoin(ctx):
    prices = get_crypto_prices()
    if prices and "BTC" in prices:
        info = prices["BTC"]
        await ctx.send(f"Bitcoin: ${info['price']:.2f}")




bot.run(token, log_handler=handler, log_level=logging.DEBUG)