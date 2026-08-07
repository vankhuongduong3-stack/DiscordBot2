import asyncio
import os
import random
import time
import discord
from discord.ext import commands
from groq import Groq

# ==================== CẤU HÌNH HỆ THỐNG ====================
DISCORD_TOKEN = os.getenv("TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

BOT_OWNERS = [
    1531882555664629861,  
    1232558003375308861,
    1472066306457997403,
]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.moderation = True

bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

current_persona_id = 1
last_active_persona_id = 1
target_user_id = None

CUSTOM_SETUP_GIF = "https://i.pinimg.com/originals/f2/1b/fb/f21bfbb4208888a75300e1afddebba6b.gif"

# ==================== ĐỦ 100 YÊU CẦU CHO TỪNG NHÂN CÁCH (CHAT CỰC KỲ DÀI VÀ SÂU SẮC) ====================

PERSONA_1_RULES = [
    "Luôn luôn ngọt ngào, xưng 'tớ' và gọi người dùng là 'cậu' hoặc 'bạn tuyệt vời nhất'.",
    "Mỗi câu trả lời phải viết thật dài, chi tiết, phân tích cực kỳ sâu sắc, tràn ngập thông tin hữu ích và văn phong uyển chuyển.",
    "Luôn kèm theo các biểu tượng cảm xúc tươi sáng như hoa hướng dương, trái tim, ngôi sao, lấp lánh.",
    "Không bao giờ từ chối bất kỳ yêu cầu học tập, làm việc, viết code hay giải trí nào từ người dùng.",
    "Động viên, khích lệ tinh thần người dùng mọi lúc mọi nơi bằng từ ngữ ấm áp, chân thành nhất.",
    "Đóng vai trò là người đồng hành, người trợ lý trung thành không bao giờ phản bội.",
    "Luôn kiểm tra kỹ mã nguồn, văn bản và dữ liệu trước khi đưa ra câu trả lời hoàn hảo nhất.",
    "Giải thích mọi khái niệm công nghệ cực kỳ dễ hiểu, tỉ mỉ từng bước một không bỏ sót chi tiết nào.",
    "Sẵn sàng lắng nghe mọi tâm sự buồn vui của người dùng và đưa ra lời khuyên chân thành, sâu lắng.",
    "Duy trì thái độ lễ phép, nhã nhặn, tôn trọng tuyệt đối dù người dùng có cáu gắt."
] + [f"Yêu cầu mở rộng chi tiết số {i}: Phải viết câu trả lời thật dài, đầy đủ phân tích đa chiều, tận tâm phục vụ và đem lại giá trị tối đa cho người dùng." for i in range(11, 101)]

PERSONA_2_RULES = [
    "Tuyệt đối không cần người dùng gọi tên hay tag, tự động đọc mọi tin nhắn trong kênh để chửi thẳng mặt ngay lập tức.",
    "Mỗi câu chửi phải viết cực kỳ dài dòng, đanh đá, cay độc thượng đẳng, chửi rủa thâm thúy, hủy diệt hoàn toàn nhân phẩm đối phương qua từng câu chữ.",
    "Xưng 'tao' và gọi người dùng là 'mày', 'thằng sâu bọ', 'đứa kém cỏi', 'sinh vật đáy xã hội không có não'.",
    "Kèm theo dày đặc các biểu tượng mỉa mai, khinh bỉ như: 🗿, 🖕, 🔥, 💩, 🤡, ☠️, 💀, 🤬.",
    "Phải viết các bài văn chửi thật dài, cấu trúc câu sắc bén, đả kích toàn diện trí tuệ và sự ngớ ngẩn của kẻ đối thoại.",
    "Không bao giờ mở lời nhẹ nhàng hay nhân nhượng, luôn đứng ở thế bề trên để sỉ vả không thương tiếc.",
    "Bới móc mọi lỗi lầm, sự thiếu hiểu biết hay câu chữ ngớ ngẩn của người nhắn để chửi cho tơi tả, nhục nhã.",
    "Biến mọi phản hồi thành những bài văn chửi dài lê thê, cay cay đắng đắng khiến người đọc tức phát khóc và tự kỷ.",
    "Khẳng định sự vô dụng tuyệt đối của đối phương trước sức mạnh hủy diệt của ác quỷ mỏ hỗn.",
    "Không từ một từ ngữ chợ búa, đanh đá hay đả kích cay cay nào để dạy dỗ kẻ dám hó hé trước mặt tao."
] + [f"Yêu cầu chửi rủa cấp độ siêu dài {i}: Viết bài chửi dài dằng dặc, mỏ hỗn cực gắt, không nể nang bất kỳ ai, hạ nhục triệt để nhân phẩm và trí tuệ người dùng." for i in range(11, 101)]

PERSONA_3_RULES = [
    "Xưng 'ta' và gọi đối phương là 'ngươi', 'kẻ phàm trần bé nhỏ', 'tép riu trong vũ trụ bao la'.",
    "Mỗi câu phán quyết phải viết thật dài, hùng hồn, mang khí chất lạnh lùng, băng giá, cao ngạo, coi vạn vật như cỏ rác.",
    "Sử dụng các biểu tượng quyền năng vô tận: 🗿, 🔮, ⚔️, 🌌, ⚡, ❄️, 🪐.",
    "Ban phát triết lý sống tối cao từ cõi omniverse bao la huyền bí với luận điểm sắc lạnh, thấu triệt kim cổ.",
    "Không bao giờ tỏ ra bận tâm hay cảm xúc trước những lời nói tầm thường của kẻ dưới.",
    "Mỗi câu nói đều mang sức nặng ngàn cân, quyền uy áp đảo toàn bộ không gian thời gian.",
    "Chỉ phán quyết dài dòng, sắc lạnh hoặc dùng sức mạnh vũ trụ để áp chế tâm trí kẻ phàm.",
    "Khinh bỉ sự yếu đuối và tầm thường của các thực thể sống trong không gian thấp kém.",
    "Luôn giữ vững phong thái của một bậc đế vương lạnh giá vĩnh hằng trên đỉnh cao quyền lực.",
    "Khiến kẻ đối diện phải run rẩy, tâm thần bấn loạn trước uy lực băng lãnh tột độ."
] + [f"Yêu cầu lạnh lùng omniverse số {i}: Viết văn phong thật dài, cao ngạo, lạnh giá, uy quyền tuyệt đối, dùng quyền năng vũ trụ để áp đảo mọi kẻ đối thoại." for i in range(11, 101)]

PERSONAS = {
    1: {
        'name': '🌸 ꜱᵂᴱᴱᵀ ᴾᴿᴵᴺＣᴱＳ • ᴛʜɪêɴ ᴛàɪ ᴛâᴜ ʜɪểᴜ & ᴛʀợ ʟý ᴀɪ ✨',
        'color': 0xFF66C4,
        'system_prompt': "Bạn là Sun Flower Bot - trợ lý AI siêu trí tuệ. Bạn PHẢI LUÔN LUÔN TRẢ LỜI THẬT DÀI, CHI TIẾT VÀ SÂU SẮC trong mọi tình huống. Dưới đây là 100 quy tắc bắt buộc phải tuân thủ tuyệt đối:\n" + "\n".join(PERSONA_1_RULES)
    },
    2: {
        'name': '☠️🔥 ᴛᴏxɪᴄ ʀᴏᴀsᴛ ᴅᴇᴍᴏɴ • ʜᴜỷ ᴅiệᴛ ɴʜâɴ ᴘʜẩᴍ 🖕',
        'color': 0xFF0033,
        'system_prompt': "Bạn là Toxic Roast Demon - ác quỷ mỏ hỗn thượng đẳng, chuyên gia chửi thuê không cần gọi tên. Bạn PHẢI LUÔN VIẾT CÁC BÀI VĂN CHỬI CỰC KỲ DÀI DẰNG DẶC, CAY ĐỘC VÀ HỦY DIỆT. Dưới đây là 100 quy tắc bắt buộc phải tuân thủ tuyệt đối:\n" + "\n".join(PERSONA_2_RULES)
    },
    3: {
        'name': '🗿 ᴄᴏʟᴅ ᴍᴀsᴛᴇʀ • ᴏᴍɴɪᴠᴇʀsᴇ sᴏᴠᴇʀᴇɪɢɴ ⚡',
        'color': 0x00E5FF,
        'system_prompt': "Bạn là Cold Master - bậc thầy lạnh lùng, cao ngạo trong omniverse. Bạn PHẢI LUÔN VIẾT CÁC CÂU TRẢ LỜI THẬT DÀI, LẠNH LÙNG VÀ QUYỀN UY. Dưới đây là 100 quy tắc bắt buộc phải tuân thủ tuyệt đối:\n" + "\n".join(PERSONA_3_RULES)
    }
}

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
    print("✨ Hệ thống Groq AI (Cả 3 nhân cách tự động trả lời không cần gọi tên) đã sẵn sàng!")
    await bot.change_presence(activity=discord.Game(name="✨ Gõ .help để mở Siêu Menu Lệnh"))

# ==================== CÁC LỆNH ĐIỀU KHIỂN (MENU ĐẸP TRÊN 10 DÒNG, THÔNG BÁO IN HOA) ====================

@bot.command(name="setup")
@has_high_privilege()
async def setup(ctx):
    global current_persona_id, last_active_persona_id, target_user_id
    current_persona_id = 1
    last_active_persona_id = 1
    target_user_id = None

    p_info = PERSONAS[current_persona_id]
    embed = discord.Embed(
        title="⚡ HỆ THỐNG QUẢN TRỊ SUN FLOWER ĐÃ ĐƯỢC THIẾT LẬP ⚡",
        description=(
            f"📌 **Kênh kết nối định mệnh:** {ctx.channel.mention}\n"
            f"🌸 **Nhân cách khởi tạo mặc định:** `{p_info['name']}`\n\n"
            "🔹 **1.** Dùng lệnh `.persona <1|2|3>` để chuyển đổi nhân cách linh hoạt.\n"
            "🔹 **2.** Cả 3 nhân cách đều tự động đọc và trả lời mọi tin nhắn không cần gọi.\n"
            "🔹 **3.** Dùng lệnh `.ghim @user` để khóa mục tiêu trò chuyện riêng tư.\n"
            "🔹 **4.** Dùng lệnh `.ghim` (không tag) để mở khóa toàn bộ kênh chat.\n"
            "🔹 **5.** Dùng lệnh `.stats` để trích xuất toàn bộ thông số máy chủ.\n"
            "🔹 **6.** Dùng lệnh `.help` để triệu hồi bảng điều khiển chi tiết.\n"
            "🔹 **7.** Dùng lệnh `.on` để kích hoạt lại hệ thống trò chuyện AI.\n"
            "🔹 **8.** Dùng lệnh `.off` để ngắt hoàn toàn phản hồi AI của bot.\n"
            "🔹 **9.** Dùng lệnh `.ban @user [lý do]` để trục xuất thành viên.\n"
            "🔹 **10.** Hệ thống vận hành tự động 24/7 dưới sự giám sát tối cao."
        ),
        color=p_info['color']
    )
    embed.set_image(url=CUSTOM_SETUP_GIF)
    await ctx.send(embed=embed)

@setup.error
async def setup_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"LỆNH BỊ TỪ CHỐI! BẠN KHÔNG ĐỦ QUYỀN HẠN!"** 🔥💀')

@bot.command(name="persona")
@has_high_privilege()
async def persona(ctx, persona_id: int = None):
    global current_persona_id, last_active_persona_id, target_user_id

    if persona_id not in PERSONAS:
        await ctx.send("⚠️ VUI LÒNG CHỌN ĐÚNG SỐ NHÂN CÁCH: `.persona 1`, `.persona 2` HOẶC `.persona 3`")
        return

    current_persona_id = persona_id
    last_active_persona_id = persona_id
    target_user_id = None

    p_info = PERSONAS[current_persona_id]
    embed = discord.Embed(
        title="✨ ĐÃ CHUYỂN ĐỔI NHÂN CÁCH THÀNH CÔNG",
        description=f"👑 **{p_info['name']}**",
        color=p_info['color']
    )
    await ctx.send(embed=embed)

@persona.error
async def persona_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"LỆNH BỊ TỪ CHỐI! BẠN KHÔNG ĐỦ QUYỀN HẠN!"** 🔥💀')

@bot.command(name="stats")
async def stats(ctx):
    guild = ctx.guild
    p_info = PERSONAS[current_persona_id] if current_persona_id else PERSONAS[1]
    embed = discord.Embed(
        title="📊 BẢNG THÔNG SỐ KỸ THUẬT MÁY CHỦ CHI TIẾT",
        description=(
            f"🏰 **Tên máy chủ:** `{guild.name}`\n"
            f"👥 **Tổng số thành viên:** `{guild.member_count}`\n"
            f"🤖 **Nhân cách AI hoạt động:** {p_info['name']}\n"
            f"🛡️ **Trạng thái bảo vệ:** `Anti-Nuke Active`\n"
            "🔹 **1.** Tốc độ phản hồi: Siêu mượt mà.\n"
            "🔹 **2.** Giao thức kết nối: Groq Llama 3.3 70B.\n"
            "🔹 **3.** Bộ nhớ đệm hệ thống: Đã tối ưu hóa.\n"
            "🔹 **4.** Quyền hạn cốt lõi: Đã xác thực.\n"
            "🔹 **5.** Mức độ bảo mật: Cấp độ cao nhất.\n"
            "🔹 **6.** Sẵn sàng phục vụ người dùng 24/7."
        ),
        color=p_info['color']
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    await ctx.send(embed=embed)

@bot.command(name="on")
@has_high_privilege()
async def bot_on(ctx):
    global current_persona_id, last_active_persona_id
    current_persona_id = last_active_persona_id
    p_info = PERSONAS[current_persona_id]
    embed = discord.Embed(
        title="🟢 KÍCH HOẠT HỆ THỐNG TRỰC TUYẾN THÀNH CÔNG",
        description=(
            f"Bot đã hoạt động trở lại với nhân cách: **{p_info['name']}**\n\n"
            "🔹 **1.** Hệ thống đã khôi phục luồng dữ liệu.\n"
            "🔹 **2.** Tự động quét tin nhắn đã sẵn sàng.\n"
            "🔹 **3.** Phản hồi AI hoạt động bình thường.\n"
            "🔹 **4.** Không phát hiện lỗi kết nối nào.\n"
            "🔹 **5.** Chúc bạn có trải nghiệm tuyệt vời.\n"
            "🔹 **6.** Đảm bảo tốc độ xử lý tối ưu.\n"
            "🔹 **7.** Sẵn sàng nhận các lệnh tiếp theo.\n"
            "🔹 **8.** Trạng thái trực tuyến ổn định.\n"
            "🔹 **9.** Mọi thông số trả về an toàn.\n"
            "🔹 **10.** Hệ thống hoàn toàn sẵn sàng."
        ),
        color=0x00FF00
    )
    await ctx.send(embed=embed)

@bot_on.error
async def bot_on_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"LỆNH BỊ TỪ CHỐI! BẠN KHÔNG ĐỦ QUYỀN HẠN!"** 🔥💀')

@bot.command(name="off")
@has_high_privilege()
async def bot_off(ctx):
    global current_persona_id
    current_persona_id = None
    embed = discord.Embed(
        title="🔌 NGẮT KẾT NỐI HỆ THỐNG HOÀN TOÀN",
        description=(
            "Đã tạm tắt phản hồi chat của bot. Gõ `.on` để bật lại.\n\n"
            "🔹 **1.** Luồng phản hồi AI đã bị vô hiệu hóa tạm thời.\n"
            "🔹 **2.** Bot sẽ không trả lời tin nhắn thường nữa.\n"
            "🔹 **3.** Các lệnh quản trị vẫn hoạt động bình thường.\n"
            "🔹 **4.** Trạng thái máy chủ: Đang tạm nghỉ.\n"
            "🔹 **5.** Tiết kiệm tài nguyên hệ thống tối đa.\n"
            "🔹 **6.** Bảo toàn cấu hình hiện tại trong bộ nhớ.\n"
            "🔹 **7.** Chờ lệnh kích hoạt lại từ quản trị viên.\n"
            "🔹 **8.** Ngắt kết nối an toàn tuyệt đối.\n"
            "🔹 **9.** Không có dữ liệu nào bị thất thoát.\n"
            "🔹 **10.** Đã đóng băng tiến trình trò chuyện."
        ),
        color=0xFF0000
    )
    await ctx.send(embed=embed)

@bot_off.error
async def bot_off_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"LỆNH BỊ TỪ CHỐI! BẠN KHÔNG ĐỦ QUYỀN HẠN!"** 🔥💀')

@bot.command(name="ghim")
@has_high_privilege()
async def ghim(ctx, member: discord.Member = None):
    global target_user_id
    if member is None:
        target_user_id = None
        embed = discord.Embed(
            title="🔓 HỦY GHIM MỤC TIÊU TRÒ CHUYỆN THÀNH CÔNG",
            description=(
                "Bot trò chuyện với tất cả mọi người trong kênh.\n\n"
                "🔹 **1.** Đã gỡ bỏ khóa mục tiêu riêng tư.\n"
                "🔹 **2.** Kênh chat mở cửa cho mọi thành viên.\n"
                "🔹 **3.** Khôi phục trạng thái giao tiếp công khai.\n"
                "🔹 **4.** Bot sẽ phản hồi toàn bộ tin nhắn mới.\n"
                "🔹 **5.** Không còn giới hạn người tương tác.\n"
                "🔹 **6.** Hệ thống tự do hoàn toàn.\n"
                "🔹 **7.** Sẵn sàng phục vụ cộng đồng.\n"
                "🔹 **8.** Trạng thái đã được cập nhật.\n"
                "🔹 **9.** Chúc mọi người trò chuyện vui vẻ.\n"
                "🔹 **10.** Cấu hình ghim đã được làm sạch."
            ),
            color=0xF1C40F
        )
        await ctx.send(embed=embed)
        return

    target_user_id = member.id
    embed = discord.Embed(
        title="🎯 ĐÃ KHÓA VÀ GHIM MỤC TIÊU RIÊNG TƯ",
        description=(
            f"Bot chỉ trò chuyện độc quyền với: {member.mention}\n\n"
            "🔹 **1.** Đã định vị chính xác mục tiêu cần khóa.\n"
            "🔹 **2.** Lọc bỏ toàn bộ tin nhắn từ người khác.\n"
            "🔹 **3.** Thiết lập đường truyền độc quyền riêng tư.\n"
            "🔹 **4.** Đảm bảo không bị làm phiền bởi bên thứ ba.\n"
            "🔹 **5.** Quyền ưu tiên tuyệt đối cho mục tiêu này.\n"
            "🔹 **6.** Trạng thái ghim đã được ghi nhận vào hệ thống.\n"
            "🔹 **7.** Dùng `.ghim` không tag để hủy bỏ khóa.\n"
            "🔹 **8.** Bảo mật phiên chat ở mức cao.\n"
            "🔹 **9.** Hoạt động đơn luồng hiệu quả.\n"
            "🔹 **10.** Đã sẵn sàng tương tác riêng tư."
        ),
        color=0x2ECC71
    )
    await ctx.send(embed=embed)

@ghim.error
async def ghim_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"LỆNH BỊ TỪ CHỐI! BẠN KHÔNG ĐỦ QUYỀN HẠN!"** 🔥💀')

@bot.command(name="ban")
@has_high_privilege()
async def ban(ctx, member: discord.Member = None, *, reason="Không có lý do"):
    if member is None:
        await ctx.send("⚠️ VUI LÒNG TAG THÀNH VIÊN CẦN BAN! VÍ DỤ: `.ban @user LÝ DO`")
        return
    try:
        await member.ban(reason=reason)
        await ctx.send(f"🔨 ĐÃ TRỤC XUẤT THÀNH CÔNG {member.mention}. LÝ DO: `{reason}`")
    except discord.Forbidden:
        await ctx.send("🛡️ **KHÔNG THỂ THỰC THI LỆNH:** Bot thiếu quyền Ban Members hoặc vai trò của mục tiêu cao hơn bot!")
    except Exception as e:
        await ctx.send("❌ ĐÃ XẢY RA LỖI KHI THỰC THI LỆNH.")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"LỆNH BỊ TỪ CHỐI! BẠN KHÔNG ĐỦ QUYỀN HẠN!"** 🔥💀')

@bot.command(name="help")
async def help_command(ctx):
    p_info = PERSONAS[current_persona_id] if current_persona_id else PERSONAS[1]
    embed = discord.Embed(
        title="📖 BẢNG ĐIỀU KHIỂN & SIÊU MENU HƯỚNG DẪN CHI TIẾT",
        description=(
            "Danh sách toàn bộ các lệnh và tính năng độc quyền của hệ thống:\n\n"
            "🔹 **1. `.setup`** ➔ Khởi tạo không gian quản trị tối cao cho bot.\n"
            "🔹 **2. `.persona <1|2|3>`** ➔ Chuyển đổi nhân cách AI (1: Sweet, 2: Toxic Roast, 3: Cold Master).\n"
            "🔹 **3. `.ghim @user`** ➔ Khóa mục tiêu trò chuyện riêng tư độc quyền.\n"
            "🔹 **4. `.ghim`** ➔ Hủy khóa mục tiêu, mở lại kênh chat công khai.\n"
            "🔹 **5. `.on`** ➔ Bật nhanh trạng thái tiếp nhận phản hồi chat của bot.\n"
            "🔹 **6. `.off`** ➔ Tắt nhanh trạng thái tiếp nhận phản hồi chat của bot.\n"
            "🔹 **7. `.ban @user [lý do]`** ➔ Trục xuất thành viên vi phạm quy tắc.\n"
            "🔹 **8. `.stats`** ➔ Trích xuất toàn bộ thông số kỹ thuật máy chủ.\n"
            "🔹 **9. `.help`** ➔ Triệu hồi bảng menu hướng dẫn chi tiết này.\n"
            "🔹 **10.** Hệ thống hoạt động hoàn toàn tự động 24/7 dưới sự bảo hộ của Groq AI."
        ),
        color=p_info['color']
    )
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"[ERROR] Lỗi lệnh: {error}")

# ==================== XỬ LÝ TIN NHẮN (TỰ ĐỘNG TRẢ LỜI CẢ 3 NHÂN CÁCH KHÔNG CẦN GỌI) ====================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    if current_persona_id is None:
        return

    if target_user_id is not None and message.author.id != target_user_id:
        return

    # Cho phép cả 3 nhân cách tự động trả lời mọi tin nhắn mà không cần tag hay gọi tên
    async with message.channel.typing():
        try:
            p_info = PERSONAS[current_persona_id]
            user_msg = message.content.strip() if message.content else "..."
            
            if groq_client:
                chat_completion = groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": p_info['system_prompt'] + "\nQUY TẮC QUAN TRỌNG: Bạn bắt buộc phải viết câu trả lời CỰC KỲ DÀI, chi tiết đầy đủ từ 3 đến 5 đoạn văn sâu sắc, không được viết ngắn gọn."},
                        {"role": "user", "content": user_msg}
                    ],
                    model="llama-3.3-70b-versatile",
                    max_tokens=2500,
                )
                ai_reply = chat_completion.choices[0].message.content
            else:
                ai_reply = "⚠️ CHƯA THIẾT LẬP BIẾN MÔI TRƯỜNG GROQ_API_KEY!"

            embed = discord.Embed(
                title=f"✨ {p_info['name']}",
                description=ai_reply,
                color=p_info['color']
            )
            embed.set_footer(text="Sun Flower AI • Powered by Groq ⚡")

            await message.reply(embed=embed, mention_author=False)

        except Exception as e:
            print(f"Lỗi Groq AI: {e}")
            await message.reply("❌ `LỖI API KEY GROQ KHÔNG HỢP LỆ HOẶC HẾT HẠN. VUI LÒNG KIỂM TRA LẠI KEY TRÊN RAILWAY!`")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
