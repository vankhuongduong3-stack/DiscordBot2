import discord
from discord.ext import commands
import json
import asyncio
from collections import defaultdict, deque
import time
import os

# ==================== LOAD HOẶC TẠO CONFIG MẶC ĐỊNH ====================
CONFIG_FILE = "config.json"

default_config = {
    "LOG_CHANNEL_ID": 0,
    "OWNER_IDS": [1535132569534865490],
    "THRESHOLDS": {
        "channel_delete": 3,
        "role_delete": 3,
        "ban": 2,
        "bot_add": 1,
        "webhook_create": 2,
        "permission_update": 3,
        "time_window": 5
    },
    "WHITELISTED_USERS": [1535132569534865490],
    "WHITELISTED_ROLES": [],
    "WHITELISTED_BOTS": []
}

if not os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(default_config, f, indent=4)

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

LOG_CHANNEL_ID = CONFIG.get("LOG_CHANNEL_ID", 0)
OWNER_IDS = set(CONFIG.get("OWNER_IDS", [1535132569534865490]))
THRESHOLDS = CONFIG.get("THRESHOLDS", {})
TIME_WINDOW = THRESHOLDS.get("time_window", 5)
WHITELISTED_USERS = set(CONFIG.get("WHITELISTED_USERS", []))
WHITELISTED_ROLES = set(CONFIG.get("WHITELISTED_ROLES", []))
WHITELISTED_BOTS = set(CONFIG.get("WHITELISTED_BOTS", []))

WHITELISTED_USERS.update(OWNER_IDS)

# ==================== BOT SETUP ====================
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.bans = True
intents.moderation = True
intents.webhooks = True
intents.message_content = True

bot = commands.Bot(command_prefix="l!", intents=intents, help_command=None)

# ==================== TRACKING STRUCTURES ====================
action_history = defaultdict(lambda: deque(maxlen=100))
lockdown_active = False

# ==================== HELPERS ====================
def is_whitelisted(user: discord.User) -> bool:
    if user.id in OWNER_IDS:
        return True
    if user.id in WHITELISTED_USERS:
        return True
    if user.bot and user.id in WHITELISTED_BOTS:
        return True
    return False

async def log_event(guild: discord.Guild, title: str, description: str, color=0xFF0000):
    if not LOG_CHANNEL_ID:
        return
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if not channel:
        return
    embed = discord.Embed(title=title, description=description, color=color, timestamp=discord.utils.utcnow())
    embed.set_footer(text=f"Guild: {guild.name}")
    try:
        await channel.send(embed=embed)
    except:
        pass

async def safe_ban(guild: discord.Guild, user_id: int, reason: str):
    """Ban an toàn ngay cả khi user đã out khỏi server"""
    try:
        user_to_ban = await bot.fetch_user(user_id)
        await guild.ban(user_to_ban, reason=reason, delete_message_days=0)
        await log_event(guild, "🚨 ĐÃ TRỤC XUẤT KẺ TẤN CÔNG", f"Đã ban: **{user_to_ban}** (ID: `{user_id}`)\nLý do: {reason}")
    except Exception as e:
        await log_event(guild, "⚠️ LỖI KHI BAN", f"Không thể ban ID `{user_id}`: {e}")

async def activate_lockdown(guild: discord.Guild):
    global lockdown_active
    if lockdown_active:
        return
    lockdown_active = True
    try:
        everyone = guild.default_role
        await everyone.edit(permissions=discord.Permissions(
            create_instant_invite=False,
            manage_channels=False,
            manage_roles=False,
            manage_webhooks=False,
            mention_everyone=False
        ))
        await log_event(guild, "🔒 LOCKDOWN KHẨN CẤP", "Đã khóa toàn bộ quyền nguy hiểm của `@everyone`.")
    except Exception as e:
        await log_event(guild, "⚠️ LỖI LOCKDOWN", f"{e}")

async def deactivate_lockdown(guild: discord.Guild):
    global lockdown_active
    if not lockdown_active:
        return
    lockdown_active = False
    try:
        everyone = guild.default_role
        await everyone.edit(permissions=discord.Permissions.none())
        await log_event(guild, "🔓 HỦY LOCKDOWN", "Đã mở khóa server trở lại trạng thái bình thường.")
    except Exception as e:
        await log_event(guild, "⚠️ LỖI HỦY LOCKDOWN", f"{e}")

# ==================== MODULE: BACKUP & RESTORE SERVER ====================
BACKUP_DIR = "backups"
if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

async def create_server_backup(guild: discord.Guild) -> str:
    """Sao lưu toàn bộ cấu trúc Server (Roles, Channels, Categories)"""
    backup_data = {
        "guild_name": guild.name,
        "timestamp": time.time(),
        "roles": [],
        "categories": [],
        "channels": []
    }

    # 1. Backup Roles (Bỏ qua @everyone và các managed role của bot)
    for role in sorted(guild.roles, key=lambda r: r.position, reverse=True):
        if role.is_default() or role.managed:
            continue
        backup_data["roles"].append({
            "name": role.name,
            "permissions": role.permissions.value,
            "color": role.color.value,
            "hoist": role.hoist,
            "mentionable": role.mentionable
        })

    # 2. Backup Categories & Channels
    for category in guild.categories:
        cat_data = {
            "name": category.name,
            "position": category.position,
            "overwrites": {str(target.id): ow.pair()[0].value for target, ow in category.overwrites.items()},
            "channels": []
        }
        for channel in category.channels:
            if isinstance(channel, discord.TextChannel):
                cat_data["channels"].append({
                    "type": "text",
                    "name": channel.name,
                    "topic": channel.topic,
                    "slowmode": channel.slowmode_delay,
                    "position": channel.position
                })
            elif isinstance(channel, discord.VoiceChannel):
                cat_data["channels"].append({
                    "type": "voice",
                    "name": channel.name,
                    "bitrate": channel.bitrate,
                    "user_limit": channel.user_limit,
                    "position": channel.position
                })
        backup_data["categories"].append(cat_data)

    # Backup channels không nằm trong category nào
    for channel in guild.text_channels:
        if channel.category is None:
            backup_data["channels"].append({
                "type": "text_nocat",
                "name": channel.name,
                "topic": channel.topic,
                "slowmode": channel.slowmode_delay,
                "position": channel.position
            })

    filename = os.path.join(BACKUP_DIR, f"backup_{guild.id}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, indent=4, ensure_ascii=False)
    return filename

# ==================== EVENT: ON_READY ====================
@bot.event
async def on_ready():
    print(f"✅ Bot Anti-Nuke Ultimate đã sẵn sàng! Đăng nhập: {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Bảo vệ tuyệt đối Server"))

# ==================== EVENT: ON_AUDIT_LOG_ENTRY (ANTI-NUKE CORE) ====================
@bot.event
async def on_audit_log_entry(entry: discord.AuditLogEntry):
    if not entry.guild:
        return
    guild = entry.guild
    user = entry.user
    if not user or user.id == bot.user.id:
        return

    if is_whitelisted(user):
        return

    action_type = entry.action
    now = time.time()

    dangerous_actions = {
        discord.AuditLogAction.channel_delete: "channel_delete",
        discord.AuditLogAction.role_delete: "role_delete",
        discord.AuditLogAction.ban: "ban",
        discord.AuditLogAction.bot_add: "bot_add",
        discord.AuditLogAction.webhook_create: "webhook_create",
        discord.AuditLogAction.role_update: "permission_update",
        discord.AuditLogAction.channel_update: "permission_update",
        discord.AuditLogAction.overwrite_update: "permission_update",
        discord.AuditLogAction.member_update: "permission_update"
    }

    if action_type not in dangerous_actions:
        return

    action_key = dangerous_actions[action_type]
    threshold = THRESHOLDS.get(action_key, 3)

    history = action_history[user.id]
    history.append(now)

    window_start = now - TIME_WINDOW
    recent = [t for t in history if t >= window_start]

    if len(recent) >= threshold:
        history.clear()

        await log_event(guild, f"⚠️ PHÁT HIỆN TẤN CÔNG - {action_key.upper()}",
                        f"User **{user}** (ID: `{user.id}`) vi phạm ngưỡng `{action_key}` ({len(recent)}/{threshold} lần trong {TIME_WINDOW}s).")

        # Thực hiện trừng phạt & cô lập server lập tức
        await safe_ban(guild, user.id, f"Anti-Nuke Protection: Spam hành động {action_key}")
        await activate_lockdown(guild)
        
        # Tự động tạo bản backup khẩn cấp trước khi có thiệt hại sâu hơn
        await create_server_backup(guild)

        await asyncio.sleep(60)
        await deactivate_lockdown(guild)

# ==================== COMMANDS ====================
@bot.command(name="setup")
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = discord.Embed(
        title="🛡️ HỆ THỐNG ANTI-NUKE & BACKUP ULTIMATE",
        description="Trạng thái hệ thống phòng thủ cấp độ cao đang bật.",
        color=0x00BFFF,
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name="Kênh Log", value=f"<#{LOG_CHANNEL_ID}>" if LOG_CHANNEL_ID else "Chưa đặt (`l!setlog`)", inline=False)
    embed.add_field(name="Trạng thái Lockdown", value="🔒 Đang bật" if lockdown_active else "🔓 Đang tắt", inline=True)
    embed.add_field(name="Tính năng", value="• Chống Xóa Kênh/Role\n• Chống Bot Lạ\n• Chống Webhook Spam\n• Hỗ trợ Backup/Restore", inline=False)
    embed.set_footer(text=f"Yêu cầu bởi {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="backup")
@commands.has_permissions(administrator=True)
async def backup_cmd(ctx):
    """Lưu trữ cấu hình server thủ công"""
    msg = await ctx.send("⏳ Đang tiến hành sao lưu cấu trúc server...")
    try:
        path = await create_server_backup(ctx.guild)
        await msg.edit(content=f"✅ **Sao lưu thành công!** Cấu trúc server đã được ghi lại an toàn.")
        await log_event(ctx.guild, "💾 TẠO BACKUP THỦ CÔNG", f"Được thực hiện bởi {ctx.author.mention}")
    except Exception as e:
        await msg.edit(content=f"❌ Lỗi khi backup: {e}")

@bot.command(name="whitelist")
@commands.has_permissions(administrator=True)
async def whitelist(ctx, target: discord.User):
    WHITELISTED_USERS.add(target.id)
    if target.id not in CONFIG["WHITELISTED_USERS"]:
        CONFIG["WHITELISTED_USERS"].append(target.id)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(CONFIG, f, indent=4)
    await ctx.send(f"✅ Đã thêm **{target}** vào whitelist.")

@bot.command(name="unwhitelist")
@commands.has_permissions(administrator=True)
async def unwhitelist(ctx, target: discord.User):
    if target.id in OWNER_IDS:
        await ctx.send("❌ Không thể gỡ quyền Owner khỏi Whitelist.")
        return
    WHITELISTED_USERS.discard(target.id)
    if target.id in CONFIG["WHITELISTED_USERS"]:
        CONFIG["WHITELISTED_USERS"].remove(target.id)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(CONFIG, f, indent=4)
    await ctx.send(f"✅ Đã xóa **{target}** khỏi whitelist.")

@bot.command(name="setlog")
@commands.has_permissions(administrator=True)
async def setlog(ctx, channel: discord.TextChannel):
    global LOG_CHANNEL_ID
    LOG_CHANNEL_ID = channel.id
    CONFIG["LOG_CHANNEL_ID"] = channel.id
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(CONFIG, f, indent=4)
    await ctx.send(f"✅ Đã đặt kênh log là {channel.mention}")

@bot.command(name="lockdown")
@commands.has_permissions(administrator=True)
async def lockdown_cmd(ctx):
    await activate_lockdown(ctx.guild)
    await ctx.send("🔒 Đã bật lockdown thủ công.")

@bot.command(name="unlockdown")
@commands.has_permissions(administrator=True)
async def unlockdown_cmd(ctx):
    await deactivate_lockdown(ctx.guild)
    await ctx.send("🔓 Đã tắt lockdown thủ công.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bạn cần quyền Administrator để thực hiện lệnh này.")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        await ctx.send(f"❌ Lỗi hệ thống: {error}")

# ==================== RUN BOT ====================
if __name__ == "__main__":
    TOKEN = os.getenv("TOKEN")
    if not TOKEN:
        print("❌ LỖI: Không tìm thấy biến môi trường TOKEN!")
    else:
        bot.run(TOKEN)
