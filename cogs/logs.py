import discord
from discord import app_commands
from discord.ext import commands
from utils.embed_utils import make_embed, CYAN
from utils import storage
from emojis import EMOJI

class LogsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="setlogchannel", description="Set channel untuk log aktivitas audit")
    @app_commands.default_permissions(manage_guild=True)
    async def setlogchannel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        data = storage.get("channels")
        gid = str(interaction.guild.id)
        entry = data.get(gid, {})
        entry["log"] = channel.id
        data[gid] = entry
        storage.set("channels", data)
        await interaction.response.send_message(embed=make_embed(title=f"{EMOJI['log']} Log Channel", description=f"Log akan dikirim ke {channel.mention}"))

    async def send_log(self, guild: discord.Guild, title: str, desc: str):
        data = storage.get("channels")
        ch_id = data.get(str(guild.id), {}).get("log")
        if not ch_id:
            return
        ch = guild.get_channel(ch_id)
        if ch:
            await ch.send(embed=make_embed(title=title, description=desc, color=CYAN))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.send_log(member.guild, f"{EMOJI.get('welcome','👋')} Member Join", f"{member.mention} bergabung. ID: `{member.id}`")

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await self.send_log(member.guild, f"{EMOJI.get('minus','➖')} Member Leave", f"{member} keluar. ID: `{member.id}`")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.guild and not message.author.bot:
            await self.send_log(message.guild, f"{EMOJI.get('trash','🗑️')} Hapus Pesan", f"Author: {message.author.mention}\nIsi: {message.content[:1000]}")

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if after.guild and not after.author.bot and before.content != after.content:
            await self.send_log(after.guild, f"{EMOJI.get('paint','🎨')} Edit Pesan", f"Author: {after.author.mention}\nSebelum: {before.content[:500]}\nSesudah: {after.content[:500]}")

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.timed_out_until != after.timed_out_until:
            await self.send_log(after.guild, f"{EMOJI.get('timeout','⏳')} Timeout Update", f"{after.mention} timeout until: {after.timed_out_until}")

    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        await self.send_log(role.guild, f"{EMOJI.get('plus','➕')} Role Dibuat", f"{role.mention} dibuat.")

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        await self.send_log(role.guild, f"{EMOJI.get('minus','➖')} Role Dihapus", f"{role.name} dihapus.")

async def setup(bot):
    await bot.add_cog(LogsCog(bot))
