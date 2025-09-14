import re, time
import discord
from discord import app_commands
from discord.ext import commands
from utils.embed_utils import make_embed, CYAN
from utils import storage
from emojis import EMOJI

DEFAULT_BADWORDS = [
    # Indo
    "anjing","bangsat","babi","kontol","memek","goblok","tolol","kampret","bodoh","tai","jingan",
    # EN
    "fuck","bitch","bastard","asshole","dick","pussy","cunt","moron","stupid","idiot"
]

class AutomodCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="enableautomod", description="Hidupkan/Matikan automod untuk server ini")
    @app_commands.describe(enabled="True untuk hidupkan, False untuk matikan")
    @app_commands.default_permissions(manage_guild=True)
    async def enableautomod(self, interaction: discord.Interaction, enabled: bool):
        data = storage.get("automod")
        gid = str(interaction.guild.id)
        entry = data.get(gid, {"enabled": False, "badwords": DEFAULT_BADWORDS, "link_blacklist": [], "warn_limits":{"mute":2,"timeout":3,"kick":5,"ban":7}})
        entry["enabled"] = enabled
        data[gid] = entry
        storage.set("automod", data)
        await interaction.response.send_message(embed=make_embed(title=f"{EMOJI['shield']} Automod", description=f"Automod **{'ON' if enabled else 'OFF'}**"))

    @app_commands.command(name="setbadword", description="Set daftar kata kasar (kosongkan untuk default)")
    @app_commands.default_permissions(manage_guild=True)
    async def setbadword(self, interaction: discord.Interaction, words: str=None):
        data = storage.get("automod")
        gid = str(interaction.guild.id)
        entry = data.get(gid, {"enabled": True, "badwords": DEFAULT_BADWORDS, "link_blacklist": [], "warn_limits":{"mute":2,"timeout":3,"kick":5,"ban":7}})
        if words:
            custom = [w.strip().lower() for w in words.split(",") if w.strip()]
            entry["badwords"] = list(dict.fromkeys(custom))
        else:
            entry["badwords"] = DEFAULT_BADWORDS
        data[gid] = entry
        storage.set("automod", data)
        await interaction.response.send_message(embed=make_embed(title=f"{EMOJI['gear']} Badwords", description=f"Total kata: **{len(entry['badwords'])}**"))

    @app_commands.command(name="addlinkblacklist", description="Tambah link ke blacklist antispam (pisahkan koma)")
    @app_commands.default_permissions(manage_guild=True)
    async def addlinkblacklist(self, interaction: discord.Interaction, links: str):
        data = storage.get("automod")
        gid = str(interaction.guild.id)
        entry = data.get(gid, {"enabled": True, "badwords": DEFAULT_BADWORDS, "link_blacklist": [], "warn_limits":{"mute":2,"timeout":3,"kick":5,"ban":7}})
        for url in [u.strip().lower() for u in links.split(",") if u.strip()]:
            if url not in entry["link_blacklist"]:
                entry["link_blacklist"].append(url)
        data[gid] = entry
        storage.set("automod", data)
        await interaction.response.send_message(embed=make_embed(title=f"{EMOJI['link']} Blacklist", description=f"Blacklist sekarang: {', '.join(entry['link_blacklist']) or '-'}"))

    @app_commands.command(name="setlimitwarn", description="Atur level tindakan otomatis berdasarkan jumlah warn")
    @app_commands.describe(mute="Jumlah warn untuk mute (0=disable)", timeout="warn untuk timeout", kick="warn untuk kick", ban="warn untuk ban")
    @app_commands.default_permissions(manage_guild=True)
    async def setlimitwarn(self, interaction: discord.Interaction, mute: int=2, timeout: int=3, kick: int=5, ban: int=7):
        data = storage.get("automod")
        gid = str(interaction.guild.id)
        entry = data.get(gid, {"enabled": True, "badwords": DEFAULT_BADWORDS, "link_blacklist": [], "warn_limits":{"mute":2,"timeout":3,"kick":5,"ban":7}})
        entry["warn_limits"] = {"mute":mute, "timeout":timeout, "kick":kick, "ban":ban}
        data[gid] = entry
        storage.set("automod", data)
        await interaction.response.send_message(embed=make_embed(title=f"{EMOJI['gear']} Warn Limits", description=str(entry["warn_limits"])))

    # Event listeners
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if not message.guild or message.author.bot:
            return
        data = storage.get("automod")
        gid = str(message.guild.id)
        entry = data.get(gid)
        if not entry or not entry.get("enabled"):
            return

        content = message.content.lower()
        # detect badwords
        if any(bw in content for bw in entry.get("badwords", DEFAULT_BADWORDS)):
            await self._strike(message, reason="Badword terdeteksi")
            try:
                await message.delete()
            except Exception:
                pass
            return

        # detect blacklisted links
        if any(link in content for link in entry.get("link_blacklist", [])):
            await self._strike(message, reason="Link blacklist")
            try:
                await message.delete()
            except Exception:
                pass
            return

        # simple spam: repeated chars or messages too fast not handled deeply here (lightweight)

    async def _strike(self, message: discord.Message, reason: str):
        from utils import storage
        warns = storage.get("warns")
        gid = str(message.guild.id)
        uid = str(message.author.id)
        warns.setdefault(gid, {}).setdefault(uid, 0)
        warns[gid][uid] += 1
        storage.set("warns", warns)

        # Take action
        automod = storage.get("automod").get(gid, {})
        limits = automod.get("warn_limits", {"mute":2,"timeout":3,"kick":5,"ban":7})
        count = warns[gid][uid]
        desc = f"{message.author.mention} mendapatkan warn ke-{count} karena: {reason}"

        try:
            if limits.get("ban", 0) and count >= limits["ban"]:
                await message.guild.ban(message.author, reason=f"Automod ban: {reason}")
                desc += f"\n{EMOJI.get('ban','🔨')} User di-ban (warn ≥ {limits['ban']})"
            elif limits.get("kick", 0) and count >= limits["kick"]:
                await message.guild.kick(message.author, reason=f"Automod kick: {reason}")
                desc += f"\n{EMOJI.get('kick','👢')} User di-kick (warn ≥ {limits['kick']})"
            elif limits.get("timeout", 0) and count >= limits["timeout"]:
                await message.author.timeout(discord.utils.utcnow() + discord.timedelta(minutes=30), reason="Automod timeout")
                desc += f"\n{EMOJI.get('timeout','⏳')} Timeout 30 menit (warn ≥ {limits['timeout']})"
            elif limits.get("mute", 0) and count >= limits["mute"]:
                # No native mute role; using short timeout
                await message.author.timeout(discord.utils.utcnow() + discord.timedelta(minutes=10), reason="Automod mute (timeout pendek)")
                desc += f"\n{EMOJI.get('timeout','⏳')} Automute 10 menit (warn ≥ {limits['mute']})"
        except Exception:
            pass

        # log to channel if exists
        channels = storage.get("channels").get(gid, {})
        log_id = channels.get("log")
        if log_id:
            ch = message.guild.get_channel(log_id)
            if ch:
                await ch.send(embed=make_embed(title=f"{EMOJI.get('warn','⚠️')} Automod", description=desc, color=CYAN))

async def setup(bot):
    await bot.add_cog(AutomodCog(bot))
