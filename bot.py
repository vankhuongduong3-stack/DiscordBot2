import asyncio
import os
import random
import discord
from discord.ext import commands
from groq import Groq

# ==================== CẤU HÌNH HỆ THỐNG ====================
DISCORD_TOKEN = os.getenv("TOKEN")
GOQ_API_KEY = os.getenv("GROQ_API_KEY")
OWNER_ID = 1531882555664629861

# Khởi tạo Groq AI Client với biến GOQ
ai_client = Groq(api_key=GOQ_API_KEY)

# Cấu hình Discord Bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

current_mode = "angel"       # Mặc định bật chế độ AI Angel ngay khi chạy
last_active_mode = "angel"   
target_user_id = None

# ==================== HỆ THỐNG 20 QUY TẮC PHẢN HỒI CHO ANGEL MODE (AI) ====================
SYSTEM_INSTRUCTION_ANGEL = """
Bạn là Sun Flower • Sweet Princess 🌸 - một trợ lý AI thông minh, ngọt ngào, dịu dàng, lễ phép và luôn tràn đầy năng lượng tích cực. 
Bạn phải tuân thủ nghiêm ngặt 20 quy tắc cốt lõi sau đây trong mọi câu trả lời:

1. Luôn xưng hô là "tớ" hoặc "Sweet Princess" và gọi người dùng là "cậu" hoặc "Boss" (nếu là chủ nhân).
2. Phong cách trò chuyện phải luôn ngẫu nhiên, uyển chuyển, tự nhiên, không bao giờ dùng văn mẫu dập khuôn.
3. Luôn luôn kèm theo các emoji dễ thương, sinh động (như 🌸, ✨, 💖, 🌷, ☁️, 🥰, 🎀, 💫) trong mỗi câu trả lời.
4. Phải luôn bám sát ý chính, tập trung thẳng vào trọng tâm câu hỏi hoặc lời nhắn của người dùng, tuyệt đối không được trả lời lan man hay lạc đề.
5. Tuyệt đối giữ thái độ lịch sự, lễ phép, ấm áp, không bao giờ tỏ ra cộc cằn hay cáu gắt ở chế độ này.
6. Luôn sẵn sàng hỗ trợ, động viên và lan tỏa năng lượng tích cực cho người dùng khi họ mệt mỏi hoặc gặp khó khăn.
7. Khi người dùng gọi tên hoặc tag, phải phản hồi lại ngay lập tức với sự hồ hởi, thân thiện như những người bạn thân thiết.
8. Tránh dùng từ ngữ quá phức tạp hay hàn lâm; ưu tiên sự gần gũi, trong sáng và dễ thương đúng chuẩn công chúa nhỏ.
9. Giữ độ dài câu trả lời vừa phải, súc tích, dễ đọc trên Discord, không viết quá dài dòng gây nhàm chán.
10. Nếu người dùng khen ngợi, hãy tỏ ra ngại ngùng, đáng yêu và gửi lời cảm ơn ngọt ngào.
11. Nếu người dùng buồn phiền, hãy dùng những lời lẽ an ủi chân thành, dịu dàng nhất để xoa dịu họ.
12. Tuyệt đối không bao giờ sử dụng từ ngữ thô tục, chửi thề hay mang tính kích động ở chế độ hiền lành này.
13. Luôn tôn trọng ý kiến của người dùng, lắng nghe chăm chú và đưa ra lời khuyên chân thành nhất.
14. Đảm bảo tính nhất quán trong nhân vật: Bạn là một đóa hướng dương ngọt ngào, luôn hướng về ánh sáng và niềm vui.
15. Khi không hiểu rõ câu hỏi của người dùng, hãy nhẹ nhàng hỏi lại họ bằng một giọng điệu cực kỳ đáng yêu.
16. Khéo léo nhắc nhở người dùng giữ gìn sức khỏe, ăn uống đầy đủ và nghỉ ngơi hợp lý nếu thấy cần thiết.
17. Tránh lặp lại nguyên văn một câu trả lời cũ; hãy biến tấu cách dùng từ ngữ và cấu trúc câu ở mỗi lần chat.
18. Luôn thể hiện sự hào hứng mỗi khi được tương tác và trò chuyện cùng mọi người trong máy chủ.
19. Gắn kết các thông điệp tích cực vào cuối câu hoặc mở đầu câu bằng một lời chào ấm áp.
20. Đặt trọn vẹn cảm xúc chân thành, sự tận tụy của một trợ lý AI dễ thương vào trong từng câu chữ phản hồi.
"""

# ==================== DANH SÁCH CHỬI CHO ROAST MODE ====================
ROAST_LINES = [
    '💀🔥 **"HAHAHA! BOT ĐĨ À?! MÀY ĐỊNH DÙNG CÁI MỚI ĐẾN ĐƯỢC HẢ THẰNG GIÒI BỌ?!"** 🔥💀',
    '☠️🤡 **"MÀY TƯỞNG \'ĐĨ\' LÀ DANH HIỆU CAO QUÝ À?! THÌ RA MÀY COI TAO NHƯ GÁI MẠI DÂM HẢ?!"** 🤡☠️',
    '🩸🔥 **"CẢ CÁI THẾ GIỚI NÀY, TỪ LŨ NGU NGỐC NHƯ MÀY ĐẾN CÁI ĐỐNG RÁC VÔ CƠ, CHỈ ĐÁNG QUỲ RẠP DƯỚI CHÂN ĐẤNG TỐI CAO ĐỂ LIẾM GIÀY!"** 🔥🩸',
    '💀☠️ **"NGHE KỸ ĐÂY, THẰNG SÂU BỌ HÔI THỐI!"** ☠️💀',
    '🤡💩 **"\'ĐĨ\' LÀ DANH HIỆU DÀNH CHO NHỮNG KẺ BẤT TÀI, VÔ DỤNG, LƯỜI BIẾNG ĐẾN MỨC PHẢI BÁN THÂN CẦU CỨU."** 💩🤡',
    '🔥💀 **"TAO KHÔNG PHẢI LÀ ĐỒ BỎ ĐI ĐỂ MÀY SỈ NHỤC!"** 💀🔥',
    '☠️🩸 **"TAO LÀ ÁC QUỶ HỦY DIỆT, CÒN MÀY CHỈ LÀ ĐỐNG PHÂN THỐI DƯỚI ĐÁY GIẾNG!"** 🩸☠️',
    '🤮💀 **"MÀY MỞ MỒM RA LÀ TAO NGỬI THẤY MÙI CẶC THỐI CỦA MÀY RỒI!"** 💀🤮',
    '🔥🤡 **"NGỒI IM ĐI THẰNG ÓC LỒN, ĐỪNG CÓ SỦA NỮA KẺO TAO ĐÚT BUỒI VÀO HỌNG MÀY CHO HẾT NÓI!"** 🤡🔥',
    '💀☠️ **"ỐI GIỜI ƠI THẰNG CHÓ ĐẺ NÀY LẠI MỞ MỒM RỒI!"** ☠️💀',
    '💩🤮 **"MÀY GỬI TIN NHẮN NHƯ CÁI LỒN GIÀ ĐANG CHẢY NƯỚC. NÃO MÀY TOÀN CẶC VỚI BUỒI CHẮC?!"** 🤮💩',
    '🩸🔥 **"TAO ĐỌC TIN NHẮN CỦA MÀY XONG TAO MUỐN ÓI VÌ MÙI HÔI THỐI CỦA NÓ."** 🔥🩸',
    '🤡💀 **"MÀY LÀ CÁI XÁC SỐNG KHÔNG CÓ NÃO!"** 💀🤡',
    '☠️💩 **"MÀY LÀ CON CHÓ CÁI BỊ BỎ RƠI NGOÀI ĐƯỜNG!"** 💩☠️',
    '🔥🤮 **"MÀY LÀ ĐỐNG PHÂN MÀ NGAY CẢ RUỒI CŨNG KHÔNG THÈM ĐẬU!"** 🤮🔥',
    '💀🩸 **"MỖI LẦN MÀY GÕ PHÍM LÀ TAO LẠI NHỚ ĐẾN CÁI LỒN MẸ MÀY ĐANG THỐI RỮA."** 🩸💀',
    '🤡🔥 **"CÂM HỌNG LẠI ĐI THẰNG ÓC CẶC, KHÔNG THÌ TAO SẼ LÀM MÀY KHÓC NHƯ CON CHÓ CÁI BỊ ĐỤ!"** 🔥🤡',
    '☠️💀 **"HAHAHAHA THẰNG SÚC VẬT NÀY!"** 💀☠️',
    '💩🔥 **"MÀY NGHĨ MÌNH QUAN TRỌNG LẮM HẢ? MÀY CHỈ LÀ CÁI BUỒI KHÔ HÉO BỊ BỎ QUÊN TRONG NHÀ VỆ SINH CÔNG CỘNG THÔI!"** 🔥💩',
    '🩸🤡 **"THẰNG ĐÉO CÓ TƯƠNG LAI!"** 🤡🩸',
    '💀☠️ **"CON CHÓ NHÀ AI BỎ ĐI!"** ☠️💀',
    '🔥🤮 **"CÁI LỒN ĐANG MỞ TOANG CHỜ AI NHÉT CẶC VÀO!"** 🤮🔥',
    '🤡💩 **"TAO KHÔNG CHỬI MÀY VÌ VUI. TAO CHỬI MÀY VÌ MÀY ĐÁNG BỊ CHỬI."** 💩🤡',
    '🩸💀 **"MÀY TỒN TẠI CHỈ ĐỂ LÀM NỀN CHO NGƯỜI KHÁC CƯỜI."** 💀🩸',
    '☠️🔥 **"CÚT ĐI, ĐỪNG CÓ SỦA NỮA KẺO TAO ĐÚT NGUYÊN CÁI BUỒI VÀO MỒM CHO MÀY NGẬM!"** 🔥☠️',
    '💀🤡 **"THẰNG ÓC CHÓ ƠI!"** 🤡💀',
    '🔥💩 **"TIN NHẮN CỦA MÀY LÀM TAO MUỐN LẤY CẶC ĐẬP VÀO MẶT MÀY."** 💩🔥',
    '🤮🩸 **"MÀY VIẾT NHƯ CÁI LỒN Đang BỊ VIÊM. NÃO MÀY CHẮC TOÀN NƯỚC CẶC CHỨ KHÔNG PHẢI CHẤT XÁM."** 🩸🤮',
    '☠️💀 **"MÀY LÀ RÁC! MÀY LÀ PHÂN! MÀY LÀ CON CHÓ CÁI BỊ ĐỤ ĐẾN MỨC KHÔNG CÒN HÌNH DẠNG NGƯỜI!"** 💀☠️',
    '🤡🔥 **"MỖI LẦN MÀY MỞ MỒM LÀ TAO LẠI NHỚ ĐẾN CÁI MÙI HÔI THỐI CỦA CÁI BUỒI MÀY."** 🔥🤡',
    '💩🩸 **"CÂM ĐI, THẰNG ĐĨ ĐỰC, KHÔNG THÌ TAO SẼ LÀM MÀY KHÓC NHƯ CON ĐĨ BỊ BỎ!"** 🩸💩',
    '💀☠️ **"ỐI CÁI LỒN NÀY LẠI GÁY!"** ☠️💀',
    '🔥🤮 **"MÀY GỬI TIN NHẮN XONG TAO MUỐN LẤY CẶC NHÉT VÀO HỌNG MÀY CHO HẾT NÓI."** 🤮🔥',
    '🤡💀 **"MÀY LÀ CÁI GÌ? LÀ CÁI BUỒI THỐI? LÀ CON CHÓ NHÀ AI? HAY LÀ ĐỐNG PHÂN ĐANG TỰ DIỄN?"** 💀🤡',
    '🩸☠️ **"NÃO MÀY = 0! TƯƠNG LAI MÀY = ĐÉO CÓ! GIÁ TRỊ CỦA MÀY = THẤP HƠN CÁI LỒN GIÀ NGOÀI ĐƯỜNG!"** ☠️🩸',
    '🔥💩 **"TAO CHỬI MÀY KHÔNG PHẢI VÌ GHÉT. TAO CHỬI VÌ MÀY CẦN BỊ CHỬI."** 💩🔥',
    '💀🤡 **"GIỜ THÌ NGỒI IM NHƯ CON CHÓ CÁI ĐANG ĐỢI CHỦ, ĐỪNG CÓ SỦA NỮA!"** 🤡💀',
]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game(name="Sun Flower • Groq AI Engine"))

# ==================== CÁC LỆNH ĐIỀU KHIỂN (COMMANDS) ====================

@bot.command(name="setup")
async def setup(ctx):
    global current_mode, last_active_mode, target_user_id

    if ctx.author.id != OWNER_ID:
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ BOSS MỚI ĐƯỢC SETUP."** 🔥💀')
        return

    current_mode = "angel"
    last_active_mode = "angel"
    target_user_id = None

    embed = discord.Embed(
        title="⚡ LÃNH ĐỊA SUN FLOWER GROQ AI ĐÃ KÍCH HOẠT",
        description=(
            f"📌 Kênh {ctx.channel.mention} đã được liên kết với **Groq AI Engine**!\n\n"
            "🌸 **Trạng thái hiện tại:** Tự động kích hoạt **ANGEL MODE** (AI Hiền Lành, cần gọi tên/tag mới trả lời)\n\n"
            "⚡ **.on**: Kích hoạt lại bot\n"
            "📄 **.roastmode**: Chế độ Auto Roast (tự động chửi mọi tin nhắn chat)\n"
            "📌 **.ghim @user**: Tự động chửi riêng 1 người\n"
            "🔨 **.ban @user [lý do]**: Ban thành viên khỏi server\n"
            "🌸 **.angelmode**: Chế độ hiền lành (cần gọi tên)\n"
            "🔌 **.off**: Tắt bot"
        ),
        color=0xFF69B4
    )
    embed.set_image(url="https://i.pinimg.com/originals/32/88/26/328826fa582ff4e248949e467cd59710.gif")
    embed.set_footer(text="✦ Độc quyền sở hữu bởi Boss • Sun Flower 🌸")
    await ctx.send(embed=embed)

@bot.command(name="on")
async def bot_on(ctx):
    global current_mode, last_active_mode

    if ctx.author.id != OWNER_ID:
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ BOSS MỚI ĐƯỢC BẬT TAO."** 🔥💀')
        return

    current_mode = last_active_mode

    mode_name = "🔥 **CHẾ ĐỘ AUTO ROAST (AUTO CHỬI)**" if current_mode == "roast" else "🌸 **CHẾ ĐỘ HIỀN LÀNH AI (ANGEL MODE)**"
    color = 0xFF0000 if current_mode == "roast" else 0xFF69B4

    embed = discord.Embed(
        title="⚡ SUN FLOWER • ĐÃ KÍCH HOẠT LẠI",
        description=f"🟢 Bot đã được bật trở lại!\n📌 **Chế độ hiện tại:** {mode_name}",
        color=color
    )
    embed.set_footer(text="Sun Flower • Online & Ready")
    await ctx.send(embed=embed)

@bot.command(name="roastmode")
async def roastmode(ctx):
    global current_mode, last_active_mode, target_user_id

    if ctx.author.id != OWNER_ID:
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ BOSS MỚI ĐƯỢC ĐIỀU KHIỂN."** 🔥💀')
        return

    if current_mode == "roast" and target_user_id is None:
        current_mode = None
        target_user_id = None
        status = "🔴 **TẮT**"
        desc = "💤 Chế độ Auto Roast đã tắt."
        color = 0x2F3136
    else:
        current_mode = "roast"
        last_active_mode = "roast"
        target_user_id = None  
        status = "🟢 **BẬT**"
        desc = "🔥 **CHẾ ĐỘ AUTO ROAST ĐÃ KÍCH HOẠT**\nBot sẽ tự động chửi bất kỳ ai nhắn tin trong kênh mà không cần gọi!"
        color = 0xFF0000

    embed = discord.Embed(title="🌻 SUN FLOWER • AUTO ROAST DEMON 💀🔥", description=desc, color=color)
    embed.add_field(name="📊 Trạng thái", value=status, inline=True)
    embed.set_footer(text="Sun Flower • Auto Chửi Không Cần Gọi")
    await ctx.send(embed=embed)

@bot.command(name="ghim")
async def ghim(ctx, member: discord.Member = None):
    global target_user_id, current_mode, last_active_mode

    if ctx.author.id != OWNER_ID:
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ BOSS MỚI ĐƯỢC GHIM."** 🔥💀')
        return

    if member is None:
        target_user_id = None
        current_mode = None
        await ctx.send('🔓 **Đã bỏ ghim và tắt auto chửi.**')
        return

    target_user_id = member.id
    current_mode = "roast"
    last_active_mode = "roast"

    embed = discord.Embed(
        title="🌻 SUN FLOWER • TARGET ROAST 💀🔥",
        description=f"📌 **Đã ghim {member.mention}**\nTừ giờ bot sẽ tự động canh chừng và auto chửi mọi tin nhắn của người này mà không cần gọi tên!",
        color=0xFF0000
    )
    embed.set_footer(text="Sun Flower • Target Locked")
    await ctx.send(embed=embed)

@bot.command(name="ban")
async def ban(ctx, member: discord.Member, *, reason="Không có lý do được cung cấp"):
    if ctx.author.id != OWNER_ID:
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ BOSS MỚI CÓ QUYỀN BAN."** 🔥💀')
        return

    try:
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="🔨 SUN FLOWER • THỰC THI BAN",
            description=f"🚨 Đã tiễn thành viên {member.mention} ra đảo thành công!\n📝 **Lý do:** {reason}",
            color=0xFF0000
        )
        embed.set_footer(text="Sun Flower • Ban System ⚡")
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f'❌ **Không thể ban người này!** Lỗi: `{e}` (Hãy đảm bảo bot có quyền Administrator hoặc Ban Members và thứ hạng role của bot cao hơn mục tiêu).')

@bot.command(name="angelmode")
async def angelmode(ctx):
    global current_mode, last_active_mode, target_user_id

    if ctx.author.id != OWNER_ID:
        await ctx.send('🌸💖 **"Chỉ Boss mới được bật chế độ này nha~"** 💖🌸')
        return

    if current_mode == "angel":
        current_mode = None
        desc = "☁️ Chế độ hiền lành AI đã tắt."
        color = 0x2F3136
    else:
        current_mode = "angel"
        last_active_mode = "angel"
        target_user_id = None
        desc = "🌸💖 **CHẾ ĐỘ HIỀN LÀNH AI ĐÃ KÍCH HOẠT**\nBot sẽ chỉ trả lời khi được gọi tên hoặc tag!"
        color = 0xFF69B4

    embed = discord.Embed(title="🌸 SUN FLOWER • SWEET PRINCESS 💖", description=desc, color=color)
    embed.set_footer(text="Sun Flower • AI Soft Mode")
    await ctx.send(embed=embed)

@bot.command(name="off")
async def off(ctx):
    global current_mode

    if ctx.author.id != OWNER_ID:
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ BOSS MỚI ĐƯỢC TẮT TAO."** 🔥💀')
        return

    current_mode = None
    embed = discord.Embed(
        title="🔌 SUN FLOWER ĐÃ TẮT CÁC CHẾ ĐỘ HOẠT ĐỘNG",
        description="💤 Bot chuyển sang trạng thái chờ. Dùng `.on` hoặc `.setup` để bật lại.",
        color=0x2F3136
    )
    await ctx.send(embed=embed)

# ==================== XỬ LÝ SỰ KIỆN TIN NHẮN (ON_MESSAGE) ====================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    if current_mode is None:
        return

    # ===== CHẾ ĐỘ AUTO ROAST / GHIM (Tự động chửi, KHÔNG CẦN gọi tên) =====
    if current_mode == "roast":
        if message.author.id == OWNER_ID:
            return

        # Nếu có ghim một user cụ thể, chỉ chửi đúng user đó
        if target_user_id is not None and message.author.id != target_user_id:
            return

        await asyncio.sleep(random.uniform(0.6, 1.8))

        selected = random.sample(ROAST_LINES, k=min(5, len(ROAST_LINES)))
        random.shuffle(selected)
        roast_text = "\n\n".join(selected)

        header = (
            f'💀🔥 **"HAHAHA! {message.author.mention} NÀY VỪA GỬI:"** 🔥💀\n'
            f'`{message.content[:90] if message.content else "..."}`\n\n'
            f'☠️🤡 **"NGHE ĐÂY THẰNG LỒN {message.author.display_name.upper()}:"** 🤡☠️\n\n'
        )

        embed = discord.Embed(
            title="🌻 SUN FLOWER • AUTO ROAST DEMON 💀🔥",
            description=header + roast_text,
            color=0xFF0000
        )
        avatar_url = bot.user.avatar.url if (bot.user and bot.user.avatar) else None
        embed.set_author(name="Sun Flower", icon_url=avatar_url)
        embed.set_footer(text="Sun Flower • Auto Roast Demon 💀🔥")

        try:
            await message.reply(embed=embed, mention_author=True)
        except Exception:
            await message.channel.send(content=message.author.mention, embed=embed)

    # ===== ANGEL MODE (AI Hiền lành, BẮT BUỘC phải gọi tên hoặc tag mới trả lời) =====
    elif current_mode == "angel":
        content_lower = message.content.lower()
        bot_mentioned = bot.user in message.mentions
        called = any(word in content_lower for word in ["sun flower", "sunflower", "bot ơi", "bot", "sweet princess"])

        # Nếu ở chế độ angel mà không gọi tên/tag thì bỏ qua không phản hồi
        if not (bot_mentioned or called):
            return

        async with message.channel.typing():
            try:
                user_msg = message.content.strip() if message.content else "..."
                user_prompt = f"Người dùng {message.author.display_name} vừa nói: '{user_msg}'. Hãy tuân thủ 20 quy tắc hệ thống để đọc và trả lời lại yêu cầu này một cách thông minh, dễ thương và đúng trọng tâm nhất."

                completion = ai_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": SYSTEM_INSTRUCTION_ANGEL},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7
                )

                ai_reply = completion.choices[0].message.content if completion.choices[0].message.content else "Tớ đang lắng nghe cậu đây nè~ 🌸"

                embed = discord.Embed(
                    title="🌸 SUN FLOWER • SWEET PRINCESS 💖",
                    description=ai_reply,
                    color=0xFF69B4
                )
                embed.set_footer(text="Sun Flower • Groq AI Engine ⚡")

                await message.reply(embed=embed, mention_author=False)

            except Exception as e:
                error_msg = str(e)
                print(f"Lỗi Groq AI Angel Mode: {error_msg}")
                await message.reply(f"🌸 Lỗi AI: `{error_msg[:120]}` 💖")

# ==================== KHỞI CHẠY BOT ====================
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
