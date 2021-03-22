import discord
import random

WRONG_USAGE = "Something went wrong"
HELP_USAGE = "Please see `!!help` for further information"
HOWTO_URL = "https://github.com/erwanvivien/discord_OverCRI"
ICON_URL = "https://raw.githubusercontent.com/erwanvivien/discord-eGLD/main/imgs/goldr-icon.png"

BOT_COLOR = discord.Colour(0xFBDC1B)
ERROR_COLOR = discord.Colour(0xff0000)
WARN_COLOR = discord.Colour(0xebdb34)
VALID_COLOR = discord.Colour(0x55da50)

REPORT_CHANN_ID = 819550515347456061

HELP_EMBED = discord.Embed(title="Help", url="https://github.com/erwanvivien/discord_OverCRI",
                           description="**How to use the bot:**")

HELP_EMBED.add_field(name="• Groups",
                     value="- [`!!groups`](https://github.com/erwanvivien/discord_OverCRI#groups): Gets a random person from specified group", inline=False)
HELP_EMBED.add_field(name="• People",
                     value='''- [`!!login <login>`](https://github.com/erwanvivien/discord_OverCRI#people): Gets a person from exact login
- [`!!random`](https://github.com/erwanvivien/discord_OverCRI#people): Gets a random person from all groups
- [`!!firstname [lastname]`](https://github.com/erwanvivien/discord_OverCRI#people): Gets a person matching the best from both input, of course if you specify the lastname it has way better results''', inline=False)
HELP_EMBED.add_field(name="• Mappings", value='''- [`!!map <mapping-name>`](https://github.com/erwanvivien/discord_OverCRI#mappings): It maps the file sent to the mapping-name. ⚠️ This needs an attached file
- [`!!define <mapping-name> any desc ...`](https://github.com/erwanvivien/discord_OverCRI#mappings): It adds a description to the said mapping
- [`!!mappings`](https://github.com/erwanvivien/discord_OverCRI#mappings): Displays all mappings
- [`!!<mapping-name>`](https://github.com/erwanvivien/discord_OverCRI#mappings): Sends back the file mapped''', inline=False)
HELP_EMBED.add_field(
    name="• Help", value="- [`!!help`](https://github.com/erwanvivien/discord_OverCRI#help): Displays this message", inline=False)


def author_name(author, discriminator=True):
    # Get nick from msg author (discord) if exists
    if not discriminator:
        return author.display_name
    return f"{author.name}#{author.discriminator}"


def create_embed(title, desc, colour=BOT_COLOR, url=HOWTO_URL, icon_url="", footer_url=ICON_URL, footer_text="Goldr"):
    embed = discord.Embed(title=title,
                          description=desc,
                          colour=colour,
                          url=url)

    if icon_url:
        embed.set_thumbnail(url=icon_url)
    if footer_url or footer_text:
        embed.set_footer(text=footer_text, icon_url=footer_url)

    return embed


async def error_message(message, title=WRONG_USAGE, desc=HELP_USAGE, url=HOWTO_URL,
                        icon_url="", footer_url=ICON_URL, footer_text="OverCRI"):
    # Sends error message to discord (red)
    return await message.channel.send(embed=create_embed(title, desc, ERROR_COLOR, url, icon_url, footer_url, footer_text))


async def send_message(message, title=WRONG_USAGE, desc=HELP_USAGE, url=HOWTO_URL,
                       icon_url="", footer_url=ICON_URL, footer_text="OverCRI"):
    # Sends message to discord (bot_color)
    return await message.channel.send(embed=create_embed(title, desc, BOT_COLOR, url, icon_url, footer_url, footer_text))


async def send_file(message, filename, content=""):
    # Sends message to discord (bot_color)
    return await message.channel.send(content, file=discord.File(filename))


async def edit_message(message, title=WRONG_USAGE, desc=HELP_USAGE, url=HOWTO_URL,
                       icon_url="", footer_url=ICON_URL, footer_text="OverCRI"):
    # Sends message to discord (bot_color)
    return await message.edit(embed=create_embed(title, desc, BOT_COLOR, url, icon_url, footer_url, footer_text))


async def report(client, title, desc):
    report_channel = client.get_channel(REPORT_CHANN_ID)
    embed = create_embed(
        title, f"Reported message was :\n```{desc}```")
    await report_channel.send("<@289145021922279425>\n", embed=embed)
