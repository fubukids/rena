import discord

CYAN = discord.Color.teal()  # close to cyan
FOOTER_TEXT = "weiz"

def make_embed(title: str=None, description: str=None, color: discord.Color=CYAN):
    e = discord.Embed(title=title or discord.Embed.Empty, description=description or discord.Embed.Empty, color=color)
    e.set_footer(text=FOOTER_TEXT)
    return e
