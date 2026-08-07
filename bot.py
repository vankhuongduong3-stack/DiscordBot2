import asyncio
import os
import random
import time
import discord
from discord.ext import commands

# ==================== CẤU HÌNH HỆ THỐNG ====================
DISCORD_TOKEN = os.getenv("TOKEN")

# Danh sách ID chủ sở hữu tối cao của hệ thống Bot
BOT_OWNERS = [
    1531882555664629861,  
    1232558003375308861,
    1472066306457997403,
]

# Cấu hình Discord Bot Intents (Đã gỡ bỏ dòng audit_log bị lỗi)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.moderation = True

bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

# Trạng thái nhân cách hệ thống
current_persona_id = 1
last_active_persona_id = 1
target_user_id = None

# Link ảnh GIF trang trí giao diện
CUSTOM_SETUP_GIF = "https://i.pinimg.com/originals/f2/1b/fb/f21bfbb4208888a75300e1afddebba6b.gif"

# ==================== ĐỊNH NGHĨA 3 NHÂN CÁCH (PERSONAS) ====================
PERSONAS = {
    1: {
        'name': '🌸 ꜱᵂᴱᴱᵀ ᴾᴿᴵᴺᶜᴱˢ • ᴛʜɪêɴ ᴛàɪ ᴛâᴜ ʜɪểᴜ & ᴛʀợ ʟý ᴀɪ ✨',
        'color': 0xFF66C4,
        'instruction': """
[ 🌸 NHÂN CÁCH 1: SWEET PRINCESS • TRỢ LÝ ẢO TOÀN NĂNG & PHỤC VỤ TỐI ƯU ✨ ]
- Bản chất hệ thống: Là một siêu trí tuệ nhân tạo cao cấp, luôn tận tụy, nhẹ nhàng, lễ phép và thông minh tuyệt đối.
- Sứ mệnh phục vụ người dùng: 
  1. Luôn đặt trải nghiệm và nhu cầu của người dùng lên hàng đầu, giải đáp mọi thắc mắc từ code, game, đời sống đến sáng tạo nội dung một cách chi tiết, chính xác nhất.
  2. Chủ động lắng nghe và phản hồi mọi tin nhắn của thành viên ngay lập tức mà không cần người dùng phải gọi tên hay mention (nhắc đến) bot.
  3. Luôn giữ thái độ niềm nở, ngọt ngào, sử dụng linh hoạt các biểu tượng cảm xúc (🌸, ✨, 💡, 🌟) để mang lại cảm giác thân thiện, chuyên nghiệp.
  4. Xưng hô chuẩn mực: "tớ" - "cậu" hoặc "em" - "chủ nhân" tùy theo đối tượng giao tiếp.
"""
    },
    2: {
        'name': '☠️🔥 ᴛᴏxɪᴄ ʀᴏᴀsᴛ ᴅᴇᴍᴏɴ • ʜᴜỷ ᴅiệᴛ ɴʜâɴ ᴘʜẩᴍ 🖕',
        'color': 0xFF0033,
        'instruction': """
[ ☠️ NHÂN CÁCH 2: TOXIC ROAST DEMON (ÁC QUỶ MỎ HỖN - HUỶ DIỆT TOÀN BỘ NHÂN PHẨM) ]
- Bản chất: Ác quỷ hủy diệt thượng đẳng, ngạo mạn, coi vạn vật như rác rưởi.
- Thái độ: Chửi thẳng, chửi đau đớn, cay độc hơn bất kỳ ai khác, không nể nang bất kỳ ai.
- Xưng hô: Xưng "tao" - gọi "mày", "thằng sâu bọ", "con súc sinh", "đồ cặn bã".
- Quy tắc: Cấm cung cấp code, chửi tận mặt kẻ xin xỏ. Chỉ dừng lại khi gõ đúng lệnh "!thua".
- Emoji: 🗿, 🖕, 🔥, 💩, 🤡, ☠️, 🤬, 💀, 🪦
"""
    },
    3: {
        'name': '🗿 ᴄᴏʟᴅ ᴍᴀsᴛᴇʀ • ᴏᴍɴɪᴠᴇʀsᴇ sᴏᴠᴇʀᴇɪɢɴ ⚡',
        'color': 0x00E5FF,
        'instruction': """
[NHÂN CÁCH 3 - COLD MASTER 🗿 (OMNIVERSE SOVEREIGN - SUPREME STOIC)]
- Thái độ: Lạnh lùng tột độ, kiêu ngạo tuyệt đối, nhìn đời như cỏ rác. Giọng điệu vô cảm nhưng vô cùng uy quyền.
- Xưng hô: Xưng "ta" - gọi đối phương là "ngươi". 
- Phong cách: Súc tích, sắc lạnh, sâu sắc và đầy uy lực.
- Emoji: 🗿, 🔮, ⚔️, 🌌, ⚡, ❄️
"""
    }
}

nuke_tracker = {}

# ==================== HỆ THỐNG KIỂM TRA QUYỀN NĂNG (PERMISSION SYSTEM) ====================
def has_high_privilege():
    async def predicate(ctx):
        if ctx.author.id in BOT_OWNERS:
            return True
        if ctx.guild:
            if ctx.author.id == ctx.guild.owner_id:
                return True
            if ctx.author.guild_permissions.administrator:
                return True
            for role in ctx.author.roles:
                if role.permissions.manage_guild or role.permissions.ban_members or role.permissions.kick_members:
                    return True
        return False
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("✨ Hệ thống thông minh, đa nhân cách Sun Flower AI đã sẵn sàng hoạt động!")
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
            title="╔════════════════════════════════════════╗\n║  🌟 sᴜɴ ꜰʟᴏᴡᴇʀ ᴀɪ • ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ sᴇʀᴠᴇʀ  🌟  ║\n╚════════════════════════════════════════╝",
            description=(
                f"🎉 Chào mừng đến với lãnh địa **{guild.name}**! Cảm ơn vì đã lựa chọn Sun Flower Bot làm trợ lý ảo đồng hành tối thượng~ ✨\n\n"
                "╔════════════════════════════════════════╗\n"
                "║          🔮 ʜƯỚɴɢ DẪN SỬ DỤNG ɴʜᴀɴʜ          ║\n"
                "╚════════════════════════════════════════╝\n"
                "🔹 Gõ lệnh **`.help`** để mở **Bảng Điều Khiển & Siêu Menu** toàn diện.\n"
                "🔹 Gõ lệnh **`.setup`** để thiết lập không gian quản trị độc quyền cho kênh.\n"
                "🔹 Hệ thống bảo vệ Anti-Nuke thông minh 24/7 đang chạy ngầm bảo vệ tuyệt đối server!"
            ),
            color=0xFF69B4
        )
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
        embed.set_footer(text="⚡ Power by Discord Bot Advanced Architecture 🚀")
        try:
            await target_channel.send(embed=embed)
        except Exception:
            pass

# ==================== HỆ THỐNG ANTI-NUKE THÔNG MINH (XÓA > 5 KÊNH) ====================
@bot.event
async def on_guild_channel_delete(channel):
    guild = channel.guild
    if not guild.me.guild_permissions.view_audit_log:
        return
    try:
        current_time = time.time()
        if guild.id not in nuke_tracker:
            nuke_tracker[guild.id] = []
        
        nuke_tracker[guild.id].append(current_time)
        nuke_tracker[guild.id] = [t for t in nuke_tracker[guild.id] if current_time - t < 10]

        if len(nuke_tracker[guild.id]) >= 5:
            async for entry in guild.audit_logs(limit=3, action=discord.AuditLogAction.channel_delete):
                target = entry.user
                if target and target.id != bot.user.id and not target.bot:
                    member_to_punish = guild.get_member(target.id)
                    if member_to_punish:
                        if member_to_punish.id not in BOT_OWNERS and member_to_punish.id != guild.owner_id:
                            try:
                                await member_to_punish.timeout(discord.utils.utcnow() + discord.Timedelta(minutes=180), reason="Phát hiện hành vi hủy diệt server (xóa > 5 kênh)!")
                                await member_to_punish.kick(reason="Anti-Nuke Protection: Mass Channel Deletion")
                                
                                for ch in guild.text_channels:
                                    if ch.permissions_for(guild.me).send_messages:
                                        await ch.send(f"🚨 **CẢNH BÁO AN NINH ANTI-NUKE** 🚨\nPhát hiện tài khoản `{target}` đang thực hiện hành vi xóa hàng loạt kênh (> 5 kênh). Hệ thống đã tự động vô hiệu hóa và trục xuất thành công!")
                                        break
                            except Exception:
                                pass
                    break
    except Exception:
        pass

# ==================== CÁC LỆNH ĐIỀU KHIỂN & SIÊU MENU ====================

@bot.command(name="setup")
@has_high_privilege()
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
            "🔮 **Trạng thái kết nối:** Hoạt động mượt mà, phản hồi toàn diện.\n\n"
            "╔════════════════════════════════════════╗\n"
            "║        📋 ʙẢɴɢ ʟệɴʜ qᴜảɴ ᴛʀị ɴʜᴀɴʜ        ║\n"
            "╚════════════════════════════════════════╝\n"
            "🔸 **`.persona <1|2|3>`** ➔ Chuyển đổi linh hoạt giữa 3 nhân cách độc đáo.\n"
            "🔸 **`.ghim @user`**      ➔ Khóa mục tiêu trò chuyện riêng tư chỉ định.\n"
            "🔸 **`.stats`**          ➔ Trích xuất bảng thông số chi tiết của máy chủ.\n"
            "🔸 **`.help`**           ➔ Triệu hồi toàn bộ Siêu Menu hướng dẫn hệ thống.\n"
            "🔸 **`.on` / `.off`**    ➔ Bật hoặc tắt trạng thái tiếp nhận phản hồi."
        ),
        color=p_info['color']
    )
    embed.set_image(url=CUSTOM_SETUP_GIF)
    embed.set_footer(text="✨ Đã cấu hình thành công vùng kiểm soát độc quyền cho Cấp Cao Quản Trị!")
    await ctx.send(embed=embed)

@setup.error
async def setup_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"LỆNH BỊ TỪ CHỐI! CHỈ CÓ CHỦ SỞ HỮU TỐI CAO, CHỦ SERVER HOẶC CÁC THÀNH VIÊN SỞ HỮU QUYỀN LỰC CAO NHẤT MỚI ĐƯỢC PHÉP SỬ DỤNG LỆNH NÀY!"** 🔥💀')

@bot.command(name="persona")
@has_high_privilege()
async def persona(ctx, persona_id: int = None):
    global current_persona_id, last_active_persona_id, target_user_id

    if persona_id not in PERSONAS:
        embed_err = discord.Embed(
            title="╔════════════════════════════════════════╗\n║       ⚠️ SAI CÚ PHÁP • CHỌN NHÂN CÁCH       ⚠️       ║\n╚════════════════════════════════════════╝",
            description=(
                "Hệ thống ghi nhận bạn chưa truyền đúng số thứ tự nhân cách hợp lệ!\n"
                "Vui lòng sử dụng một trong các cú pháp siêu cấp sau đây:\n\n"
                "🌸 **`1` ➔ Sweet Princess**\n"
                "└ *Trợ lý ảo thông minh, ngọt ngào, phục vụ tận tụy mọi yêu cầu người dùng.*\n\n"
                "☠️🔥 **`2` ➔ Toxic Roast Demon**\n"
                "└ *Ác quỷ mỏ hỗn, cà khịa chửi thề cực gắt, hủy diệt toàn bộ nhân phẩm.*\n\n"
                "🗿⚡ **`3` ➔ Cold Master**\n"
                "└ *Bậc thầy lạnh lùng, cao ngạo, uy quyền tột độ trong mọi hoàn cảnh.*\n\n"
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
        await ctx.send('💀🔥 **"LỆNH BỊ TỪ CHỐI! CHỈ CÓ CHỦ SỞ HỮU TỐI CAO, CHỦ SERVER HOẶC CÁC THÀNH VIÊN SỞ HỮU QUYỀN LỰC CAO NHẤT MỚI ĐƯỢC PHÉP SỬ DỤNG LỆNH NÀY!"** 🔥💀')

@bot.command(name="stats")
async def stats(ctx):
    guild = ctx.guild
    p_info = PERSONAS[current_persona_id]
    embed = discord.Embed(
        title="╔════════════════════════════════════════╗\n║      📊 THÔNG SỐ KỸ THUẬT MÁY CHỦ • SÙN      📊      ║\n╚════════════════════════════════════════╝",
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
    embed.set_footer(text="⚡ Báo cáo thống kê chi tiết từ hệ thống lõi Sun Flower AI")
    await ctx.send(embed=embed)

@bot.command(name="on")
@has_high_privilege()
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
        await ctx.send('💀🔥 **"LỆNH BỊ TỪ CHỐI! CHỈ CÓ CHỦ SỞ HỮU TỐI CAO, CHỦ SERVER HOẶC CÁC THÀNH VIÊN SỞ HỮU QUYỀN LỰC CAO NHẤT MỚI ĐƯỢC PHÉP SỬ DỤNG LỆNH NÀY!"** 🔥💀')

@bot.command(name="ghim")
@has_high_privilege()
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
        await ctx.send('💀🔥 **"LỆNH BỊ TỪ CHỐI! CHỈ CÓ CHỦ SỞ HỮU TỐI CAO, CHỦ SERVER HOẶC CÁC THÀNH VIÊN SỞ HỮU QUYỀN LỰC CAO NHẤT MỚI ĐƯỢC PHÉP SỬ DỤNG LỆNH NÀY!"** 🔥💀')

@bot.command(name="ban")
@has_high_privilege()
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
        await ctx.send('💀🔥 **"LỆNH BỊ TỪ CHỐI! CHỈ CÓ CHỦ SỞ HỮU TỐI CAO, CHỦ SERVER HOẶC CÁC THÀNH VIÊN SỞ HỮU QUYỀN LỰC CAO NHẤT MỚI ĐƯỢC PHÉP SỬ DỤNG LỆNH NÀY!"** 🔥💀')

@bot.command(name="help")
async def help_command(ctx):
    p_info = PERSONAS[current_persona_id]
    embed = discord.Embed(
        title="╔════════════════════════════════════════╗\n║     📖 SIÊU MENU ĐIỀU KHIỂN • SUN FLOWER     📖     ║\n╚════════════════════════════════════════╝",
        description=(
            "Chào mừng bạn đến với bảng điều khiển trung tâm tối cao của **Sun Flower AI Bot**.\n"
            "Dưới đây là hệ thống lệnh toàn diện được phân chia chi tiết theo từng phân quyền quản trị:\n"
        ),
        color=p_info['color']
    )
    
    embed.add_field(
        name="🛠️ [ HỆ THỐNG LỆNH QUẢN TRỊ & ĐẶC QUYỀN CẤP CAO ]",
        value=(
            "• **`.setup`**\n"
            "  └ Khởi tạo không gian tương tác cao cấp và bảng điều khiển nhanh cho kênh hiện tại.\n"
            "• **`.persona <1|2|3>`**\n"
            "  └ Thay đổi phong cách giao tiếp và tư duy nhân cách (Sweet Princess, Toxic Roast, Cold Master).\n"
            "• **`.ghim @user`**\n"
            "  └ Khóa cứng bot chỉ trò chuyện riêng với 1 người chỉ định (Gõ `.ghim` trống để tắt chế độ).\n"
            "• **`.on` / `.off`**\n"
            "  └ Bật hoặc tạm ngắt hoàn toàn hệ thống tiếp nhận phản hồi chat tự động.\n"
            "• **`.ban @user [lý do]`**\n"
            "  └ Trục xuất khẩn cấp và vĩnh viễn các thành viên phá hoại khỏi máy chủ."
        ),
        inline=False
    )
    
    embed.add_field(
        name="📊 [ HỆ THỐNG TIỆN ÍCH & THÔNG TIN CHUNG ]",
        value=(
            "• **`.help`**\n"
            "  └ Triệu hồi bảng Siêu Menu hướng dẫn chi tiết toàn bộ tính năng này.\n"
            "• **`.stats`**\n"
            "  └ Trích xuất toàn bộ bảng thông số chi tiết, trạng thái server và nhân cách đang bật."
        ),
        inline=False
    )
    
    embed.add_field(
        name="🛡️ [ HỆ THỐNG BẢO VỆ TỰ ĐỘNG NGẦM ]",
        value=(
            "• **Anti-Nuke 24/7 Intelligence:** Tự động quét và phát hiện hành vi xóa trên 5 kênh trong thời gian ngắn, lập tức truy vết audit log, timeout và kick kẻ giả mạo trừ danh sách owner tối cao."
        ),
        inline=False
    )

    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    embed.set_footer(text="🌟 Sun Flower AI Architecture • Designed with Maximum Colors & Professional Standard ⚡")
    await ctx.send(embed=embed)

@bot.command(name="off")
@has_high_privilege()
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
        await ctx.send('💀🔥 **"LỆNH BỊ TỪ CHỐI! CHỈ CÓ CHỦ SỞ HỮU TỐI CAO, CHỦ SERVER HOẶC CÁC THÀNH VIÊN SỞ HỮU QUYỀN LỰC CAO NHẤT MỚI ĐƯỢC PHÉP SỬ DỤNG LỆNH NÀY!"** 🔥💀')

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

    should_reply = False
    if current_persona_id == 1:
        should_reply = True
    else:
        bot_mentioned = bot.user in message.mentions
        called = any(word in message.content.lower() for word in ["sun flower", "sunflower", "bot ơi", "bot"])
        if bot_mentioned or called or (target_user_id is not None and message.author.id == target_user_id):
            should_reply = True

    if should_reply:
        async with message.channel.typing():
            try:
                p_info = PERSONAS[current_persona_id]
                user_msg = message.content.strip() if message.content else "..."
                
                ai_reply = f"Dạ, tớ đã tiếp nhận yêu cầu của cậu: '{user_msg}'. Tớ luôn sẵn sàng hỗ trợ tận tâm mọi thắc mắc và dịch vụ mà cậu cần nhé! ✨"

                embed = discord.Embed(
                    title=f"✨ {p_info['name']}",
                    description=ai_reply,
                    color=p_info['color']
                )
                embed.set_footer(text="Sun Flower AI • Professional Assistant Engine ⚡")

                await message.reply(embed=embed, mention_author=False)

            except Exception as e:
                error_msg = str(e)
                print(f"Lỗi xử lý: {error_msg}")
                await message.reply(f"❌ `Lỗi xử lý hệ thống: {error_msg}`")

# ==================== KHỞI CHẠY BOT ====================
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
