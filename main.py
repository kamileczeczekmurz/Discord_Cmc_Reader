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


@bot.command()
async def sol(ctx, amount: float = 1.0):
    try:
        prices = get_crypto_prices()
        if not prices or "SOL" not in prices:
            await ctx.send("Error: Failed to fetch current SOL price")
            return

        sol_usd_price = prices["SOL"]["price"]

        response = requests.get("https://api.nbp.pl/api/exchangerates/rates/a/usd/")
        usd_pln_rate = response.json()["rates"][0]["mid"]

        usd_value = amount * sol_usd_price
        pln_value = usd_value * usd_pln_rate

        response_msg = (
            f"SOL Conversion:\n"
            f"Amount: {amount} SOL\n"
            f"Value: {usd_value:.2f} USD\n"
            f"Value: {pln_value:.2f} PLN\n"
            f"Current rates:\n"
            f"1 SOL = {sol_usd_price:.2f} USD\n"
            f"1 USD = {usd_pln_rate:.4f} PLN"
        )
        await ctx.send(f"```\n{response_msg}\n```")

    except requests.RequestException:
        await ctx.send("Error: Failed to connect to exchange rate API")
    except Exception as e:
        await ctx.send("An unexpected error occurred")
        print(f"SOL conversion error: {e}")


@bot.command()
async def commands(ctx):
    help_embed = discord.Embed(
        title="Available Commands",
        description="List of all bot commands and their usage",
        color=discord.Color.blue()
    )

    help_embed.add_field(
        name="General",
        value=(
            "`/commands` - Shows this help message\n"
            "`/witam` - Basic greeting command\n"
            "`/dm` - Sends a private message\n"
            "`/tescik` - Test command (requires Tester role)"
        ),
        inline=False
    )

    help_embed.add_field(
        name="Cryptocurrency",
        value=(
            "`/crypto` - Shows prices of BTC, ETH, SOL\n"
            "`/bitcoin` - Shows current Bitcoin price\n"
            "`/sol [amount]` - Converts SOL to USD/PLN"
        ),
        inline=False
    )

    help_embed.add_field(
        name="Moderation",
        value=(
            "`/assign @user` - Assigns Tester role\n"
            "`/remove @user` - Removes Tester role"
        ),
        inline=False
    )
    help_embed.set_footer(text=f"Requested by {ctx.author.name}")
    await ctx.send(embed=help_embed)




bot.run(token, log_handler=handler, log_level=logging.DEBUG
