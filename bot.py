import discord
from discord.ext import commands
import json
import asyncio
from collections import defaultdict, deque
import time

# ==================== LOAD CONFIG ====================
with open("config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

LOG_CHANNEL_ID = CONFIG.get("LOG_CHANNEL_ID", 0)
THRESHOLDS = CONFIG.get("THRESHOLDS", {})
TIME_WINDOW = THRESHOLDS.get("time_window", 5)
WHITELISTED_USERS = set(CONFIG.get("WHITELISTED_USERS", []))
WHITELISTED_ROLES = set(CONFIG.get("WHITELISTED_ROLES", []))
WHITELISTED_BOTS = set(CONFIG.get("WHITELISTED_BOTS", []))

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
action_history = defaultdict(lambda: deque(maxlen=50))
lockdown_active = False

# ==================== HELPERS ====================
def is_whitelisted(user: discord.User) -> bool:
    if user.id in WHITELISTED_USERS:
        return True
    if user.bot and user.id in WHITELISTED_BOTS:
        return True
    return False

def is_admin(user: discord.Member) -> bool:
    return user.guild_permissions.administrator

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

async def ban_user(member: discord.Member, reason: str):
    try:
        await member.ban(reason=reason, delete_message_days=0)
        await log_event(member.guild, "🚨 ĐÃ BAN KẺ TẤN CÔNG", f"Đã ban {member.mention} (ID: {member.id})\nLý do: {reason}")
    except discord.Forbidden:
        await log_event(member.guild, "⚠️ LỖI QUYỀN", f"Không thể ban {member.mention} do thiếu quyền.")
    except Exception as e:
        await log_event(member.guild, "⚠️ LỖI KHI BAN", f"{e}")

async def activate_lockdown(guild: discord.Guild):
    global lockdown_active
    if lockdown_active:
        return
    lockdown_active = True
    try:
        everyone = guild.default_role
        await everyone.edit(permissions=discord.Permissions(create_instant_invite=False))
        await log_event(guild, "🔒 LOCKDOWN KÍCH HOẠT", "Đã vô hiệu hóa quyền tạo kênh/vai trò cho @everyone.")
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
        await log_event(guild, "🔓 LOCKDOWN HỦY BỎ", "Đã mở khóa server.")
    except Exception as e:
        await log_event(guild, "⚠️ LỖI HỦY LOCKDOWN", f"{e}")

# ==================== EVENT: ON_READY ====================
@bot.event
async def on_ready():
    print(f"✅ Bot đã sẵn sàng! Đăng nhập với tên {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="mọi hành động trong server"))

# ==================== EVENT: ON_AUDIT_LOG_ENTRY ====================
@bot.event
async def on_audit_log_entry(entry: discord.AuditLogEntry):
    if not entry.guild:
        return
    guild = entry.guild
    user = entry.user
    if not user:
        return

    if user.id == bot.user.id:
        return
    if is_whitelisted(user):
        return

    action_type = entry.action
    now = time.time()

    dangerous_actions = {
        discord.AuditLogAction.channel_delete: "channel_delete",
        discord.AuditLogAction.role_delete: "role_delete",
        discord.AuditLogAction.ban: "ban",
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
        await log_event(guild, f"⚠️ PHÁT HIỆN TẤN CÔNG - {action_key}",
                        f"User {user.mention} (ID: {user.id}) đã thực hiện {len(recent)} lần {action_key} trong {TIME_WINDOW}s (ngưỡng: {threshold}).")

        member = guild.get_member(user.id)
        if member:
            await ban_user(member, f"Auto-ban: {len(recent)} hành động {action_key} trong {TIME_WINDOW}s")
        else:
            await log_event(guild, "⚠️ KHÔNG TÌM THẤY MEMBER", f"Không thể ban {user.mention} vì không có trong server.")

        await activate_lockdown(guild)
        await asyncio.sleep(30)
        await deactivate_lockdown(guild)

# ==================== COMMANDS ====================
@bot.command(name="setup")
@commands.has_permissions(administrator=True)
async def setup(ctx):
    """Hiển thị bảng điều khiển chính của bot anti-nuke."""
    embed = discord.Embed(
        title="🛡️ HỆ THỐNG ANTI-NUKE",
        description="Chào mừng đến với hệ thống bảo vệ server tự động.",
        color=0x00BFFF,
        timestamp=discord.utils.utcnow()
    )
    embed.add_field(name="Kênh log", value=f"<#{LOG_CHANNEL_ID}>" if LOG_CHANNEL_ID else "Chưa cấu hình", inline=False)
    embed.add_field(name="Trạng thái lockdown", value="🔒 Đang bật" if lockdown_active else "🔓 Đã tắt", inline=True)
    embed.add_field(name="Ngưỡng phát hiện", value=f"Xóa kênh: {THRESHOLDS.get('channel_delete', 3)}\nXóa role: {THRESHOLDS.get('role_delete', 3)}\nBan: {THRESHOLDS.get('ban', 2)}", inline=True)
    embed.add_field(name="Các lệnh", value="`l!help` để xem hướng dẫn", inline=False)
    embed.set_footer(text=f"Yêu cầu bởi {ctx.author.name}", icon_url=ctx.author.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="help")
async def help_cmd(ctx):
    embed = discord.Embed(title="📖 Hướng dẫn Anti-Nuke", color=0x00BFFF)
    embed.add_field(name="l!setup", value="Hiển thị trạng thái hệ thống", inline=False)
    embed.add_field(name="l!whitelist @user", value="Thêm user vào whitelist", inline=False)
    embed.add_field(name="l!unwhitelist @user", value="Xóa user khỏi whitelist", inline=False)
    embed.add_field(name="l!setlog #channel", value="Thiết lập kênh log", inline=False)
    embed.add_field(name="l!lockdown / l!unlockdown", value="Bật/tắt lockdown thủ công", inline=False)
    await ctx.send(embed=embed)

@bot.command(name="antinuke")
@commands.has_permissions(administrator=True)
async def antinuke_status(ctx):
    """Hiển thị trạng thái của anti-nuke."""
    embed = discord.Embed(title="🛡️ TÌNH TRẠNG ANTI-NUKE", color=0x00FF00)
    embed.add_field(name="Lockdown", value="🔒 Đang bật" if lockdown_active else "🔓 Đã tắt", inline=True)
    embed.add_field(name="Kênh log", value=f"<#{LOG_CHANNEL_ID}>" if LOG_CHANNEL_ID else "Chưa cấu hình", inline=True)
    embed.add_field(name="Ngưỡng", value=f"Xóa kênh: {THRESHOLDS.get('channel_delete', 3)}\nXóa role: {THRESHOLDS.get('role_delete', 3)}\nBan: {THRESHOLDS.get('ban', 2)}", inline=False)
    embed.add_field(name="Whitelist", value=f"Users: {len(WHITELISTED_USERS)}\nRoles: {len(WHITELISTED_ROLES)}\nBots: {len(WHITELISTED_BOTS)}", inline=True)
    await ctx.send(embed=embed)

@bot.command(name="whitelist")
@commands.has_permissions(administrator=True)
async def whitelist(ctx, target: discord.User):
    WHITELISTED_USERS.add(target.id)
    CONFIG["WHITELISTED_USERS"].append(target.id)
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(CONFIG, f, indent=4)
    await ctx.send(f"✅ Đã thêm {target.mention} vào whitelist.")

@bot.command(name="unwhitelist")
@commands.has_permissions(administrator=True)
async def unwhitelist(ctx, target: discord.User):
    WHITELISTED_USERS.discard(target.id)
    if target.id in CONFIG["WHITELISTED_USERS"]:
        CONFIG["WHITELISTED_USERS"].remove(target.id)
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(CONFIG, f, indent=4)
    await ctx.send(f"✅ Đã xóa {target.mention} khỏi whitelist.")

@bot.command(name="setlog")
@commands.has_permissions(administrator=True)
async def setlog(ctx, channel: discord.TextChannel):
    global LOG_CHANNEL_ID
    LOG_CHANNEL_ID = channel.id
    CONFIG["LOG_CHANNEL_ID"] = channel.id
    with open("config.json", "w", encoding="utf-8") as f:
        json.dump(CONFIG, f, indent=4)
    await ctx.send(f"✅ Đã đặt kênh log là {channel.mention}")

@bot.command(name="lockdown")
@commands.has_permissions(administrator=True)
async def lockdown_cmd(ctx):
    await activate_lockdown(ctx.guild)
    await ctx.send("🔒 Đã kích hoạt lockdown.")

@bot.command(name="unlockdown")
@commands.has_permissions(administrator=True)
async def unlockdown_cmd(ctx):
    await deactivate_lockdown(ctx.guild)
    await ctx.send("🔓 Đã hủy lockdown.")

# ==================== ERROR HANDLING ====================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Bạn cần quyền Administrator để dùng lệnh này.")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        await ctx.send(f"❌ Lỗi: {error}")

# ==================== RUN BOT ====================
if __name__ == "__main__":
    TOKEN = "YOUR_DISCORD_BOT_TOKEN_HERE"
    bot.run(TOKEN)
