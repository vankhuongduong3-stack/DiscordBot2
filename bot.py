import discord
from discord.ext import commands
import asyncio
import json
import os
from datetime import datetime, timedelta
from collections import defaultdict
import re

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='l!', intents=intents, help_command=None)

# Cấu hình
CONFIG_FILE = "antinuke_config.json"
OWNER_ID = 1535132569534865490  # Owner ID
MAX_ACTIONS = 3                # Số hành động tối đa
TIME_WINDOW = 5                # Khoảng thời gian (giây)
DELAY = 0.2                    # Độ trễ xử lý
ACTION_DELAY = 0.5             # Độ trễ giữa các hành động

# Lưu trữ dữ liệu
action_log = defaultdict(list)
suspicious_users = {}
recovery_backup = {}
log_channels = {}  # Lưu log channel theo guild

class AntiNukeConfig:
    def __init__(self):
        self.config = {
            "punishment": "kick",
            "max_actions": 3,
            "time_window": 5,
            "enabled": True,
            "auto_recovery": True,
            "log_channels": {},
            "alert_channels": {}
        }
        self.load_config()
    
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                self.config.update(json.load(f))
    
    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=4)

config = AntiNukeConfig()

def is_owner(user):
    """Kiểm tra xem user có phải là owner không"""
    return user.id == OWNER_ID

def is_admin(member):
    """Kiểm tra xem member có quyền admin không"""
    return member.guild_permissions.administrator or member.guild_permissions.manage_guild

async def punish_user(member, reason):
    """Xử phạt user theo cấu hình"""
    await asyncio.sleep(ACTION_DELAY)
    
    # Không xử phạt owner
    if is_owner(member):
        return False
    
    # Không xử phạt admin
    if is_admin(member):
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
    except:
        return False

async def send_log(guild, title, description, color=discord.Color.red()):
    """Gửi log đến kênh log đã cấu hình"""
    await asyncio.sleep(DELAY)
    
    # Lấy log channel từ config hoặc memory
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
            await channel.send(embed=embed)

async def backup_guild(guild):
    """Backup toàn bộ server"""
    backup = {
        "channels": [],
        "roles": [],
        "settings": {
            "name": guild.name,
            "icon": str(guild.icon.url) if guild.icon else None,
            "verification_level": str(guild.verification_level),
            "default_notifications": str(guild.default_notifications)
        }
    }
    
    for channel in guild.channels:
        await asyncio.sleep(0)  # Không delay để backup nhanh
        backup["channels"].append({
            "name": channel.name,
            "type": str(channel.type),
            "position": channel.position,
            "category": channel.category.name if channel.category else None,
            "overwrites": {str(target.id): {perm: value for perm, value in overwrite.pairs()} 
                          for target, overwrite in channel.overwrites.items()}
        })
    
    for role in guild.roles:
        await asyncio.sleep(0)  # Không delay để backup nhanh
        if not role.managed:
            backup["roles"].append({
                "name": role.name,
                "permissions": role.permissions.value,
                "color": role.color.value,
                "hoist": role.hoist,
                "mentionable": role.mentionable,
                "position": role.position
            })
    
    recovery_backup[guild.id] = backup
    return backup

async def restore_guild(guild):
    """Khôi phục server từ backup"""
    if guild.id not in recovery_backup:
        return False
    
    backup = recovery_backup[guild.id]
    
    # Khôi phục roles
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
        except:
            pass
    
    # Khôi phục channels
    for channel_data in backup["channels"]:
        await asyncio.sleep(ACTION_DELAY)
        try:
            if "text" in channel_data["type"]:
                await guild.create_text_channel(
                    name=channel_data["name"],
                    position=channel_data["position"],
                    overwrites={discord.Object(id=int(target_id)): discord.PermissionOverwrite(**perms) 
                               for target_id, perms in channel_data["overwrites"].items()}
                )
            elif "voice" in channel_data["type"]:
                await guild.create_voice_channel(
                    name=channel_data["name"],
                    position=channel_data["position"],
                    overwrites={discord.Object(id=int(target_id)): discord.PermissionOverwrite(**perms) 
                               for target_id, perms in channel_data["overwrites"].items()}
                )
        except:
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
    
    # Tự động backup tất cả servers
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
        if entry.user.bot:
            return
        
        # Bỏ qua nếu là owner hoặc admin
        if is_owner(entry.user) or is_admin(entry.user):
            return
        
        user_id = entry.user.id
        current_time = datetime.now()
        action_log[user_id].append(current_time)
        
        # Xóa log cũ
        action_log[user_id] = [t for t in action_log[user_id] 
                               if current_time - t < timedelta(seconds=config.config["time_window"])]
        
        if len(action_log[user_id]) >= config.config["max_actions"]:
            # Xóa kênh vừa tạo
            await asyncio.sleep(ACTION_DELAY)
            await channel.delete()
            
            # Xử phạt
            await punish_user(entry.user, "Tạo kênh hàng loạt - Nghi ngờ nuke")
            
            await send_log(guild, "🚨 PHÁT HIỆN NUKE!", 
                          f"**User:** {entry.user.mention}\n**Hành động:** Tạo kênh hàng loạt\n**Xử phạt:** {config.config['punishment']}")

@bot.event
async def on_guild_channel_delete(channel):
    if not config.config["enabled"]:
        return
    
    await asyncio.sleep(DELAY)
    guild = channel.guild
    
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
        if entry.user.bot:
            return
        
        if is_owner(entry.user) or is_admin(entry.user):
            return
        
        user_id = entry.user.id
        current_time = datetime.now()
        action_log[user_id].append(current_time)
        
        action_log[user_id] = [t for t in action_log[user_id] 
                               if current_time - t < timedelta(seconds=config.config["time_window"])]
        
        if len(action_log[user_id]) >= config.config["max_actions"]:
            await punish_user(entry.user, "Xóa kênh hàng loạt - Nghi ngờ nuke")
            
            # Khôi phục kênh
            if config.config["auto_recovery"]:
                await restore_guild(guild)
            
            await send_log(guild, "🚨 PHÁT HIỆN NUKE!", 
                          f"**User:** {entry.user.mention}\n**Hành động:** Xóa kênh hàng loạt\n**Xử phạt:** {config.config['punishment']}")

@bot.event
async def on_member_ban(guild, user):
    if not config.config["enabled"]:
        return
    
    await asyncio.sleep(DELAY)
    
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
        if entry.user.bot:
            return
        
        if is_owner(entry.user) or is_admin(entry.user):
            return
        
        user_id = entry.user.id
        current_time = datetime.now()
        action_log[user_id].append(current_time)
        
        action_log[user_id] = [t for t in action_log[user_id] 
                               if current_time - t < timedelta(seconds=config.config["time_window"])]
        
        if len(action_log[user_id]) >= config.config["max_actions"]:
            await punish_user(entry.user, "Ban hàng loạt - Nghi ngờ nuke")
            
            # Unban nạn nhân
            try:
                await asyncio.sleep(ACTION_DELAY)
                await guild.unban(user)
            except:
                pass
            
            await send_log(guild, "🚨 PHÁT HIỆN NUKE!", 
                          f"**User:** {entry.user.mention}\n**Hành động:** Ban hàng loạt\n**Xử phạt:** {config.config['punishment']}")

@bot.event
async def on_member_remove(member):
    if not config.config["enabled"]:
        return
    
    await asyncio.sleep(DELAY)
    guild = member.guild
    
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.kick):
        if entry.user.bot:
            return
        
        if entry.target.id != member.id:
            return
        
        if is_owner(entry.user) or is_admin(entry.user):
            return
        
        user_id = entry.user.id
        current_time = datetime.now()
        action_log[user_id].append(current_time)
        
        action_log[user_id] = [t for t in action_log[user_id] 
                               if current_time - t < timedelta(seconds=config.config["time_window"])]
        
        if len(action_log[user_id]) >= config.config["max_actions"]:
            await punish_user(entry.user, "Kick hàng loạt - Nghi ngờ nuke")
            
            await send_log(guild, "🚨 PHÁT HIỆN NUKE!", 
                          f"**User:** {entry.user.mention}\n**Hành động:** Kick hàng loạt\n**Xử phạt:** {config.config['punishment']}")

@bot.event
async def on_guild_role_delete(role):
    if not config.config["enabled"]:
        return
    
    await asyncio.sleep(DELAY)
    guild = role.guild
    
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_delete):
        if entry.user.bot:
            return
        
        if is_owner(entry.user) or is_admin(entry.user):
            return
        
        user_id = entry.user.id
        current_time = datetime.now()
        action_log[user_id].append(current_time)
        
        action_log[user_id] = [t for t in action_log[user_id] 
                               if current_time - t < timedelta(seconds=config.config["time_window"])]
        
        if len(action_log[user_id]) >= config.config["max_actions"]:
            await punish_user(entry.user, "Xóa role hàng loạt - Nghi ngờ nuke")
            
            if config.config["auto_recovery"]:
                await restore_guild(guild)
            
            await send_log(guild, "🚨 PHÁT HIỆN NUKE!", 
                          f"**User:** {entry.user.mention}\n**Hành động:** Xóa role hàng loạt\n**Xử phạt:** {config.config['punishment']}")

@bot.event
async def on_guild_role_create(role):
    if not config.config["enabled"]:
        return
    
    await asyncio.sleep(DELAY)
    guild = role.guild
    
    # Kiểm tra role có quyền nguy hiểm không
    dangerous_perms = ["administrator", "ban_members", "kick_members", "manage_guild", "manage_roles", "manage_channels"]
    
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.role_create):
        if entry.user.bot:
            return
        
        if is_owner(entry.user) or is_admin(entry.user):
            return
        
        # Kiểm tra nếu role mới có quyền nguy hiểm
        for perm in dangerous_perms:
            if getattr(role.permissions, perm):
                await asyncio.sleep(ACTION_DELAY)
                await punish_user(entry.user, "Tạo role với quyền nguy hiểm")
                await role.delete()
                
                await send_log(guild, "⚠️ CẢNH BÁO!", 
                              f"**User:** {entry.user.mention}\n**Hành động:** Tạo role nguy hiểm\n**Role:** {role.name}")
                break

@bot.event
async def on_webhooks_update(channel):
    if not config.config["enabled"]:
        return
    
    await asyncio.sleep(DELAY)
    guild = channel.guild
    
    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.webhook_create):
        if entry.user.bot:
            return
        
        if is_owner(entry.user) or is_admin(entry.user):
            return
        
        user_id = entry.user.id
        current_time = datetime.now()
        action_log[user_id].append(current_time)
        
        action_log[user_id] = [t for t in action_log[user_id] 
                               if current_time - t < timedelta(seconds=config.config["time_window"])]
        
        if len(action_log[user_id]) >= 2:  # Giới hạn webhook thấp hơn
            # Xóa webhook
            await asyncio.sleep(ACTION_DELAY)
            webhooks = await channel.webhooks()
            for webhook in webhooks:
                await webhook.delete()
            
            await punish_user(entry.user, "Tạo webhook spam")
            
            await send_log(guild, "🚨 PHÁT HIỆN SPAM WEBHOOK!", 
                          f"**User:** {entry.user.mention}\n**Hành động:** Tạo webhook spam")

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    # Chống spam mention
    if len(message.mentions) > 5:
        await asyncio.sleep(DELAY)
        await message.delete()
        await message.author.timeout(timedelta(minutes=30), reason="Spam mention")
        
        await send_log(message.guild, "⚠️ SPAM MENTION!", 
                      f"**User:** {message.author.mention}\n**Hành động:** Timeout 30 phút")
        return
    
    # Chống spam link
    if len(re.findall(r'https?://', message.content)) > 3:
        await asyncio.sleep(DELAY)
        await message.delete()
        await message.author.timeout(timedelta(minutes=10), reason="Spam link")
        return
    
    # Chống spam nội dung
    user_messages = action_log.get(f"msg_{message.author.id}", [])
    current_time = datetime.now()
    user_messages = [t for t in user_messages if current_time - t < timedelta(seconds=3)]
    
    if len(user_messages) >= 5:
        await asyncio.sleep(DELAY)
        await message.author.timeout(timedelta(minutes=5), reason="Spam nội dung")
        return
    
    action_log[f"msg_{message.author.id}"] = user_messages + [current_time]
    
    await bot.process_commands(message)

# ==================== COMMANDS ====================

@bot.command(name="setup")
@commands.has_permissions(administrator=True)
async def setup(ctx):
    """Thiết lập Anti-Nuke cho server"""
    embed = discord.Embed(
        title="🛡️ TITANIUM ANTI-NUKE SETUP",
        description="Đang thiết lập hệ thống bảo vệ...",
        color=discord.Color.blue()
    )
    msg = await ctx.send(embed=embed)
    
    await asyncio.sleep(DELAY)
    
    # Tạo kênh log nếu chưa có
    log_channel = discord.utils.get(ctx.guild.channels, name="🔒-anti-nuke-log")
    if not log_channel:
        log_channel = await ctx.guild.create_text_channel("🔒-anti-nuke-log")
        await log_channel.set_permissions(ctx.guild.default_role, send_messages=False)
    
    # Lưu log channel
    config.config["log_channels"][str(ctx.guild.id)] = log_channel.id
    log_channels[ctx.guild.id] = log_channel.id
    config.save_config()
    
    # Backup server
    await backup_guild(ctx.guild)
    
    embed = discord.Embed(
        title="✅ SETUP HOÀN TẤT!",
        description="Hệ thống Titanium Anti-Nuke đã được kích hoạt!",
        color=discord.Color.green()
    )
    embed.add_field(name="📁 Kênh Log", value=log_channel.mention, inline=True)
    embed.add_field(name="⚡ Độ Trễ", value=f"{DELAY}s", inline=True)
    embed.add_field(name="🛡️ Trạng Thái", value="✅ Đã bật", inline=True)
    embed.add_field(name="💾 Backup", value="✅ Đã tạo", inline=True)
    embed.add_field(name="⚙️ Xử Phạt", value=config.config["punishment"].upper(), inline=True)
    embed.add_field(name="📊 Giới Hạn", value=f"{config.config['max_actions']} hành động/{config.config['time_window']}s", inline=True)
    embed.add_field(name="👑 Owner", value=f"<@{OWNER_ID}>", inline=True)
    
    await msg.edit(embed=embed)

@bot.command(name="logchannel")
@commands.has_permissions(administrator=True)
async def set_log_channel(ctx, channel: discord.TextChannel = None):
    """Thiết lập kênh log"""
    if channel is None:
        channel = ctx.channel
    
    await asyncio.sleep(DELAY)
    
    config.config["log_channels"][str(ctx.guild.id)] = channel.id
    log_channels[ctx.guild.id] = channel.id
    config.save_config()
    
    embed = discord.Embed(
        title="✅ LOG CHANNEL ĐÃ ĐƯỢC THIẾT LẬP",
        description=f"Kênh log: {channel.mention}",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name="help")
async def help_command(ctx):
    """Hiển thị tất cả lệnh của bot"""
    embed = discord.Embed(
        title="🛡️ TITANIUM ANTI-NUKE",
        description="Hệ thống chống phá hoại server Discord mạnh mẽ nhất!",
        color=discord.Color.gold()
    )
    
    # Commands chính
    embed.add_field(
        name="📌 LỆNH CHÍNH",
        value="```\n"
              "l!setup - Thiết lập hệ thống\n"
              "l!help - Hiển thị menu này\n"
              "l!status - Kiểm tra trạng thái\n"
              "l!backup - Backup server\n"
              "l!restore - Khôi phục server\n"
              "l!logchannel [#kênh] - Đặt kênh log\n"
              "```",
        inline=False
    )
    
    # Commands cấu hình
    embed.add_field(
        name="⚙️ CẤU HÌNH",
        value="```\n"
              "l!punishment kick/ban/timeout - Đổi hình phạt\n"
              "l!threshold <số> - Đặt giới hạn hành động\n"
              "l!window <giây> - Đặt khoảng thời gian\n"
              "l!antinuke on/off - Bật/tắt hệ thống\n"
              "l!recovery on/off - Bật/tắt tự khôi phục\n"
              "```",
        inline=False
    )
    
    # Commands bảo vệ
    embed.add_field(
        name="🛡️ BẢO VỆ",
        value="```\n"
              "l!lockdown - Khóa kênh hiện tại\n"
              "l!unlock - Mở khóa kênh hiện tại\n"
              "l!lockall - Khóa tất cả kênh\n"
              "l!unlockall - Mở tất cả kênh\n"
              "l!purge <số> - Xóa tin nhắn\n"
              "```",
        inline=False
    )
    
    # Commands thông tin
    embed.add_field(
        name="📊 THÔNG TIN",
        value="```\n"
              "l!suspects - Xem danh sách nghi phạm\n"
              "l!check @user - Kiểm tra user\n"
              "l!serverinfo - Thông tin server\n"
              "```",
        inline=False
    )
    
    embed.set_footer(text=f"Bot: {bot.user.name} | Owner: {OWNER_ID} | Ping: {round(bot.latency * 1000)}ms")
    await ctx.send(embed=embed)

@bot.command(name="status")
@commands.has_permissions(administrator=True)
async def status(ctx):
    """Kiểm tra trạng thái hệ thống"""
    log_channel_id = config.config["log_channels"].get(str(ctx.guild.id))
    log_channel = ctx.guild.get_channel(int(log_channel_id)) if log_channel_id else None
    
    embed = discord.Embed(
        title="📊 TRẠNG THÁI HỆ THỐNG",
        color=discord.Color.green() if config.config["enabled"] else discord.Color.red()
    )
    embed.add_field(name="🛡️ Anti-Nuke", value="✅ Bật" if config.config["enabled"] else "❌ Tắt", inline=True)
    embed.add_field(name="⚡ Độ Trễ", value=f"{DELAY}s", inline=True)
    embed.add_field(name="⚙️ Xử Phạt", value=config.config["punishment"].upper(), inline=True)
    embed.add_field(name="📊 Giới Hạn", value=f"{config.config['max_actions']} lần/{config.config['time_window']}s", inline=True)
    embed.add_field(name="💾 Auto Recovery", value="✅ Bật" if config.config["auto_recovery"] else "❌ Tắt", inline=True)
    embed.add_field(name="📁 Log Channel", value=log_channel.mention if log_channel else "❌ Chưa cấu hình", inline=True)
    embed.add_field(name="👑 Owner", value=f"<@{OWNER_ID}>", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name="backup")
@commands.has_permissions(administrator=True)
async def backup(ctx):
    """Backup toàn bộ server"""
    await ctx.send("🔄 Đang backup server...")
    await backup_guild(ctx.guild)
    await asyncio.sleep(ACTION_DELAY)
    
    embed = discord.Embed(
        title="✅ BACKUP HOÀN TẤT",
        description=f"Đã backup {len(ctx.guild.channels)} kênh và {len(ctx.guild.roles)} role",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name="restore")
@commands.has_permissions(administrator=True)
async def restore(ctx):
    """Khôi phục server từ backup"""
    await ctx.send("🔄 Đang khôi phục server...")
    success = await restore_guild(ctx.guild)
    
    if success:
        embed = discord.Embed(
            title="✅ KHÔI PHỤC HOÀN TẤT",
            description="Server đã được khôi phục từ backup",
            color=discord.Color.green()
        )
    else:
        embed = discord.Embed(
            title="❌ KHÔNG CÓ BACKUP",
            description="Không tìm thấy dữ liệu backup",
            color=discord.Color.red()
        )
    
    await ctx.send(embed=embed)

@bot.command(name="punishment")
@commands.has_permissions(administrator=True)
async def set_punishment(ctx, mode: str):
    """Đặt hình phạt: kick, ban, timeout"""
    await asyncio.sleep(DELAY)
    if mode.lower() in ["kick", "ban", "timeout"]:
        config.config["punishment"] = mode.lower()
        config.save_config()
        await ctx.send(f"✅ Đã đặt hình phạt thành: **{mode.upper()}**")
    else:
        await ctx.send("❌ Sử dụng: `l!punishment kick/ban/timeout`")

@bot.command(name="threshold")
@commands.has_permissions(administrator=True)
async def set_threshold(ctx, amount: int):
    """Đặt giới hạn hành động"""
    await asyncio.sleep(DELAY)
    if amount > 0:
        config.config["max_actions"] = amount
        config.save_config()
        await ctx.send(f"✅ Đã đặt giới hạn thành: **{amount} hành động**")
    else:
        await ctx.send("❌ Số lượng phải lớn hơn 0")

@bot.command(name="window")
@commands.has_permissions(administrator=True)
async def set_window(ctx, seconds: int):
    """Đặt khoảng thời gian theo dõi"""
    await asyncio.sleep(DELAY)
    if seconds > 0:
        config.config["time_window"] = seconds
        config.save_config()
        await ctx.send(f"✅ Đã đặt khoảng thời gian thành: **{seconds} giây**")
    else:
        await ctx.send("❌ Thời gian phải lớn hơn 0")

@bot.command(name="antinuke")
@commands.has_permissions(administrator=True)
async def toggle_antinuke(ctx, mode: str):
    """Bật/tắt hệ thống anti-nuke"""
    await asyncio.sleep(DELAY)
    if mode.lower() == "on":
        config.config["enabled"] = True
        config.save_config()
        await ctx.send("✅ Anti-Nuke đã được **BẬT**")
    elif mode.lower() == "off":
        config.config["enabled"] = False
        config.save_config()
        await ctx.send("❌ Anti-Nuke đã được **TẮT**")
    else:
        await ctx.send("❌ Sử dụng: `l!antinuke on/off`")

@bot.command(name="recovery")
@commands.has_permissions(administrator=True)
async def toggle_recovery(ctx, mode: str):
    """Bật/tắt tự động khôi phục"""
    await asyncio.sleep(DELAY)
    if mode.lower() == "on":
        config.config["auto_recovery"] = True
        config.save_config()
        await ctx.send("✅ Auto Recovery đã được **BẬT**")
    elif mode.lower() == "off":
        config.config["auto_recovery"] = False
        config.save_config()
        await ctx.send("❌ Auto Recovery đã được **TẮT**")
    else:
        await ctx.send("❌ Sử dụng: `l!recovery on/off`")

@bot.command(name="lockdown")
@commands.has_permissions(manage_channels=True)
async def lockdown(ctx):
    """Khóa kênh hiện tại"""
    await asyncio.sleep(ACTION_DELAY)
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("🔒 Kênh đã được khóa!")

@bot.command(name="unlock")
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    """Mở khóa kênh hiện tại"""
    await asyncio.sleep(ACTION_DELAY)
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("🔓 Kênh đã được mở khóa!")

@bot.command(name="lockall")
@commands.has_permissions(administrator=True)
async def lockall(ctx):
    """Khóa tất cả kênh"""
    for channel in ctx.guild.channels:
        await asyncio.sleep(DELAY)
        if isinstance(channel, discord.TextChannel):
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)
    
    await ctx.send("🔒 Tất cả kênh đã được khóa!")

@bot.command(name="unlockall")
@commands.has_permissions(administrator=True)
async def unlockall(ctx):
    """Mở tất cả kênh"""
    for channel in ctx.guild.channels:
        await asyncio.sleep(DELAY)
        if isinstance(channel, discord.TextChannel):
            await channel.set_permissions(ctx.guild.default_role, send_messages=True)
    
    await ctx.send("🔓 Tất cả kênh đã được mở khóa!")

@bot.command(name="purge")
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    """Xóa tin nhắn"""
    await asyncio.sleep(ACTION_DELAY)
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"✅ Đã xóa {len(deleted) - 1} tin nhắn!", delete_after=3)

@bot.command(name="suspects")
@commands.has_permissions(administrator=True)
async def suspects(ctx):
    """Xem danh sách nghi phạm"""
    embed = discord.Embed(
        title="🚨 DANH SÁCH NGHI PHẠM",
        color=discord.Color.red()
    )
    
    if suspicious_users:
        for user_id, info in suspicious_users.items():
            user = ctx.guild.get_member(user_id)
            if user:
                embed.add_field(
                    name=user.name,
                    value=f"Lý do: {info['reason']}\nThời gian: {info['time'].strftime('%H:%M:%S %d/%m/%Y')}",
                    inline=False
                )
    else:
        embed.description = "Không có nghi phạm nào!"
    
    await ctx.send(embed=embed)

@bot.command(name="check")
@commands.has_permissions(administrator=True)
async def check_user(ctx, member: discord.Member):
    """Kiểm tra thông tin user"""
    embed = discord.Embed(
        title=f"🔍 KIỂM TRA: {member.name}",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="ID", value=member.id, inline=True)
    embed.add_field(name="Tạo tài khoản", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="Tham gia server", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="Owner", value="✅ Có" if is_owner(member) else "❌ Không", inline=True)
    embed.add_field(name="Admin", value="✅ Có" if is_admin(member) else "❌ Không", inline=True)
    embed.add_field(name="Nghi phạm", value="⚠️ Có" if member.id in suspicious_users else "✅ Không", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name="serverinfo")
async def serverinfo(ctx):
    """Xem thông tin server"""
    guild = ctx.guild
    embed = discord.Embed(
        title=f"📊 {guild.name}",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Owner", value=guild.owner.mention, inline=True)
    embed.add_field(name="Bot Owner", value=f"<@{OWNER_ID}>", inline=True)
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Channels", value=len(guild.channels), inline=True)
    embed.add_field(name="Roles", value=len(guild.roles), inline=True)
    embed.add_field(name="Created", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="Boost Level", value=guild.premium_tier, inline=True)
    
    await ctx.send(embed=embed)

# Chạy bot
bot.run('YOUR_BOT_TOKEN')
