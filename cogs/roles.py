import discord
from discord import app_commands
from discord.ext import commands
from utils.embed_utils import make_embed, CYAN
from utils import storage
from emojis import EMOJI

class RolesCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="deleterole", description="Hapus role yang di-mention")
    @app_commands.default_permissions(manage_roles=True)
    async def deleterole(self, interaction: discord.Interaction, role: discord.Role):
        try:
            await role.delete(reason=f"By {interaction.user}")
            await interaction.response.send_message(embed=make_embed(title=f"{EMOJI['minus']} Delete Role", description=f"Role dihapus."))
        except discord.Forbidden:
            await interaction.response.send_message("Tidak punya izin atau role di atas bot.", ephemeral=True)

    @app_commands.command(name="createrolereaction", description="Buat Reaction Roles untuk banyak role")
    @app_commands.describe(channel="Channel target", title="Judul embed", desc="Deskripsi", roles_with_emojis="Format: emoji role_mention; dipisahkan koma")
    @app_commands.default_permissions(manage_roles=True)
    async def createrolereaction(self, interaction: discord.Interaction, channel: discord.TextChannel, title: str, desc: str, roles_with_emojis: str):
        # Parse "😀 @Role, 😎 @Role2"
        mapping = {}
        for pair in roles_with_emojis.split(","):
            pair = pair.strip()
            if not pair:
                continue
            try:
                emoji_str, role_mention = pair.split(" ", 1)
                role_id = int(role_mention.strip().strip("<@&>").strip())
                mapping[emoji_str] = role_id
            except Exception:
                continue
        e = make_embed(title=title, description=desc, color=CYAN)
        msg = await channel.send(embed=e)
        for emoji_str in mapping.keys():
            try:
                await msg.add_reaction(emoji_str)
            except Exception:
                pass
        # Save mapping
        data = storage.get("reactionroles")
        data.setdefault(str(interaction.guild.id), {})[str(msg.id)] = mapping
        storage.set("reactionroles", data)
        await interaction.response.send_message(embed=make_embed(title=f"{EMOJI['role']} Reaction Roles", description=f"RR dibuat di {channel.mention} (msg id: `{msg.id}`)"))

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is None or payload.user_id == self.bot.user.id:
            return
        data = storage.get("reactionroles").get(str(payload.guild_id), {})
        mapping = data.get(str(payload.message_id))
        if not mapping:
            return
        role_id = mapping.get(str(payload.emoji))
        if role_id:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            role = guild.get_role(int(role_id))
            if member and role:
                try:
                    await member.add_roles(role, reason="Reaction Roles")
                except Exception:
                    pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is None:
            return
        data = storage.get("reactionroles").get(str(payload.guild_id), {})
        mapping = data.get(str(payload.message_id))
        if not mapping:
            return
        role_id = mapping.get(str(payload.emoji))
        if role_id:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            role = guild.get_role(int(role_id))
            if member and role:
                try:
                    await member.remove_roles(role, reason="Reaction Roles")
                except Exception:
                    pass

    @app_commands.command(name="autorolewelcome", description="Set autorole ketika user baru join")
    @app_commands.default_permissions(manage_roles=True)
    async def autorolewelcome(self, interaction: discord.Interaction, role: discord.Role):
        data = storage.get("autorole")
        data[str(interaction.guild.id)] = role.id
        storage.set("autorole", data)
        await interaction.response.send_message(embed=make_embed(title=f"{EMOJI['role']} Autorole", description=f"Autorole set ke {role.mention}"))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        role_id = storage.get("autorole").get(str(member.guild.id))
        if role_id:
            role = member.guild.get_role(int(role_id))
            if role:
                try:
                    await member.add_roles(role, reason="Autorole welcome")
                except Exception:
                    pass

async def setup(bot):
    await bot.add_cog(RolesCog(bot))
