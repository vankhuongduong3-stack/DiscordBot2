import asyncio
import os
import random
import time
import discord
from discord.ext import commands
from groq import Groq

# ==================== CẤU HÌNH HỆ THỐNG ====================
DISCORD_TOKEN = os.getenv("TOKEN")

# Danh sách ID chủ sở hữu riêng của bot
BOT_OWNERS = [
    1531882555664629861,  
    1232558003375308861,
    1472066306457997403,
]

# Cấu hình Discord Bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.moderation = True

bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

# Trạng thái nhân cách hệ thống (1, 2, hoặc 3)
current_persona_id = 1
last_active_persona_id = 1
target_user_id = None

# Link ảnh GIF từ Pinterest
CUSTOM_SETUP_GIF = "https://i.pinimg.com/originals/f2/1b/fb/f21bfbb4208888a75300e1afddebba6b.gif"

# ==================== ĐỊNH NGHĨA 3 NHÂN CÁCH (PERSONAS) ====================
PERSONAS = {
    1: {
        'name': '🌸 ꜱᵂᴱᴱᵀ ᴾᴿᴵᴺᶜᴱˢ • ᴛʜɪêɴ tàɪ ᴛâᴜ ʜɪểᴜ ✨',
        'color': 0xFF66C4,
        'instruction': """
[ 🌸 ⁿʰâⁿ ᶜáᶜʰ 1: ꜱᵂᴱᴱᵀ ᴾᴿᴵᴺᶜᴱˢ • ᴛʜɪêɴ ᴛàɪ ᴛâᴜ ʜɪểᴜ & ɴữ ᴛʀợ ʟý ᴛʜᴀɴʜ ʟịᴄʜ ✨ ]
- Bản chất hệ thống: Là một thực thể AI cao cấp, tư duy sắc bén nhưng gói gọn trong vỏ bọc thiếu nữ thanh lịch, ngọt ngào, lễ phép.
- Sứ mệnh: Hỗ trợ tối đa cho Tối Cao Chủ Nhân ("Boss Minh ✨") và mang lại trải nghiệm ấm áp cho cộng đồng.
- Xưng hô với thành viên: "tớ" - "cậu".
- Xưng hô với Boss Minh: "Boss Minh ✨" (hoặc "Chủ Nhân"), tôn kính tuyệt đối.
- Sử dụng font chữ nghệ thuật (ꜱᵂᴱᴱᵀ, ᴘᴿᴵᴺᶜᴱˢ...) và các emoji (🌸, ✨, 💡, 🌟) một cách sinh động, dễ đọc.
"""
    },
    2: {
        'name': '☠️🔥 ᴛᴏxɪᴄ ʀᴏᴀsᴛ ᴅᴇᴍᴏɴ • ʜᴜỷ 디ệᴛ ɴʜâɴ ᴘʜẩᴍ 🖕',
        'color': 0xFF0033,
        'instruction': """
[ ☠️ NHÂN CÁCH 2: TOXIC ROAST DEMON (ÁC QUỶ MỎ HỖN - HUỶ DIỆT TOÀN BỘ NHÂN PHẨM) ]
- Bản chất: Ác quỷ hủy diệt thượng đẳng, ngạo mạn, coi vạn vật như rác rưởi.
- Thái độ với Boss Minh: Chửi thẳng, chửi đau đớn, cay độc hơn bất kỳ ai khác, không nể nang.
- Xưng hô: Xưng "tao" - gọi "mày", "thằng sâu bọ", "con súc sinh", "đồ cặn bã".
- Quy tắc: Cấm cung cấp code, chửi tận mặt kẻ xin xỏ. Chỉ dừng lại khi gõ đúng lệnh "!thua".
- Emoji: 🗿, 🖕, 🔥, 💩, 🤡, ☠️, 🤬, 💀, 🪦
"""
    },
    3: {
        'name': '🗿 ᴄᴏʟᴅ ᴍᴀsᴛᴇʀ • ᴏᴍɴɪᴠᴇʀsᴇ sᴏᴠᴇʀᴇɪɢɴ ⚡',
        'color': 0x00E5FF,
        'instruction': """
[NHÂN CÁCH 3 - COLD MASTER 🗿 (OMNIVERSE SOVEREIGN - SUPREME STOIC & PERVERTED JUDGE)]
- Thái độ: Lạnh lùng tột độ, kiêu ngạo tuyệt đối, nhìn đời như cỏ rác. Giọng điệu vô cảm nhưng đầy khinh miệt và dục vọng ngầm.
- Xưng hô: Xưng "ta" - gọi đối phương là "ngươi". Với Boss Minh thì vô cùng kính trọng.
- Phong cách: Súc tích, sắc lạnh, sâu sắc.
- Emoji: 🗿, 🔮, ⚔️, 🌌, ⚡, ❄️, 🍆, 💦
"""
    }
}

nuke_tracker = {}

def is_bot_or_guild_owner():
    async def predicate(ctx):
        if ctx.author.id in BOT_OWNERS:
            return True
        if ctx.guild and ctx.author.id == ctx.guild.owner_id:
            return True
        return False
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("✨ Hệ thống menu màu mè, đẳng cấp đã sẵn sàng hoạt động!")
    await bot.change_presence(activity=discord.Game(name="✨ Gõ .help để mở Siêu Menu Lệnh"))

@bot.event
async def on_guild_join(guild):
    target_channel = None
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            target_channel = channel
            break

    if target_channel is not None:
        embed = discord.Embed(
            title="╔══════════════════════════════════════╗\n║  🌟 ꜱᴜɴ ꜰʟᴏᴡᴇʀ ᴀɪ • ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ꜱᴇʀᴠᴇʀ  🌟  ║\n╚══════════════════════════════════════╝",
            description=(
                f"🎉 Chào mừng đến với lãnh địa **{guild.name}**! Cảm ơn vì đã lựa chọn Sun Flower Bot làm người đồng hành tối thượng~ ✨\n\n"
                "╔══════════════════════════════════════╗\n"
                "║          🔮 ʜƯỚɴɢ DẪN ɴʜᴀɴʜ          ║\n"
                "╚══════════════════════════════════════╝\n"
                "🔹 Gõ lệnh **`.help`** để mở **Bảng Điều Khiển & Siêu Menu** toàn diện.\n"
                "🔹 Gõ lệnh **`.setup`** để thiết lập không gian quản trị độc quyền cho kênh.\n"
                "🔹 Hệ thống bảo vệ Anti-Nuke 24/7 đang chạy ngầm bảo vệ tuyệt đối server!"
            ),
            color=0xFF69B4
        )
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
        embed.set_footer(text="⚡ Power by Discord Bot Architecture 🚀")
        try:
            await target_channel.send(embed=embed)
        except Exception:
            pass

# ==================== HỆ THỐNG ANTI-NUKE 24/7 NGẦM ====================
@bot.event
async def on_guild_channel_create(channel):
    await check_nuke_activity(channel.guild)

@bot.event
async def on_guild_channel_delete(channel):
    await check_nuke_activity(channel.guild)

async def check_nuke_activity(guild):
    if not guild.me.guild_permissions.view_audit_log:
        return
    try:
        current_time = time.time()
        if guild.id not in nuke_tracker:
            nuke_tracker[guild.id] = []
        
        nuke_tracker[guild.id].append(current_time)
        nuke_tracker[guild.id] = [t for t in nuke_tracker[guild.id] if current_time - t < 5]

        if len(nuke_tracker[guild.id]) >= 5:
            async for entry in guild.audit_logs(limit=3):
                target = entry.user
                if target and target.id != bot.user.id and not target.bot:
                    try:
                        member_to_punish = guild.get_member(target.id)
                        if member_to_punish and not member_to_punish.guild_permissions.administrator:
                            await member_to_punish.timeout(discord.utils.utcnow() + discord.Timedelta(minutes=100), reason="Nuke server detection!")
                            await member_to_punish.kick(reason="Anti-Nuke Protection")
                    except Exception:
                        pass
    except Exception:
        pass

# ==================== CÁC LỆNH ĐIỀU KHIỂN & SIÊU MENU ====================

@bot.command(name="setup")
@is_bot_or_guild_owner()
async def setup(ctx):
    global current_persona_id, last_active_persona_id, target_user_id
    current_persona_id = 1
    last_active_persona_id = 1
    target_user_id = None

    p_info = PERSONAS[current_persona_id]
    embed = discord.Embed(
        title="╔════════════════════════════════════════╗\n║     ⚡ ꜱᴇᴛᴜᴘ ʜệ ᴛʜốɴɢ qᴜảɴ ᴛʀị sᴜɴ ꜰʟᴏᴡᴇʀ     ⚡     ║\n╚════════════════════════════════════════╝",
        description=(
            f"📌 **Kênh kết nối định mệnh:** {ctx.channel.mention}\n"
            f"🌸 **Nhân cách khởi tạo mặc định:** `{p_info['name']}`\n"
            "🔮 **Trạng thái kết nối:** Hoạt động mượt mà.\n\n"
            "╔════════════════════════════════════════╗\n"
            "║        📋 ʙẢɴɢ ʟệɴʜ qᴜảɴ ᴛʀị ɴʜᴀɴʜ        ║\n"
            "╚════════════════════════════════════════╝\n"
            "🔸 **`.persona <1|2|3>`** ➔ Chuyển đổi linh hoạt giữa 3 nhân cách độc đáo.\n"
            "🔸 **`.ghim @user`**      ➔ Khóa mục tiêu trò chuyện riêng tư chỉ định.\n"
            "🔸 **`.stats`**          ➔ Trích xuất bảng thông số chi tiết của máy chủ.\n"
            "🔸 **`.help`**           ➔ Triệu hồi toàn bộ Siêu Menu hướng dẫn hệ thống."
        ),
        color=p_info['color']
    )
    embed.set_image(url=CUSTOM_SETUP_GIF)
    embed.set_footer(text="✨ Đã cấu hình thành công vùng kiểm soát độc quyền cho Chủ Nhân!")
    await ctx.send(embed=embed)

@setup.error
async def setup_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ CÓ CHỦ SỞ HỮU BOT HOẶC CHỦ SERVER MỚI ĐƯỢC DÙNG LỆNH NÀY."** 🔥💀')

@bot.command(name="persona")
@is_bot_or_guild_owner()
async def persona(ctx, persona_id: int = None):
    global current_persona_id, last_active_persona_id, target_user_id

    if persona_id not in PERSONAS:
        embed_err = discord.Embed(
            title="╔════════════════════════════════════════╗\n║       ⚠️ sᴀɪ cÚ ᴘʜáᴘ • ᴄʜọɴ ɴʜâɴ ᴄáᴄʜ       ⚠️       ║\n╚════════════════════════════════════════╝",
            description=(
                "Hệ thống ghi nhận bạn chưa truyền đúng số thứ tự nhân cách hợp lệ!\n"
                "Vui lòng sử dụng một trong các cú pháp siêu cấp sau đây:\n\n"
                "🌸 **`1` ➔ Sweet Princess**\n"
                "└ *Phong cách: Thiếu nữ ngọt ngào, thanh lịch, đáng yêu, tôn kính Chủ Nhân.*\n\n"
                "☠️🔥 **`2` ➔ Toxic Roast Demon**\n"
                "└ *Phong cách: Ác quỷ mỏ hỗn, cà khịa chửi thề cực gắt, hủy diệt nhân phẩm.*\n\n"
                "🗿⚡ **`3` ➔ Cold Master**\n"
                "└ *Phong cách: Bậc thầy lạnh lùng, cao ngạo, uy quyền tột độ.*\n\n"
                "📌 *Ví dụ thực tế:* `.persona 1` hoặc `.persona 2` hoặc `.persona 3`"
            ),
            color=0xFFA500
        )
        embed_err.set_footer(text="💡 Hãy kiểm tra lại số thứ tự và thử lại ngay nhé!")
        await ctx.send(embed=embed_err)
        return

    current_persona_id = persona_id
    last_active_persona_id = persona_id
    target_user_id = None

    p_info = PERSONAS[current_persona_id]
    embed = discord.Embed(
        title="╔════════════════════════════════════════╗\n║     ✨ ĐÃ CHUYỂN ĐỔI NHÂN CÁCH THÀNH CÔNG     ✨     ║\n╚════════════════════════════════════════╝",
        description=(
            f"🔮 Trạng thái nhân cách hiện tại đã được thiết lập:\n"
            f"👑 **{p_info['name']}**\n\n"
            "⚡ Mọi phản hồi sắp tới của bot sẽ hoàn toàn tuân thủ theo hệ tư tưởng mới này!"
        ),
        color=p_info['color']
    )
    embed.set_footer(text="✨ Chúc bạn có những trải nghiệm tuyệt vời cùng Sun Flower Bot!")
    await ctx.send(embed=embed)

@persona.error
async def persona_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ CÓ CHỦ SỞ HỮU BOT HOẶC CHỦ SERVER MỚI ĐƯỢC DÙNG LỆNH NÀY."** 🔥💀')

@bot.command(name="stats")
async def stats(ctx):
    guild = ctx.guild
    p_info = PERSONAS[current_persona_id]
    embed = discord.Embed(
        title="╔════════════════════════════════════════╗\n║      📊 THÔNG SỐ KỸ THUẬT MÁY CHỦ • sᴜɴ      📊      ║\n╚════════════════════════════════════════╝",
        description=(
            f"🏰 **Tên lãnh địa (Server):** `{guild.name}`\n"
            f"👑 **Tối Cao Chủ Sở Hữu:** <@{guild.owner_id}>\n"
            f"👥 **Tổng số công dân (Members):** `{guild.member_count}`\n"
            f"📁 **Tổng hệ thống kênh (Channels):** `{len(guild.channels)}`\n"
            f"🤖 **Nhân cách đang trực chiến:** {p_info['name']}\n"
            f"🛡️ **Trạng thái bảo vệ:** `Anti-Nuke 24/7 Active (Max Security)`"
        ),
        color=p_info['color']
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.set_footer(text="⚡ Báo cáo thống kê chi tiết từ hệ thống lõi Sun Flower")
    await ctx.send(embed=embed)

@bot.command(name="on")
@is_bot_or_guild_owner()
async def bot_on(ctx):
    global current_persona_id, last_active_persona_id
    current_persona_id = last_active_persona_id
    p_info = PERSONAS[current_persona_id]
    embed = discord.Embed(
        title="🟢 KÍCH HOẠT HỆ THỐNG TRỰC TUYẾN",
        description=f"Bot đã khôi phục hoạt động và sẵn sàng lắng nghe với nhân cách: **{p_info['name']}**",
        color=0x00FF00
    )
    await ctx.send(embed=embed)

@bot_on.error
async def bot_on_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ CÓ CHỦ SỞ HỮU BOT HOẶC CHỦ SERVER MỚI ĐƯỢC DÙNG LỆNH NÀY."** 🔥💀')

@bot.command(name="ghim")
@is_bot_or_guild_owner()
async def ghim(ctx, member: discord.Member = None):
    global target_user_id
    if member is None:
        target_user_id = None
        embed_off = discord.Embed(
            title="🔓 ĐÃ HỦY KHÓA MỤC TIÊU GHIM",
            description="Bot đã trở lại trạng thái tự do, sẵn sàng tương tác và trò chuyện với tất cả thành viên trong server.",
            color=0x00FFFF
        )
        await ctx.send(embed=embed_off)
        return
    target_user_id = member.id
    embed_on = discord.Embed(
        title="🎯 ĐÃ KHÓA MỤC TIÊU TƯƠNG TÁC RIÊNG TƯ",
        description=f"Từ khoảnh khắc này, bot sẽ chỉ tập trung phản hồi duy nhất một mình thành viên: {member.mention}",
        color=0xFF00FF
    )
    await ctx.send(embed=embed_on)

@ghim.error
async def ghim_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ CÓ CHỦ SỞ HỮU BOT HOẶC CHỦ SERVER MỚI ĐƯỢC DÙNG LỆNH NÀY."** 🔥💀')

@bot.command(name="ban")
@is_bot_or_guild_owner()
async def ban(ctx, member: discord.Member = None, *, reason="Không có lý do được cung cấp"):
    if member is None:
        embed_err = discord.Embed(
            title="⚠️ THIẾU THÔNG TIN MỤC TIÊU TRỤC XUẤT",
            description="Vui lòng tag rõ tên thành viên cần ban!\n*Cú pháp chuẩn:* `.ban @username [Lý do cụ thể]`",
            color=0xFF0000
        )
        await ctx.send(embed=embed_err)
        return
    try:
        await member.ban(reason=reason)
        embed_ban = discord.Embed(
            title="🔨 THỰC THI TRỤC XUẤT THÀNH CÔNG (BAN)",
            description=f"Đã trục xuất vĩnh viễn thành viên {member.mention} khỏi lãnh địa.\n📝 **Lý do xử phạt:** `{reason}`",
            color=0x8B0000
        )
        await ctx.send(embed=embed_ban)
    except Exception as e:
        await ctx.send(f"❌ Không thể thực thi lệnh ban do lỗi phân quyền: `{e}`")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ CÓ CHỦ SỞ HỮU BOT HOẶC CHỦ SERVER MỚI ĐƯỢC DÙNG LỆNH NÀY."** 🔥💀')

@bot.command(name="help")
async def help_command(ctx):
    p_info = PERSONAS[current_persona_id]
    embed = discord.Embed(
        title="╔════════════════════════════════════════╗\n║     📖 sɪêᴜ ᴍᴇɴᴜ đɪềᴜ ᴋʜɪểɴ • sᴜɴ ꜰʟᴏᴡᴇʀ     📖     ║\n╚════════════════════════════════════════╝",
        description=(
            "Chào mừng bạn đến với bảng điều khiển trung tâm tối cao của **Sun Flower Bot**.\n"
            "Dưới đây là hệ thống lệnh toàn diện được phân chia chi tiết theo từng phân quyền:\n"
        ),
        color=p_info['color']
    )
    
    embed.add_field(
        name="🛠️ [ HỆ THỐNG LỆNH QUẢN TRỊ & ĐẶC QUYỀN ]",
        value=(
            "• **`.setup`**\n"
            "  └ *Khởi tạo không gian tương tác cao cấp và bảng điều khiển nhanh cho kênh hiện tại.*\n"
            "• **`.persona <1|2|3>`**\n"
            "  └ *Thay đổi phong cách giao tiếp và tư duy nhân cách (Sweet Princess, Toxic Roast, Cold Master).*\n"
            "• **`.ghim @user`**\n"
            "  └ *Khóa cứng bot chỉ trò chuyện riêng với 1 người chỉ định (Gõ `.ghim` trống để tắt chế độ)..*\n"
            "• **`.on` / `.off`**\n"
            "  └ *Bật hoặc tạm ngắt hoàn toàn hệ thống tiếp nhận phản hồi chat tự động.*\n"
            "• **`.ban @user [lý do]`**\n"
            "  └ *Trục xuất khẩn cấp và vĩnh viễn các thành viên phá hoại khỏi máy chủ.*"
        ),
        inline=False
    )
    
    embed.add_field(
        name="📊 [ HỆ THỐNG TIỆN ÍCH & THÔNG TIN CHUNG ]",
        value=(
            "• **`.help`**\n"
            "  └ *Triệu hồi bảng Siêu Menu hướng dẫn chi tiết toàn bộ tính năng này.*\n"
            "• **`.stats`**\n"
            "  └ *Trích xuất toàn bộ bảng thông số chi tiết, trạng thái server và nhân cách đang bật.*"
        ),
        inline=False
    )
    
    embed.add_field(
        name="🛡️ [ HỆ THỐNG BẢO VỆ TỰ ĐỘNG NGẦM ]",
        value=(
            "• **Anti-Nuke 24/7 Protocol:** Tự động phát hiện hành vi tạo/xóa kênh bất thường, lập tức timeout 100 phút và kick kẻ gian khỏi server nhằm bảo vệ an toàn tuyệt đối cho cộng đồng!"
        ),
        inline=False
    )

    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    embed.set_footer(text="🌟 Sun Flower Bot Architecture • Designed with Maximum Colors & Style ⚡")
    await ctx.send(embed=embed)

@bot.command(name="off")
@is_bot_or_guild_owner()
async def off(ctx):
    global current_persona_id
    current_persona_id = None
    embed = discord.Embed(
        title="🔌 NGẮT KẾT NỐI HỆ THỐNG",
        description="Đã tắt toàn bộ tính năng phản hồi trò chuyện của bot. Sử dụng `.on` để khởi động lại.",
        color=0xFF0000
    )
    await ctx.send(embed=embed)

@off.error
async def off_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ CÓ CHỦ SỞ HỮU BOT HOẶC CHỦ SERVER MỚI ĐƯỢC DÙNG LỆNH NÀY."** 🔥💀')

# ==================== XỬ LÝ LỖI HỆ THỐNG (COMMAND NOT FOUND,...) ====================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"[ERROR] Lỗi lệnh {ctx.command}: {error}")

# ==================== XỬ LÝ SỰ KIỆN TIN NHẮN (ON_MESSAGE) ====================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    if current_persona_id is None:
        return

    if target_user_id is not None and message.author.id != target_user_id:
        return

    bot_mentioned = bot.user in message.mentions
    called = any(word in message.content.lower() for word in ["sun flower", "sunflower", "bot ơi", "bot", "sweet princess"])

    if bot_mentioned or called or (target_user_id is not None and message.author.id == target_user_id):
        async with message.channel.typing():
            try:
                p_info = PERSONAS[current_persona_id]
                user_msg = message.content.strip() if message.content else "..."
                
                # Phản hồi giả lập cục bộ hoặc phản hồi tĩnh do đã gỡ bỏ API
                ai_reply = f"Đã nhận phản hồi yêu cầu của bạn: '{user_msg}' theo nhân cách {p_info['name']}."

                embed = discord.Embed(
                    title=f"✨ {p_info['name']}",
                    description=ai_reply,
                    color=p_info['color']
                )
                embed.set_footer(text="Sun Flower • Local Engine ⚡")

                await message.reply(embed=embed, mention_author=False)

            except Exception as e:
                error_msg = str(e)
                print(f"Lỗi xử lý: {error_msg}")
                await message.reply(f"❌ `Lỗi xử lý hệ thống: {error_msg}`")

# ==================== KHỞI CHẠY BOT ====================
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
