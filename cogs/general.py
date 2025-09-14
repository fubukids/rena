import discord
from discord import app_commands
from discord.ext import commands
from utils.embed_utils import make_embed, CYAN
from emojis import EMOJI

class GeneralCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kick", description="Kick user")
    @app_commands.describe(user="User yang akan di kick", reason="Alasan")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str="No reason"):
        try:
            await user.kick(reason=reason)
            e = make_embed(title=f"{EMOJI['kick']} Kick", description=f"User {user.mention} di-kick. Alasan: {reason}", color=CYAN)
            await interaction.response.send_message(embed=e)
        except discord.Forbidden:
            await interaction.response.send_message("Aku tidak punya izin untuk kick user ini.", ephemeral=True)

    @app_commands.command(name="ban", description="Ban user")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str="No reason"):
        try:
            await user.ban(reason=reason, delete_message_days=0)
            e = make_embed(title=f"{EMOJI['ban']} Ban", description=f"User {user.mention} di-ban. Alasan: {reason}")
            await interaction.response.send_message(embed=e)
        except discord.Forbidden:
            await interaction.response.send_message("Aku tidak punya izin untuk ban user ini.", ephemeral=True)

    @app_commands.command(name="timeout", description="Timeout user (detik)")
    @app_commands.describe(seconds="Durasi timeout dalam detik", reason="Alasan")
    @app_commands.default_permissions(moderate_members=True)
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, seconds: int, reason: str="No reason"):
        try:
            await user.timeout(discord.utils.utcnow() + discord.timedelta(seconds=seconds), reason=reason)
            e = make_embed(title=f"{EMOJI['timeout']} Timeout", description=f"{user.mention} timeout {seconds} detik. Alasan: {reason}")
            await interaction.response.send_message(embed=e)
        except discord.Forbidden:
            await interaction.response.send_message("Tidak punya izin timeout.", ephemeral=True)

    @app_commands.command(name="warn", description="Warn user")
    @app_commands.describe(user="User yang akan di-warn", reason="Alasan")
    @app_commands.default_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str="No reason"):
        from utils import storage
        warns = storage.get("warns")
        gid = str(interaction.guild.id)
        uid = str(user.id)
        warns.setdefault(gid, {}).setdefault(uid, 0)
        warns[gid][uid] += 1
        storage.set("warns", warns)
        e = make_embed(title=f"{EMOJI['warn']} Warn", description=f"{user.mention} menerima warn ke-{warns[gid][uid]}. Alasan: {reason}", color=CYAN)
        await interaction.response.send_message(embed=e)

    @app_commands.command(name="unban", description="Unban user dengan ID")
    @app_commands.default_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user_id: str):
        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user)
            e = make_embed(title=f"{EMOJI['ok']} Unban", description=f"User {user.mention} sudah di-unban.")
            await interaction.response.send_message(embed=e)
        except Exception as e:
            await interaction.response.send_message(f"Gagal unban: {e}", ephemeral=True)

    @app_commands.command(name="addrole", description="Tambah role ke user")
    @app_commands.default_permissions(manage_roles=True)
    async def addrole(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role):
        try:
            await user.add_roles(role, reason=f"By {interaction.user}")
            await interaction.response.send_message(embed=make_embed(title=f"{EMOJI['plus']} Add Role", description=f"Berhasil menambah {role.mention} ke {user.mention}"))
        except discord.Forbidden:
            await interaction.response.send_message("Tidak bisa menambah role (cek posisi role bot).", ephemeral=True)

    @app_commands.command(name="moverole", description="Pindahkan role bot di atas role tertentu (butuh Manage Roles)")
    @app_commands.default_permissions(manage_roles=True)
    async def moverole(self, interaction: discord.Interaction, target_above: discord.Role):
        # Just informative: cannot programmatically move bot's top role; requires manual drag.
        await interaction.response.send_message("Silakan seret role bot di atas role target secara manual di pengaturan server.", ephemeral=True)

    @app_commands.command(name="movetimeout", description="Pindahkan timeout (alias set ulang durasi)")
    @app_commands.default_permissions(moderate_members=True)
    async def movetimeout(self, interaction: discord.Interaction, user: discord.Member, seconds: int):
        try:
            await user.timeout(discord.utils.utcnow() + discord.timedelta(seconds=seconds), reason=f"Adjust by {interaction.user}")
            await interaction.response.send_message(embed=make_embed(title=f"{EMOJI['timeout']} Timeout Updated", description=f"Timeout {user.mention} di-set ke {seconds} detik"))
        except discord.Forbidden:
            await interaction.response.send_message("Tidak punya izin.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(GeneralCog(bot))
