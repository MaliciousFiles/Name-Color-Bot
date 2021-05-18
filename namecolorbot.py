from discord.ext import commands
import discord
import random
from discord_slash import SlashCommand
import colorsys
from time import sleep
from threading import Thread
import asyncio

bot = commands.Bot(command_prefix=">", case_insensitive=True)
bot.remove_command("help")

slash = SlashCommand(bot, sync_commands=True)

guildIDs = []

COLORS = ["default", "red", "dark_red", "orange", "dark_orange", "gold", "dark_gold", "green", "dark_green", "teal", "dark_teal", "blue", "dark_blue", "blurple", "magenta", "dark_magenta", "purple", "dark_purple", "greyple", "lighter_gray", "light_gray", "darkple", "gray", "dark_gray", "darker_gray", "dark_theme", "random", "expanded_random", "rainbow"]
RAINBOW = ["red", "orange", "gold", "green", "blue", "purple"]

rainbow_threads = {}

@bot.event
async def on_ready():
    for guild in bot.guilds:
        guildIDs.append(guild.id)

@bot.event
async def on_guild_join(guild):
    guildIDs.append(guild.id)

@bot.event
async def on_guild_remove(guild):
    guildIDs.remove(guild.id)

def parse_color(color):
    rgb = None

    if color[0] == "#":
        color = color[1:]
        if len(color) != 6:
            return None

        try:
            rgb = tuple(int(color[i:i+2], 16) for i in range(0, 6, 2))
        except ValueError:
            return None
    elif color[:3] == "rgb":
        color = color[4:].replace(" ", "").replace(")", "")
        if len(color.split(",")) != 3:
            return None

        try:
            rgb = tuple(int(i) for i in color.split(","))
        except ValueError:
            return None
    else:
        color = color.replace(" ", "_")

        try:
            _locals = locals()
            exec(f"rgb = discord.Colour.{color}().to_rgb()", globals(), _locals)
            rgb = _locals["rgb"]
        except (AttributeError, SyntaxEror):
            return None

    return rgb

async def set_namecolor(ctx, color, rainbow_color=False):
    if not rainbow_color and ctx.author in rainbow_threads:
        rainbow_threads.pop(ctx.author).join()

    color = color.lower()
    if color == "help":
        await help(ctx)
        return

    role = discord.utils.get(ctx.guild.roles, name=ctx.author.name)

    try:
        color = COLORS[int(color)-1].replace("_", " ")
    except (ValueError, IndexError):
        pass

    display_color = ""

    if (color == "none"):
        await ctx.author.remove_roles(role)
        embed = discord.Embed(title="Success", description="Name color successfully removed!")
        await ctx.send(embed=embed)
        return
    elif (color == "random"):
        color_choices = COLORS.copy()
        color_choices.remove("random").remove("expanded_random")
        color = random.choice(color_choices)
        display_color = "Random: "
    elif (color == "expanded random"):
        color = f"rgb({random.randint(0, 255)}, {random.randint(0, 255)}, {random.randint(0, 255)})"
        display_color = "Expanded Random: "
    # elif (color == "rainbow"):
    #     _thread = Thread(target=start_rainbow, args=(ctx,))
    #     rainbow_threads[ctx.author] = _thread
    #     _thread.start()
    #
    #     if not rainbow_color:
    #         color = parse_color(random.choice(RAINBOW))
    #         embed = discord.Embed(title="Success", description="Name color successfully changed to **Rainbow**!", colour=discord.Colour.from_rgb(color[0], color[1], color[2]))
    #         await ctx.send(embed=embed)
    #
    #     return

    display_color += color.replace("_", " ").title().replace("Rgb", "rgb")

    parsed_color = parse_color(color)

    if parsed_color is None:
        if not rainbow_color:
            embed = discord.Embed(title="Failure", description=f"**{display_color}** is not a valid Hex Code, RGB tuple, or preset! Use `/namecolor help` or `>help` for help.", colour=discord.Colour.dark_red())
            await ctx.send(embed=embed)

        return

    disc_color = discord.Colour.from_rgb(parsed_color[0], parsed_color[1], parsed_color[2])

    if role is None:
        role = await ctx.guild.create_role(name=ctx.author.name, color=disc_color, mentionable=False)
        await role.edit(position=discord.utils.get(ctx.guild.roles, name=bot.user.name).position-1)
    else:
        await role.edit(colour=disc_color)

    await ctx.author.add_roles(role)

    if not rainbow_color:
        embed = discord.Embed(title="Success", description=f"Name color successfully changed to **{display_color}**!", colour=disc_color)
        await ctx.send(embed=embed)

@slash.slash(description="Pick your color using Hex [#ffffff], RGB [rgb(255, 255, 255)], or a Preset [white]", guild_ids=guildIDs)
async def namecolor(ctx, color):
    await set_namecolor(ctx, color)

@bot.command(name="namecolor")
async def namecolor_bot(ctx, color):
    await set_namecolor(ctx, color)

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="NameColor Help", description="""
    ***Commands*** | Prefix is `>`, or slash command

    **namecolor <color>**: *Sets your name color to **<color>**, which can be a Hex [#ffffff], RGB [rgb(255, 255, 255)], or a Preset [white]. `None` to clear.*

    ------------------------------------------------------------

    ***Presets***

    >>> 1. Default
    2. Red
    3. Dark Red
    4. Orange
    5. Dark Orange
    6. Gold
    7. Dark Gold
    8. Green
    9. Dark Green
    10. Teal
    11. Dark Teal
    12. Blue
    13. Dark Blue
    14. Blurple
    15. Magenta
    16. Dark Magenta
    17. Purple
    18. Dark Purple
    19. Greyple
    20. Lighter Gray / Grey
    21. Light Gray / Grey
    22. Gray / Grey
    23. Dark Gray / Grey
    24. Darker Gray / Grey
    25. Dark Theme
    26. Random
    27. Expanded Random
    28. ~~Rainbow~~ **OUT OF COMMISSION**
    """, colour=discord.Colour.green())
    await ctx.send(embed=embed)

bot.run("TOKEN")
