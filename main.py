import asyncio
import discord
from discord.ext import commands
from config import TOKEN
from utils.embed_utils import CYAN
from emojis import EMOJI

INTENTS = discord.Intents.default()
INTENTS.members = True
INTENTS.message_content = True
INTENTS.guilds = True
INTENTS.reactions = True

class WeizBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            intents=INTENTS,
            application_id=None
        )

    async def setup_hook(self):
        # Load cogs
        for ext in ("cogs.help","cogs.general","cogs.automod","cogs.logs","cogs.utility","cogs.roles"):
            await self.load_extension(ext)
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            print(f"Synced {len(synced)} commands.")
        except Exception as e:
            print("Sync error:", e)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        # Activity: "watching moderation"
        activity = discord.Activity(type=discord.ActivityType.watching, name="moderation")
        await self.change_presence(activity=activity, status=discord.Status.online)

bot = WeizBot()

# Simple ping to confirm
@bot.tree.command(name="ping", description="Cek latensi")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(bot.latency*1000)}ms")

if __name__ == "__main__":
    if not TOKEN or TOKEN.startswith("PASTE_"):
        raise SystemExit("Harap isi TOKEN di config.py terlebih dahulu.")
    bot.run(TOKEN)
