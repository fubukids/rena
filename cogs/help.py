import discord
from discord import app_commands
from discord.ext import commands
from utils.embed_utils import make_embed, CYAN
from emojis import EMOJI

HELP_SECTIONS = {
    "General": [
        "/kick", "/ban", "/timeout", "/warn", "/unban", "/addrole", "/moverole", "/movetimeout"
    ],
    "Automod": [
        "/enableautomod", "/setbadword", "/addlinkblacklist", "/setlimitwarn"
    ],
    "Logs": [
        "/setlogchannel"
    ],
    "Utility": [
        "/setwelcomechannel", "/setbooster", "/addemoji", "/dmuser", "/embedmaker", "/autopost", "/removeautopost"
    ],
    "RoleSettings": [
        "/deleterole", "/createrolereaction", "/autorolewelcome"
    ]
}

class HelpDropdown(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label=k, description=f"Lihat perintah {k}") for k in HELP_SECTIONS.keys()]
        super().__init__(placeholder="Pilih kategori bantuan…", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        section = self.values[0]
        cmds = "\n".join(f"{EMOJI.get('spark','✨')} `{c}`" for c in HELP_SECTIONS[section])
        e = make_embed(title=f"{EMOJI.get('gear','⚙️')} Bantuan: {section}", description=cmds, color=CYAN)
        await interaction.response.edit_message(embed=e, view=self.view)

class HelpView(discord.ui.View):
    def __init__(self, timeout=180):
        super().__init__(timeout=timeout)
        self.add_item(HelpDropdown())

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Tampilkan bantuan dengan dropdown")
    async def help(self, interaction: discord.Interaction):
        e = make_embed(title=f"{EMOJI.get('eyes','👀')} Bantuan", description="Pilih kategori di bawah ini.", color=CYAN)
        await interaction.response.send_message(embed=e, view=HelpView(), ephemeral=True)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))
