import discord
from discord.ext import commands
import asyncio
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import re

# Khởi tạo Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True
intents.moderation = True

bot = commands.Bot(command_prefix='l!', intents=intents, help_command=None)

# Cấu hình
CONFIG_FILE = "antinuke_config.json"
OWNER_ID = 1535132569534865490  # Owner ID
MAX_ACTIONS = 3                 # Số hành động tối đa
TIME_WINDOW = 5                 # Khoảng thời gian (giây)
DELAY = 0.2                     # Độ trễ xử lý
ACTION_DELAY = 0.5              # Độ trễ giữa các hành động

# Lưu trữ dữ liệu
action_log = defaultdict(list)
suspicious_users = {}
recovery_backup = {}
log_channels = {}

class AntiNukeConfig:
    def __init__(self):
        self.config = {
            "punishment": "kick",
            "max_actions": MAX_ACTIONS,
            "time_window": TIME_WINDOW,
            "enabled": True,
            "auto_recovery": True,
            "log_channels": {},
            "alert_channels": {}
        }
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    self.config.update(json.load(f))
            except Exception as e:
                print(f"Lỗi đọc file config: {e}")

    def save_config(self):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

config = AntiNukeConfig()

def is_owner(user):
    return user.id == OWNER_ID

def is_admin(member):
    if not isinstance(member, discord.Member):
        return False
    return member.guild_permissions.administrator or member.guild_permissions.manage_guild

async def punish_user(member, reason):
    await asyncio.sleep(ACTION_DELAY)
    if is_owner(member) or is_admin(member):
        return False

    try:
        if config.config["punishment"] == "ban":
            await member.ban(reason=reason)
        elif config.config["punishment"] == "timeout":
            await member.timeout(timedelta(hours=24), reason=reason)
        else:
            await member.kick(reason=reason)

        suspicious_users[member.id] = {
            "reason": reason,
            "time": datetime.now()
        }
        return True
    except Exception as e:
        print(f"Không thể xử phạt {member}: {e}")
        return False

async def send_log(guild, title, description, color=discord.Color.red()):
    await asyncio.sleep(DELAY)
    log_channel_id = config.config["log_channels"].get(str(guild.id)) or log_channels.get(guild.id)

    if log_channel_id:
        channel = guild.get_channel(int(log_channel_id))
        if channel:
            embed = discord.Embed(
                title=title,
                description=description,
                color=color,
                timestamp=datetime.now()
            )
            embed.set_footer(text=f"Titanium Anti-Nuke | {guild.name}")
            try:
                await channel.send(embed=embed)
            except Exception:
                pass

async def backup_guild(guild):
    backup = {
        "channels": [],
        "roles": [],
        "settings": {
            "name": guild.name,
            "icon": str(guild.icon.url) if guild.icon else None
        }
    }

    for channel in guild.channels:
        backup["channels"].append({
            "name": channel.name,
            "type": str(channel.type),
            "position": channel.position,
            "category": channel.category.name if channel.category else None
        })

    for role in guild.roles:
        if not role.managed and not role.is_default():
            backup["roles"].append({
                "name": role.name,
                "permissions": role.permissions.value,
                "color": role.color.value,
                "hoist": role.hoist,
                "mentionable": role.mentionable
            })

    recovery_backup[guild.id] = backup
    return backup

async def restore_guild(guild):
    if guild.id not in recovery_backup:
        return False

    backup = recovery_backup[guild.id]

    for role_data in backup["roles"]:
        await asyncio.sleep(ACTION_DELAY)
        try:
            await guild.create_role(
                name=role_data["name"],
                permissions=discord.Permissions(role_data["permissions"]),
                color=discord.Color(role_data["color"]),
                hoist=role_data["hoist"],
                mentionable=role_data["mentionable"]
            )
        except Exception:
            pass

    for channel_data in backup["channels"]:
        await asyncio.sleep(ACTION_DELAY)
        try:
            if "text" in channel_data["type"]:
                await guild.create_text_channel(name=channel_data["name"])
            elif "voice" in channel_data["type"]:
                await guild.create_voice_channel(name=channel_data["name"])
        except Exception:
            pass

    return True

@bot.event
async def on_ready():
    print(f'✅ {bot.user} đã sẵn sàng!')
    print(f'📊 Đang bảo vệ {len(bot.guilds)} servers')
    print(f'👑 Owner ID: {OWNER_ID}')
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.watching,
        name=f"l!help | {len(bot.guilds)} servers"
    ))

    for guild in bot.guilds:
        await backup_guild(guild)

# ==================== EVENTS ====================

@bot.event
async def on_guild_channel_create(channel):
    if not config.config["enabled"]:
        return

    await asyncio.sleep(DELAY)
    guild = channel.guild

    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_create):
        if entry.user.bot or is_owner(entry.user) or is_admin(entry.user):
            return

        user_id = entry.user.id
        current_time = datetime.now()
        action_log[user_id].append(current_time)

        action_log[user_id] = [t for t in action_log[user_id] if current_time - t < timedelta(seconds=config.config["time_window"])]

        if len(action_log[user_id]) >= config.config["max_actions"]:
            try:
                await channel.delete()
            except Exception:
                pass
            await punish_user(entry.user, "Tạo kênh hàng loạt - Nghi ngờ nuke")
            await send_log(guild, "🚨 PHÁT HIỆN NUKE!", f"**User:** {entry.user.mention}\n**Hành động:** Tạo kênh hàng loạt\n**Xử phạt:** {config.config['punishment']}")

@bot.event
async def on_guild_channel_delete(channel):
    if not config.config["enabled"]:
        return

    await asyncio.sleep(DELAY)
    guild = channel.guild

    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
        if entry.user.bot or is_owner(entry.user) or is_admin(entry.user):
            return

        user_id = entry.user.id
        current_time = datetime.now()
        action_log[user_id].append(current_time)

        action_log[user_id] = [t for t in action_log[user_id] if current_time - t < timedelta(seconds=config.config["time_window"])]

        if len(action_log[user_id]) >= config.config["max_actions"]:
            await punish_user(entry.user, "Xóa kênh hàng loạt - Nghi ngờ nuke")
            if config.config["auto_recovery"]:
                await restore_guild(guild)
            await send_log(guild, "🚨 PHÁT HIỆN NUKE!", f"**User:** {entry.user.mention}\n**Hành động:** Xóa kênh hàng loạt\n**Xử phạt:** {config.config['punishment']}")

@bot.event
async def on_member_ban(guild, user):
    if not config.config["enabled"]:
        return

    await asyncio.sleep(DELAY)

    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
        if entry.user.bot or is_owner(entry.user) or is_admin(entry.user):
            return

        user_id = entry.user.id
        current_time = datetime.now()
        action_log[user_id].append(current_time)

        action_log[user_id] = [t for t in action_log[user_id] if current_time - t < timedelta(seconds=config.config["time_window"])]

        if len(action_log[user_id]) >= config.config["max_actions"]:
            await punish_user(entry.user, "Ban hàng loạt - Nghi ngờ nuke")
            try:
                await guild.unban(user)
            except Exception:
                pass
            await send_log(guild, "🚨 PHÁT HIỆN NUKE!", f"**User:** {entry.user.mention}\n**Hành động:** Ban hàng loạt\n**Xử phạt:** {config.config['punishment']}")

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return

    if len(message.mentions) > 5:
        try:
            await message.delete()
            await message.author.timeout(timedelta(minutes=30), reason="Spam mention")
            await send_log(message.guild, "⚠️ SPAM MENTION!", f"**User:** {message.author.mention}\n**Hành động:** Timeout 30 phút")
        except Exception:
            pass
        return

    await bot.process_commands(message)

# ==================== COMMANDS ====================

@bot.command(name="setup")
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = discord.Embed(title="🛡️ TITANIUM ANTI-NUKE SETUP", description="Đang thiết lập hệ thống bảo vệ...", color=discord.Color.blue())
    msg = await ctx.send(embed=embed)

    log_channel = discord.utils.get(ctx.guild.channels, name="🔒-anti-nuke-log")
    if not log_channel:
        log_channel = await ctx.guild.create_text_channel("🔒-anti-nuke-log")
        await log_channel.set_permissions(ctx.guild.default_role, send_messages=False)

    config.config["log_channels"][str(ctx.guild.id)] = log_channel.id
    log_channels[ctx.guild.id] = log_channel.id
    config.save_config()

    await backup_guild(ctx.guild)

    embed = discord.Embed(title="✅ SETUP HOÀN TẤT!", description="Hệ thống Anti-Nuke đã được kích hoạt!", color=discord.Color.green())
    embed.add_field(name="📁 Kênh Log", value=log_channel.mention, inline=True)
    embed.add_field(name="🛡️ Trạng Thái", value="✅ Đã bật", inline=True)
    embed.add_field(name="⚙️ Xử Phạt", value=config.config["punishment"].upper(), inline=True)
    await msg.edit(embed=embed)

@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(title="🛡️ TITANIUM ANTI-NUKE", description="Hệ thống chống phá hoại server Discord", color=discord.Color.gold())
    embed.add_field(
        name="📌 LỆNH CHÍNH",
        value="`l!setup` - Thiết lập hệ thống\n`l!status` - Kiểm tra trạng thái\n`l!backup` - Backup server\n`l!restore` - Khôi phục server",
        inline=False
    )
    await ctx.send(embed=embed)

# Chạy bot (khuyên dùng os.getenv cho token)
TOKEN = os.getenv("DISCORD_TOKEN", "NHAP_TOKEN_CUA_BAN_VAO_DAY")
bot.run(TOKEN)
