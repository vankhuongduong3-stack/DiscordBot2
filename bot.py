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
        "channel_create": 1,  # Chỉ cần 1 hành động là kích hoạt ngay lập tức
        "channel_delete": 1,
        "role_delete": 1,
        "ban": 1,
        "bot_add": 1,
        "webhook_create": 1,
        "permission_update": 1,
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
    """Ban siêu tốc ngay lập tức trong tích tắc"""
    try:
        user_to_ban = await bot.fetch_user(user_id)
        await guild.ban(user_to_ban, reason=reason, delete_message_days=0)
        await log_event(guild, "⚡ TIÊU DIỆT CHỚP NHOÁNG (<0.5s)", f"Đã ban ngay lập tức: **{user_to_ban}** (ID: `{user_id}`)\nLý do: {reason}")
    except Exception as e:
        await log_event(guild, "⚠️ LỖI BAN NHANH", f"Không thể ban ID `{user_id}`: {e}")

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
        await log_event(guild, "🔒 LOCKDOWN TỨC THÌ", "Đã khóa toàn bộ quyền hạn nguy hiểm của `@everyone`.")
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
    """Sao lưu cấu trúc server"""
    backup_data = {
        "guild_name": guild.name,
        "timestamp": time.time(),
        "roles": [],
        "channels": []
    }
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
    for channel in guild.channels:
        if isinstance(channel, discord.TextChannel):
            backup_data["channels"].append({"type": "text", "name": channel.name, "topic": channel.topic})
        elif isinstance(channel, discord.VoiceChannel):
            backup_data["channels"].append({"type": "voice", "name": channel.name})

    filename = os.path.join(BACKUP_DIR, f"backup_{guild.id}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, indent=4, ensure_ascii=False)
    return filename

# ==================== EVENT: ON_READY ====================
@bot.event
async def on_ready():
    print(f"✅ Bot Anti-Nuke Speed-Light đã sẵn sàng! Đăng nhập: {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="Bảo vệ siêu tốc 0.5s"))

# ==================== EVENT: ON_AUDIT_LOG_ENTRY (INSTANT RESPONSE) ====================
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

    # Toàn bộ danh sách hành động nguy hiểm
    dangerous_actions = {
        discord.AuditLogAction.channel_create: "channel_create",
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
    threshold = THRESHOLDS.get(action_key, 1) # Ngưỡng mặt định = 1 để kích hoạt tức khắc

    # Xử lý song song đồng thời các tác vụ trừng phạt để đạt tốc độ dưới 0.5s thực tế
    await asyncio.gather(
        safe_ban(guild, user.id, f"Instant Anti-Nuke: Phát hiện hành động {action_key}"),
        activate_lockdown(guild),
        create_server_backup(guild)
    )

# ==================== COMMANDS ====================
@bot.command(name="setup")
@commands.has_permissions(administrator=True)
async def setup(ctx):
    embed = discord.Embed(
        title="⚡ HỆ THỐNG ANTI-NUKE SIÊU TỐC (<0.5S)",
        description="Mọi hành vi tấn công sẽ bị vô hiệu hóa ngay lập tức từ yêu cầu đầu tiên.",
        color=0x00BFFF,
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name="Kênh Log", value=f"<#{LOG_CHANNEL_ID}>" if LOG_CHANNEL_ID else "Chưa đặt (`l!setlog`)", inline=False)
    embed.add_field(name="Trạng thái Lockdown", value="🔒 Đang bật" if lockdown_active else "🔓 Đang tắt", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="backup")
@commands.has_permissions(administrator=True)
async def backup_cmd(ctx):
    msg = await ctx.send("⏳ Đang sao lưu cấu trúc server...")
    try:
        await create_server_backup(ctx.guild)
        await msg.edit(content="✅ **Sao lưu thành công!**")
    except Exception as e:
        await msg.edit(content=f"❌ Lỗi: {e}")

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
        await ctx.send("❌ Không thể gỡ quyền Owner.")
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
        await ctx.send("❌ Bạn cần quyền Administrator.")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        await ctx.send(f"❌ Lỗi: {error}")

# ==================== RUN BOT ====================
if __name__ == "__main__":
    TOKEN = os.getenv("TOKEN")
    if not TOKEN:
        print("❌ LỖI: Không tìm thấy biến môi trường TOKEN!")
    else:
        bot.run(TOKEN)
