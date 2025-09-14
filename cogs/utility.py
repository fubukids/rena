import asyncio, time
import discord
from discord import app_commands
from discord.ext import commands, tasks
from utils.embed_utils import make_embed, CYAN
from utils import storage
from emojis import EMOJI

class UtilityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.autopost_loop.start()

    def cog_unload(self):
        self.autopost_loop.cancel()

    @app_commands.command(name="setwelcomechannel", description="Set welcome channel dengan opsi pesan")
    @app_commands.describe(channel="Channel welcome", description_text="Deskripsi embed", image_url="URL gambar (opsional)", ping_user="Ping user baru?")
    @app_commands.default_permissions(manage_guild=True)
    async def setwelcomechannel(self, interaction: discord.Interaction, channel: discord.TextChannel, description_text: str="Selamat datang!", image_url: str=None, ping_user: bool=True):
        data = storage.get("channels")
        gid = str(interaction.guild.id)
        entry = data.get(gid, {})
        entry["welcome"] = channel.id
        data[gid] = entry
        storage.set("channels", data)
        # Save welcome config
        wc = storage.get("welcome_cfg")
        wc[str(interaction.guild.id)] = {"desc": description_text, "image": image_url, "ping": ping_user}
        storage.set("welcome_cfg", wc)
        await interaction.response.send_message(embed=make_embed(title=f"{EMOJI['welcome']} Welcome Channel", description=f"Welcome di {channel.mention}"))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        chs = storage.get("channels").get(str(member.guild.id), {})
        ch_id = chs.get("welcome")
        if ch_id:
            ch = member.guild.get_channel(ch_id)
            cfg = storage.get("welcome_cfg").get(str(member.guild.id), {"desc":"Selamat datang!","image":None,"ping":True})
            if ch:
                e = make_embed(title=f"{EMOJI.get('welcome','👋')} Selamat Datang {member.name}", description=cfg.get("desc"))
                e.set_thumbnail(url=member.display_avatar.url if member.display_avatar else discord.Embed.Empty)
                if cfg.get("image"):
                    e.set_image(url=cfg["image"])
                mention = member.mention if cfg.get("ping", True) else ""
                await ch.send(content=mention, embed=e)

    @app_commands.command(name="setbooster", description="Set channel untuk ucapan booster")
    @app_commands.default_permissions(manage_guild=True)
    async def setbooster(self, interaction: discord.Interaction, channel: discord.TextChannel):
        data = storage.get("channels")
        gid = str(interaction.guild.id)
        entry = data.get(gid, {})
        entry["booster"] = channel.id
        data[gid] = entry
        storage.set("channels", data)
        await interaction.response.send_message(embed=make_embed(title=f"{EMOJI['booster']} Booster Channel", description=f"Booster message ke {channel.mention}"))

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if not before.premium_since and after.premium_since:
            chs = storage.get("channels").get(str(after.guild.id), {})
            ch_id = chs.get("booster")
            if ch_id:
                ch = after.guild.get_channel(ch_id)
                if ch:
                    e = make_embed(title=f"{EMOJI.get('booster','🚀')} Terima kasih, Booster!", description=f"{after.mention} baru saja boost server!")
                    e.set_thumbnail(url=after.display_avatar.url if after.display_avatar else discord.Embed.Empty)
                    await ch.send(embed=e)

    @app_commands.command(name="addemoji", description="Tambah custom emoji dari emoji lain")
    @app_commands.describe(emoji_str="Emoji sumber", name="Nama emoji baru")
    @app_commands.default_permissions(manage_emojis_and_stickers=True)
    async def addemoji(self, interaction: discord.Interaction, emoji_str: str, name: str):
        try:
            # Try to convert from partial emoji
            emoji = discord.PartialEmoji.from_str(emoji_str)
            asset = await emoji.read()
            new = await interaction.guild.create_custom_emoji(name=name, image=asset)
            await interaction.response.send_message(embed=make_embed(title=f"{EMOJI['plus']} Emoji", description=f"Emoji dibuat: <:{new.name}:{new.id}>"))
        except Exception as e:
            await interaction.response.send_message(f"Gagal menambah emoji: {e}", ephemeral=True)

    @app_commands.command(name="dmuser", description="Kirim DM ke user (harus satu server)")
    @app_commands.default_permissions(manage_messages=True)
    async def dmuser(self, interaction: discord.Interaction, user: discord.Member, message: str):
        try:
            await user.send(message)
            await interaction.response.send_message(embed=make_embed(title=f"{EMOJI['message']} DM", description=f"DM terkirim ke {user.mention}"))
        except Exception as e:
            await interaction.response.send_message(f"Gagal DM: {e}", ephemeral=True)

    @app_commands.command(name="embedmaker", description="Buat embed cepat")
    @app_commands.describe(title="Judul", desc="Deskripsi", channel="Kirim ke channel ini (opsional)", image_url="URL gambar opsional")
    async def embedmaker(self, interaction: discord.Interaction, title: str, desc: str, channel: discord.TextChannel=None, image_url: str=None):
        e = make_embed(title=title, description=desc, color=CYAN)
        if image_url:
            e.set_image(url=image_url)
        if channel:
            await channel.send(embed=e)
            await interaction.response.send_message("Embed dikirim.", ephemeral=True)
        else:
            await interaction.response.send_message(embed=e)

    @app_commands.command(name="autopost", description="Buat autopost embed berjadwal")
    @app_commands.describe(channel="Channel tujuan", role_to_ping="Role yang diping (opsional)", title="Judul", desc="Deskripsi", interval_seconds="Interval detik")
    @app_commands.default_permissions(manage_guild=True)
    async def autopost(self, interaction: discord.Interaction, channel: discord.TextChannel, interval_seconds: int, title: str, desc: str, role_to_ping: discord.Role=None):
        data = storage.get("autopost")
        gid = str(interaction.guild.id)
        entry = data.get(gid, {"tasks":[]})
        entry["tasks"].append({
            "channel": channel.id,
            "role": role_to_ping.id if role_to_ping else None,
            "title": title,
            "desc": desc,
            "color": CYAN.value,
            "interval": interval_seconds,
            "last": 0
        })
        data[gid] = entry
        storage.set("autopost", data)
        await interaction.response.send_message(embed=make_embed(title=f"{EMOJI['loop']} Autopost", description=f"Task dibuat setiap {interval_seconds} detik ke {channel.mention}"))

    @app_commands.command(name="removeautopost", description="Hapus semua autopost di server ini")
    @app_commands.default_permissions(manage_guild=True)
    async def removeautopost(self, interaction: discord.Interaction):
        data = storage.get("autopost")
        data[str(interaction.guild.id)] = {"tasks":[]}
        storage.set("autopost", data)
        await interaction.response.send_message(embed=make_embed(title=f"{EMOJI['trash']} Autopost", description="Semua autopost dihapus."))

    @tasks.loop(seconds=10)
    async def autopost_loop(self):
        await self.bot.wait_until_ready()
        data = storage.get("autopost")
        now = int(time.time())
        changed = False
        for gid, entry in data.items():
            guild = self.bot.get_guild(int(gid))
            if not guild: 
                continue
            for task in entry.get("tasks", []):
                if now - int(task.get("last",0)) >= int(task["interval"]):
                    ch = guild.get_channel(int(task["channel"]))
                    if ch:
                        e = make_embed(title=task["title"], description=task["desc"], color=discord.Color(task.get("color", CYAN.value)))
                        ping = f"<@&{task['role']}>" if task.get("role") else ""
                        try:
                            await ch.send(content=ping, embed=e, allowed_mentions=discord.AllowedMentions(roles=True))
                            task["last"] = now
                            changed = True
                        except Exception:
                            pass
        if changed:
            storage.set("autopost", data)

async def setup(bot):
    await bot.add_cog(UtilityCog(bot))
