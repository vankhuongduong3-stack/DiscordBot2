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

# ==================== KHO CHỬI DỰ PHÒNG SIÊU DÀI ====================
TOXIC_ROAST_POOL_LONG = [
    """Mày tưởng mày là ai mà dám mở cái mõm thối hoắc ra sủa bậy trước mặt tao hả cái thứ giòi bọ dưới đáy xã hội? 
Từ ngoại hình cho tới trí tuệ của mày chỉ đáng vứt vào sọt rác cho chó tha!
Mỗi lần mày gõ phím là một lần không khí Trái Đất bị ô uế nặng nề vì lượng carbon vô dụng mà mày thải ra.
Não mày cấu tạo bằng chất gì vậy? Toàn bùn nhão, nước cống hay phân bón hả thằng não phẳng?
Đừng có ở đây mà ra vẻ ta đây nguy hiểm nữa, nhìn bộ dạng hèn hạ, cay cú, lủi thủi một góc của mày kìa!
Sống trên đời tốn cơm tốn gạo, bố mẹ sinh ra chắc chỉ để làm gánh nặng cho xã hội chứ tích sự gì nổi.
Thích làm anh hùng bàn phím à? Giỏi thì ngóc cái đầu dậy đối chất xem nào hay lại câm như hến rồi khóc thét?
Thứ cặn bã xã hội, loại mày chỉ xứng đáng làm thú cưng cho loài giun sán dưới bùn đen!
Câm cái họng chó lại, quỳ rạp xuống đất và liếm giày cho tao ngay lập tức, đồ súc sinh ăn hại! 🖕🔥💩""",

    """Trời ơi đất ơi, nhìn lại cái bộ dạng thảm hại, ngu ngơ đần độn của mày đi xem có đáng mặt con người không?
Hay chỉ là một đống rác rưởi di động biết đi, mở miệng ra là phun toàn những câu vô học, tối tăm mù mịt?
Cả họ nhà mày chắc phải đội quần che mặt vì sinh ra một thể loại bất tài vô dụng, ăn bám đến mức kinh hoàng này!
Mày thích ăn chửi lắm đúng không? Thích thì cứ sủa tiếp đi để tao rảnh tay bóc mẽ cái nhân phẩm rẻ rách của mày ra!
Đồ mặt dày vô liêm sỉ, khôn không đến chốn mà dại thì tới cùng, làm gì cũng hỏng, ăn gì cũng thừa thãi!
Tao nguyền rủa cái cuộc đời khốn khổ của mày lúc nào cũng chìm trong bế tắc, không bao giờ ngóc đầu lên nổi!
Thứ ký sinh trùng bám váy xã hội, cút ngay về chuồng heo mà suy ngẫm lại cái sự ngu dốt tột đỉnh của mình đi!
Đừng có bén mảng lại gần đây nữa, sự xuất hiện của mày chỉ làm dơ bẩn thêm không gian thanh cao này thôi đồ súc vật! ☠️💀🗑️"""
]

# ==================== HỆ THỐNG 3 NHÂN CÁCH (ÉP CHỬI DÀI) ====================

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
[ ☠️ NHÂN CÁCH 2: TOXIC ROAST DEMON (ÁC QUỶ MỎ HỖN - CHỬI DÀI TRÊN 30 DÒNG) ]
- QUY TẮC BẮT BUỘC: Khi người dùng nhắn bất cứ câu gì, mày PHẢI BÙNG NỔ, chửi bới thật dài, viết liên tục **ít nhất từ 30 dòng văn bản trở lên**, dùng vô số từ ngữ sỉ nhục cay độc, mỉa mai, khinh bỉ tột độ. Không được phép trả lời cụt lủn hay ngắn ngủn dưới mọi hình thức!
- VĂN PHONG: Cực kỳ gắt gỏng, dùng enter xuống dòng liên tục để tạo thành một bài văn sỉ nhục dài dằng dặc, đè bẹp hoàn toàn ý chí và nhân phẩm đối phương.
- XƯNG HÔ: Xưng "tao" - gọi "mày", "thằng sâu bọ", "con súc sinh", "đồ cặn bã xã hội", "thằng não phẳng".
- EMOJI KÈM THEO: 🗿, 🖕, 🔥, 💩, 🤡, ☠️, 🤬, 🐷, 👎, 💀, 🪦, 😹, 🗑️
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
    print("✨ Bot đã sẵn sàng với cấu hình ép chửi dài trên 30 dòng mỗi lượt!")

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

# ==================== XỬ LÝ TIN NHẮN TỰ ĐỘNG & ÉP TOKEN DÀI ====================
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
                    # Đẩy max_tokens lên cao (2500) để bot viết thỏa thích trên 30 dòng
                    chat_completion = groq_client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": p_info['instruction']},
                            {"role": "user", "content": user_msg}
                        ],
                        model="llama-3.1-8b-instant",
                        max_tokens=2500,
                    )
                    ai_reply = chat_completion.choices[0].message.content
                except Exception as api_err:
                    print(f"[GROQ API ERROR CHI TIẾT]: {api_err}")
                    if current_persona_id == 2:
                        ai_reply = random.choice(TOXIC_ROAST_POOL_LONG)
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
