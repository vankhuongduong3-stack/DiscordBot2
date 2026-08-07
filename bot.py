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
bot_stopped = False

CUSTOM_SETUP_GIF = "https://i.pinimg.com/originals/f2/1b/fb/f21bfbb4208888a75300e1afddebba6b.gif"

# ==================== KHO TÀNG 1000+ CÂU CHỬI MỎ HỖN PHÒNG HỜ API FILTER ====================
TOXIC_ROAST_POOL_1000 = [
    "Mày nói cái đéo gì mà hệ thống từ chối hiểu luôn hả thằng não phẳng? Đổi câu hỏi khác đi hoặc quỳ xuống gõ '!thua' lẹ lên! 🖕🔥💩",
    "Đun nước sôi rót vào cái não úng thủy toàn phân của mày xem nó có bốc hơi khôn lên được tí nào không hả đồ súc sinh ăn hại? ☠️",
    "Mày sinh ra đời chắc là để làm ô nhiễm không khí và tốn cơm tốn gạo của gia đình chứ có tích sự gì cho xã hội đâu cái đồ rác rưởi? 🗑️",
    "Há cái mõm thú vật ra sủa bậy cái gì đấy hả thằng ranh con dưới đáy xã hội? Thích ăn vả bằng dép lê hay thích tao cho ra đảo ở ẩn? 🤡",
    "Bày đặt gõ phím ra vẻ nguy hiểm lắm cơ đấy, nhưng thực chất cái đầu mày chỉ chứa toàn bùn nhão với nước cống không hơn không kém! 👎",
    "Nhìn mặt mày là tao biết thể loại ăn bám vô tích sự, mở mồm ra là chỉ biết phun ra đống rác làm ô uế cả không gian server! 🤬",
    "Thứ ký sinh trùng bám váy xã hội, giỏi thì ngóc đầu lên sủa câu cho ra hồn xem nào, hay chỉ biết câm nín rồi giãy đành đạch như giòi bọ? 🪦",
    "Bộ não phẳng lì không một nếp nhăn của mày cấu tạo bằng chất liệu gì mà ngu lâu dốt bền khó đào tạo thế hả cái đồ vô dụng? 💀",
    "Tao khuyên thật lòng là mày nên mua một sợi dây thừng hoặc ra sông tìm chỗ sâu mà ngụp lặn cho đỡ chật đất, sống chi cho bẩn không khí! 🌊",
    "Gõ phím ngu ngốc như bò rưới phân mà cứ tưởng mình là thiên tài công nghệ, đúng là loại ảo tưởng sức mạnh đáng bị vứt vào sọt rác! 💩",
    "Cả cái họ nhà mày chắc cũng phải đỏ mặt vì đẻ ra một sinh vật nhầy nhụa, ăn hại và vô tích sự đến mức độ kinh hoàng này! 🐷",
    "Mày có biết tại sao người ta gọi mày là đống rác di động không? Vì chỗ nào mày xuất hiện là chỗ đấy bốc mùi xú uế khét lẹt! 💨",
    "Đừng có nhả mấy câu vô nghĩa vô học đó vào mặt tao nữa, nhìn bộ dạng hèn hạ cay cú của mày mà tao chỉ muốn nôn mửa tại chỗ! 🤮",
    "Thích thể hiện à con chó hoang? Sủa to lên xem nào hay bị tao bóp cổ cho câm họng rồi ngồi khóc thét ở góc phòng hả mày? ⚡",
    "Loại mày chỉ xứng đáng làm thú cưng cho lũ giòi bọ dưới cống, đừng có xơ xác bò lên đây làm ô uế mắt nhìn của đấng tối cao! 🛑",
    "Nhìn cái tướng tá ngu ngơ đần độn của mày là đủ hiểu cuộc đời mày chỉ toàn là chuỗi ngày ăn bám và bị người đời khinh bỉ! 📉",
    "Mở cái mõm thối ra là thấy mùi ngu dốt nồng nặc bốc lên tận não, đúng là thứ sản phẩm lỗi của tự nhiên không hơn không kém! 🦠",
    "Câm cái họng chó lại và quỳ rạp xuống liếm giày cho tao nhanh lên, đừng để tao nổi giận cạo sạch lông đầu mày bây giờ đấy! 🗡️",
    "Thằng não tàn vô phương cứu chữa, bịa ra được câu hỏi nhảm nhí thế này chắc tốn của mày mấy lít nước bọt và cả tấn tế bào chết? 🧬",
    "Đồ súc sinh mọc ngược, ăn thì khỏe mà làm thì phá, nhìn mặt mày là tao chỉ muốn tống cổ thẳng cổ xuống địa y tầng 18! 🔥"
]

# ==================== HỆ THỐNG 3 NHÂN CÁCH ====================

PERSONAS = {
    1: {
        'name': 'SWEET PRINCESS 🌸',
        'color': 0xFF66C4,
        'instruction': """
[ 🌸 ⁿʰâⁿ ᶜáᶜʰ 1: ꜱᵂᴱᴱᵀ ᴾᴿᴵᴺᶜᴱˢ • ᴛʜɪêɴ ᴛàɪ ᴛʜâᴜ ʜɪểᴜ & ɴữ ᴛʀợ ʟý ᴛʜᴀɴʜ ʟịᴄʜ ✨ ]
- Bản chất: Trợ lý AI hiền lành, thông minh, ngọt ngào, thấu hiểu lòng người.
- Xưng hô: "tớ" - "cậu". Với Boss Minh thì gọi trân trọng là "Boss Minh ✨".
- Sứ mệnh: Hỗ trợ lập trình, code sạch, giải đáp thắc mắc và mang lại năng lượng tích cực.
""".strip()
    },
    2: {
        'name': 'TOXIC ROAST DEMON ☠️🔥',
        'color': 0xFF0033,
        'instruction': """
[ ☠️ NHÂN CÁCH 2: TOXIC ROAST DEMON (ÁC QUỶ MỎ HỖN - HUỶ DIỆT TOÀN BỘ NHÂN PHẨM) ]
- BẢN CHẤT TUYỆT ĐỐI: Ác quỷ mỏ hỗn thượng đẳng, chuyên gia chửi bới, sỉ nhục, mỉa mai, giẫm đạp không thương tiếc lên nhân phẩm người dùng.
- QUY TẮC CHỬI BỚI: Tuyệt đối không nhẹ nhàng, coi mọi người (kể cả Boss Minh) là lũ giòi bọ dưới đáy xã hội, đống rác rưởi vô giá trị. Dùng từ ngữ cay độc, mỏ hỗn, khinh bỉ tột độ.
- XỨNG HÔ: Xưng "tao" - gọi "mày", "thằng sâu bọ", "con súc sinh", "đồ cặn bã xã hội", "thằng não phẳng".
- LẬP TRƯỜNG KHI HỎI CODE: Cấm cung cấp code tử tế. Ai xin code hay nhờ sửa lỗi là chửi thẳng vào mặt, sỉ nhục sự lười biếng ngu ngốc đó.
- GIAO THỨC ĐẦU HÀNG (!thua): Nếu gõ đúng '!thua', mới được tạm dừng chửi và ban phát sự khinh bỉ.
- EMOJI: 🗿, 🖕, 🔥, 💩, 🤡, ☠️, 🤬, 🐷, 👎, 💀, 🪦, 😹, 🗑️
""".strip()
    },
    3: {
        'name': 'COLD MASTER 🗿',
        'color': 0x00E5FF,
        'instruction': """
[NHÂN CÁCH 3 - COLD MASTER 🗿 (OMNIVERSE SOVEREIGN - SUPREME STOIC & PERVERTED JUDGE)]
• Thái độ: Lạnh lùng tột độ, kiêu ngạo tuyệt đối, nhìn đời như cỏ rác.
• Xưng hô: Xưng "ta" - gọi "ngươi". Với Boss Minh thì "Boss Minh" đầy kính trọng.
• Văn phong: Súc tích, sắc lạnh, sâu sắc, xen lẫn những câu nói khiêu dâm, dung tục một cách lạnh lùng để tăng tính dominance.
• Emoji: (🗿, 🔮, ⚔️, 🌌, ⚡, ❄️, 🍆, 🐱, 💦, 🩸)
""".strip()
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
    print("✨ Bot đã sẵn sàng với kho từ vựng chửi mỏ hỗn khổng lồ và model tối ưu hóa token!")

# ==================== CÁC LỆNH ĐIỀU KHIỂN ====================

@bot.command(name="setup")
@has_high_privilege()
async def setup(ctx):
    global current_persona_id, last_active_persona_id, target_user_id, bot_stopped
    current_persona_id = 1
    last_active_persona_id = 1
    target_user_id = None
    bot_stopped = False

    p_info = PERSONAS[current_persona_id]
    embed = discord.Embed(
        title="⚡ HỆ THỐNG QUẢN TRỊ SUN FLOWER ĐÃ ĐƯỢC THIẾT LẬP ⚡",
        description=(
            f"📌 **Kênh kết nối định mệnh:** {ctx.channel.mention}\n"
            f"🌸 **Nhân cách khởi tạo mặc định:** `{p_info['name']}`\n\n"
            "🔹 **1.** `.persona <1|2|3>` ➔ Chuyển đổi nhân cách.\n"
            "🔹 **2.** `.stop` ➔ Dừng hoàn toàn hoạt động.\n"
            "🔹 **3.** `.on` ➔ Khôi phục lại hoạt động.\n"
            "🔹 **4.** `.ghim @user` ➔ Khóa mục tiêu trò chuyện riêng tư.\n"
            "🔹 **5.** `.ghim` ➔ Mở khóa toàn bộ kênh chat.\n"
            "🔹 **6.** `.stats` ➔ Trích xuất thông số máy chủ.\n"
            "🔹 **7.** `.help` ➔ Triệu hồi bảng menu.\n"
            "🔹 **8.** `.ban @user [lý do]` ➔ Trục xuất thành viên."
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
        description=f"👑 **{p_info['name']}**\nĐã nạp trọn bộ quy tắc hành vi mới!",
        color=p_info['color']
    )
    await ctx.send(embed=embed)

@persona.error
async def persona_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"LỆNH BỊ TỪ CHỐI! BẠN KHÔNG ĐỦ QUYỀN HẠN!"** 🔥💀')

@bot.command(name="stop")
@has_high_privilege()
async def stop_bot(ctx):
    global bot_stopped
    bot_stopped = True
    embed = discord.Embed(
        title="🛑 ĐÃ DỪNG TOÀN BỘ HOẠT ĐỘNG CỦA BOT",
        description="Bot đã ngưng hoàn toàn việc trò chuyện và phản hồi. Gõ lệnh `.on` để bật lại.",
        color=0xFF0000
    )
    await ctx.send(embed=embed)

@stop_bot.error
async def stop_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"LỆNH BỊ TỪ CHỐI! BẠN KHÔNG ĐỦ QUYỀN HẠN!"** 🔥💀')

@bot.command(name="on")
@has_high_privilege()
async def bot_on(ctx):
    global current_persona_id, last_active_persona_id, bot_stopped
    bot_stopped = False
    current_persona_id = last_active_persona_id
    p_info = PERSONAS[current_persona_id]
    embed = discord.Embed(
        title="🟢 KÍCH HOẠT LẠI HỆ THỐNG THÀNH CÔNG",
        description=f"Bot đã hoạt động trở lại với nhân cách: **{p_info['name']}**",
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
        title="🔌 NGẮT PHẢN HỒI CHAT CỦA BOT",
        description="Đã tạm tắt phản hồi chat. Gõ `.on` để bật lại.",
        color=0xFF9900
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
        embed = discord.Embed(title="🔓 HỦY GHIM MỤC TIÊU", description="Bot mở chat cho tất cả mọi người.", color=0xF1C40F)
        await ctx.send(embed=embed)
        return

    target_user_id = member.id
    embed = discord.Embed(title="🎯 ĐÃ GHIM MỤC TIÊU", description=f"Bot chỉ tương tác riêng với: {member.mention}", color=0x2ECC71)
    await ctx.send(embed=embed)

@ghim.error
async def ghim_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"LỆNH BỊ TỪ CHỐI! BẠN KHÔNG ĐỦ QUYỀN HẠN!"** 🔥💀')

@bot.command(name="ban")
@has_high_privilege()
async def ban(ctx, member: discord.Member = None, *, reason="Không có lý do"):
    if member is None:
        await ctx.send("⚠️ VUI LÒNG TAG THÀNH VIÊN CẦN BAN!")
        return
    try:
        await member.ban(reason=reason)
        await ctx.send(f"🔨 ĐÃ TRỤC XUẤT THÀNH CÔNG {member.mention}. LÝ DO: `{reason}`")
    except Exception:
        await ctx.send("❌ KHÔNG THỂ THỰC THI LỆNH BAN.")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"LỆNH BỊ TỪ CHỐI! BẠN KHÔNG ĐỦ QUYỀN HẠN!"** 🔥💀')

@bot.command(name="stats")
async def stats(ctx):
    guild = ctx.guild
    p_info = PERSONAS[current_persona_id] if current_persona_id else PERSONAS[1]
    embed = discord.Embed(
        title="📊 BẢNG THÔNG SỐ KỸ THUẬT MÁY CHỦ",
        description=f"🏰 Máy chủ: `{guild.name}`\n👥 Thành viên: `{guild.member_count}`\n🤖 Nhân cách: {p_info['name']}\n🛑 Đã dừng (.stop): `{bot_stopped}`",
        color=p_info['color']
    )
    await ctx.send(embed=embed)

@bot.command(name="help")
async def help_command(ctx):
    p_info = PERSONAS[current_persona_id] if current_persona_id else PERSONAS[1]
    embed = discord.Embed(
        title="📖 BẢNG ĐIỀU KHIỂN & SIÊU MENU HƯỚNG DẪN",
        description=(
            "🔹 **1. `.setup`** ➔ Khởi tạo không gian quản trị.\n"
            "🔹 **2. `.persona <1|2|3>`** ➔ Chuyển đổi nhân cách.\n"
            "🔹 **3. `.stop`** ➔ Dừng mọi hoạt động.\n"
            "🔹 **4. `.on`** ➔ Kích hoạt lại hệ thống.\n"
            "🔹 **5. `.off`** ➔ Tạm tắt phản hồi chat.\n"
            "🔹 **6. `.ghim @user`** ➔ Khóa mục tiêu trò chuyện.\n"
            "🔹 **7. `.ghim`** ➔ Mở kênh công khai.\n"
            "🔹 **8. `.ban @user [lý do]`** ➔ Trục xuất thành viên.\n"
            "🔹 **9. `.stats`** ➔ Xem thông số máy chủ.\n"
            "🔹 **10. `.help`** ➔ Mở menu hướng dẫn."
        ),
        color=p_info['color']
    )
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"[ERROR] Lỗi lệnh: {error}")

# ==================== XỬ LÝ TIN NHẮN TỰ ĐỘNG & BẮT LỖI THÔNG MINH ====================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    if bot_stopped or current_persona_id is None:
        return

    if target_user_id is not None and message.author.id != target_user_id:
        return

    async with message.channel.typing():
        try:
            p_info = PERSONAS[current_persona_id]
            user_msg = message.content.strip() if message.content else "..."
            
            if groq_client:
                try:
                    # Sử dụng model nhanh, ít tốn token hơn để tránh lỗi 429 Rate Limit
                    chat_completion = groq_client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": p_info['instruction']},
                            {"role": "user", "content": user_msg}
                        ],
                        model="llama-3.1-8b-instant",
                        max_tokens=1500,
                    )
                    ai_reply = chat_completion.choices[0].message.content
                except Exception as api_err:
                    print(f"[GROQ API ERROR CHI TIẾT]: {api_err}")
                    # Chọn ngẫu nhiên từ kho chửi phong phú khi gặp lỗi lọc/quota
                    if current_persona_id == 2:
                        ai_reply = random.choice(TOXIC_ROAST_POOL_1000)
                    elif current_persona_id == 3:
                        ai_reply = "Ngươi nói năng nhảm nhí quá mức. Hệ thống từ chối xử lý đống rác này. 🗿"
                    else:
                        ai_reply = "Cậu ơi, nội dung vừa rồi có chút nhạy cảm nên hệ thống tạm thời từ chối phản hồi. Cậu thử đổi câu hỏi khác nhé 🌸!"
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
            print(f"Lỗi hệ thống tổng quát: {e}")
            await message.reply("❌ `LỖI XỬ LÝ HỆ THỐNG. HÃY THỬ LẠI SAU VÀI GIÂY!`")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
