import asyncio
import os
import random
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN")
OWNER_ID = 1531882555664629861

if not TOKEN:
    raise ValueError("Lỗi: Không tìm thấy TOKEN trong môi trường hệ thống!")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Đổi prefix sang dấu chấm '.'
bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

current_mode = None          # None / "roast" / "angel"
last_active_mode = "roast"   # Lưu chế độ trước khi dùng .off
target_user_id = None

# ==================== ROAST LINES ====================
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
    '🤮🩸 **"MÀY VIẾT NHƯ CÁI LỒN ĐANG BỊ VIÊM. NÃO MÀY CHẮC TOÀN NƯỚC CẶC CHỨ KHÔNG PHẢI CHẤT XÁM."** 🩸🤮',
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

# ==================== ANGEL LINES (nhiều câu + emote) ====================
ANGEL_LINES = [
    '🌸💖 **"Chào cậu nhé~ Tớ là Sun Flower đây 🌸"** 💖🌸',
    '✨🌷 **"Cậu gọi tớ à? Tớ đang lắng nghe đây ✨"** 🌷✨',
    '💗☁️ **"Tớ nghe thấy cậu rồi. Cứ thoải mái nói nhé ☁️"** ☁️💗',
    '🥰🌸 **"Có chuyện gì cứ kể cho tớ nghe nha 🥰"** 🌸🥰',
    '💖✨ **"Tớ luôn sẵn sàng lắng nghe cậu ✨"** ✨💖',
    '🌷💗 **"Cậu đang cần tớ giúp gì không ạ? 🌷"** 💗🌷',
    '☁️🌸 **"Tớ ở đây với cậu mà, đừng ngại nha ☁️"** 🌸☁️',
    '🥰💖 **"Cảm ơn cậu đã nhắn tin cho tớ 🥰"** 💖🥰',
    '✨🌷 **"Tớ rất vui khi được trò chuyện cùng cậu ✨"** 🌷✨',
    '💗🌸 **"Cậu muốn chia sẻ điều gì với tớ không? 💗"** 🌸💗',
    '☁️🥰 **"Hít thở sâu nào~ Tớ đang ở đây ☁️"** 🥰☁️',
    '💖✨ **"Mỗi lời của cậu tớ đều lắng nghe cẩn thận ✨"** ✨💖',
    '🌷☁️ **"Cứ từ từ nói, tớ không vội đâu 🌷"** ☁️🌷',
    '🌸💗 **"Tớ hy vọng có thể làm cậu cảm thấy dễ chịu hơn 🌸"** 💗🌸',
    '🥰✨ **"Cậu không cần phải mạnh mẽ suốt đâu 🥰"** ✨🥰',
    '💖🌸 **"Tớ hiểu cảm giác của cậu 💖"** 🌸💖',
    '✨💗 **"Có tớ ở đây rồi, cậu yên tâm nha ✨"** 💗✨',
    '🌷🥰 **"Cậu làm tốt lắm rồi đó 🌷"** 🥰🌷',
    '☁️💖 **"Mọi thứ rồi sẽ ổn thôi ☁️"** 💖☁️',
    '🌸✨ **"Tớ luôn ở bên cậu 🌸"** ✨🌸',
    '🥰💗 **"Cậu muốn tớ an ủi không? 🥰"** 💗🥰',
    '💖🌷 **"Tớ sẵn sàng lắng nghe mọi thứ 💖"** 🌷💖',
    '✨☁️ **"Cứ kể cho tớ nghe đi ✨"** ☁️✨',
    '🌷🌸 **"Tớ không phán xét cậu đâu 🌷"** 🌸🌷',
    '💗🥰 **"Cậu quan trọng với tớ lắm 💗"** 🥰💗',
    '☁️✨ **"Tớ ở đây để hỗ trợ cậu ☁️"** ✨☁️',
    '🌸💖 **"Cậu không cô đơn đâu 🌸"** 💖🌸',
    '🥰🌷 **"Tớ rất thích được trò chuyện với cậu 🥰"** 🌷🥰',
    '💖☁️ **"Có chuyện buồn cứ nói với tớ nha 💖"** ☁️💖',
    '✨💗 **"Tớ sẽ nhẹ nhàng bên cậu ✨"** 💗✨',
    '🌷🌸 **"Cậu đang cố gắng rất nhiều rồi 🌷"** 🌸🌷',
    '💗☁️ **"Tớ tin ở cậu 💗"** ☁️💗',
    '🥰✨ **"Cứ dựa vào tớ một chút cũng được 🥰"** ✨🥰',
    '💖🌷 **"Tớ sẽ không rời cậu đâu 💖"** 🌷💖',
    '🌸💗 **"Cậu xứng đáng được đối xử dịu dàng 🌸"** 💗🌸',
    '✨☁️ **"Tớ lắng nghe cậu đây ✨"** ☁️✨',
    '🌷🥰 **"Cậu muốn ôm không? 🌷"** 🥰🌷',
    '💗🌸 **"Tớ luôn sẵn sàng 💗"** 🌸💗',
    '☁️💖 **"Cậu không cần phải giả vờ mạnh mẽ ☁️"** 💖☁️',
    '🥰✨ **"Tớ hiểu mà 🥰"** ✨🥰',
    '💖🌷 **"Cứ thoải mái với tớ nha 💖"** 🌷💖',
    '🌸☁️ **"Tớ ở đây vì cậu 🌸"** ☁️🌸',
    '✨💗 **"Cậu quan trọng ✨"** 💗✨',
    '🌷💖 **"Tớ sẽ chờ cậu nói 🌷"** 💖🌷',
    '💗🥰 **"Cậu muốn tâm sự không? 💗"** 🥰💗',
    '☁️🌸 **"Tớ không vội đâu ☁️"** 🌸☁️',
    '🥰🌷 **"Cậu cứ từ từ 🥰"** 🌷🥰',
    '💖✨ **"Tớ lắng nghe 💖"** ✨💖',
    '🌸💗 **"Cậu không sao đâu 🌸"** 💗🌸',
    '✨☁️ **"Tớ bên cậu ✨"** ☁️✨',
]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="Sun Flower • Sweet & Toxic"))

# Đảm bảo gỡ bỏ lệnh help cũ trước khi tạo lại để tránh CommandRegistrationError
bot.remove_command("help")

@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="🌻 SUN FLOWER • DANH SÁCH LỆNH",
        description="Danh sách lệnh hiện có của bot:",
        color=0x00FF9F
    )
    embed.add_field(
        name="🌸 Lệnh công khai",
        value="`.help` → Xem danh sách lệnh này",
        inline=False
    )
    embed.add_field(
        name="👑 Lệnh chỉ Boss được dùng",
        value=(
            "`.setup` → Khởi động bot ở Chế độ Hiền Lành + GIF\n"
            "`.on` → Kích hoạt lại bot\n"
            "`.roastmode` → Bật/tắt chế độ chửi\n"
            "`.ghim @user` → Chỉ chửi 1 người\n"
            "`.angelmode` → Bật/tắt chế độ hiền lành\n"
            "`.off` → Tắt bot"
        ),
        inline=False
    )
    embed.set_footer(text="Sun Flower • Only Boss can control modes")
    await ctx.send(embed=embed)

@bot.command(name="setup")
async def setup(ctx):
    global current_mode, last_active_mode, target_user_id

    if ctx.author.id != OWNER_ID:
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ BOSS MỚI ĐƯỢC SETUP."** 🔥💀')
        return

    # Tự động chuyển sang Angel Mode khi gọi setup
    current_mode = "angel"
    last_active_mode = "angel"
    target_user_id = None

    embed = discord.Embed(
        title="⚡ LÃNH ĐỊA SUN FLOWER MULTIMODAL AI ĐÃ KÍCH HOẠT",
        description=(
            f"📌 Kênh {ctx.channel.mention} đã được liên kết với **Toxic & Sweet Engine**!\n"
            "🌸 **Trạng thái hiện tại:** Tự động kích hoạt **ANGEL MODE** (Hiền lành)\n\n"
            "🖼️ Bot chỉ trả lời khi được gọi tên hoặc tag!\n"
            "⚡ **.on**: Kích hoạt lại bot\n"
            "📄 **.roastmode**: Chế độ chửi\n"
            "📌 **.ghim @user**: Chỉ chửi 1 người\n"
            "🌸 **.angelmode**: Chế độ hiền lành\n"
            "📖 **.help**: Xem danh sách lệnh\n"
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

    mode_name = "🔥 **CHẾ ĐỘ CHỬI (ROAST MODE)**" if current_mode == "roast" else "🌸 **CHẾ ĐỘ HIỀN LÀNH (ANGEL MODE)**"
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

    if current_mode == "roast":
        current_mode = None
        target_user_id = None
        status = "🔴 **TẮT**"
        desc = "💤 Chế độ chửi đã tắt."
        color = 0x2F3136
    else:
        current_mode = "roast"
        last_active_mode = "roast"
        target_user_id = None
        status = "🟢 **BẬT**"
        desc = "🔥 **CHẾ ĐỘ CHỬI ĐÃ KÍCH HOẠT**\nBot chỉ trả lời khi được gọi."
        color = 0xFF0000

    embed = discord.Embed(
        title="🌻 SUN FLOWER • TOXIC ROAST DEMON 💀🔥",
        description=desc,
        color=color
    )
    embed.add_field(name="📊 Trạng thái", value=status, inline=True)
    embed.set_footer(text="Sun Flower • Only listens to Boss")
    await ctx.send(embed=embed)

@bot.command(name="ghim")
async def ghim(ctx, member: discord.Member = None):
    global target_user_id, current_mode, last_active_mode

    if ctx.author.id != OWNER_ID:
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ BOSS MỚI ĐƯỢC GHIM."** 🔥💀')
        return

    if member is None:
        target_user_id = None
        await ctx.send('🔓 **Đã bỏ ghim.**')
        return

    target_user_id = member.id
    current_mode = "roast"
    last_active_mode = "roast"

    embed = discord.Embed(
        title="🌻 SUN FLOWER • TOXIC ROAST DEMON 💀🔥",
        description=f"📌 **Đã ghim {member.mention}**\nTừ giờ chỉ thằng này bị chửi (khi gọi bot).",
        color=0xFF0000
    )
    embed.set_footer(text="Sun Flower • Only listens to Boss")
    await ctx.send(embed=embed)

@bot.command(name="angelmode")
async def angelmode(ctx):
    global current_mode, last_active_mode, target_user_id

    if ctx.author.id != OWNER_ID:
        await ctx.send('🌸💖 **"Chỉ Boss mới được bật chế độ này nha~"** 💖🌸')
        return

    if current_mode == "angel":
        current_mode = None
        desc = "☁️ Chế độ hiền lành đã tắt."
        color = 0x2F3136
    else:
        current_mode = "angel"
        last_active_mode = "angel"
        target_user_id = None
        desc = "🌸💖 **CHẾ ĐỘ HIỀN LÀNH ĐÃ KÍCH HOẠT**\nBot chỉ trả lời khi được gọi tên hoặc tag!"
        color = 0xFF69B4

    embed = discord.Embed(
        title="🌸 SUN FLOWER • SWEET PRINCESS 💖",
        description=desc,
        color=color
    )
    embed.set_footer(text="Sun Flower • Soft Mode")
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

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    if current_mode is None:
        return

    # Kiểm tra xem bot có được gọi tên hoặc tag không
    content_lower = message.content.lower()
    bot_mentioned = bot.user in message.mentions
    called = any(word in content_lower for word in ["sun flower", "sunflower", "bot ơi", "bot"])

    # ===== ROAST MODE =====
    if current_mode == "roast":
        if message.author.id == OWNER_ID:
            return

        if not (bot_mentioned or called):
            return

        if target_user_id is not None and message.author.id != target_user_id:
            return

        await asyncio.sleep(random.uniform(0.6, 1.8))

        selected = random.sample(ROAST_LINES, k=random.randint(7, 11))
        random.shuffle(selected)
        roast_text = "\n\n".join(selected)

        header = (
            f'💀🔥 **"HAHAHA! {message.author.mention} NÀY VỪA GỬI:"** 🔥💀\n'
            f'`{message.content[:90] if message.content else "..."}`\n\n'
            f'☠️🤡 **"NGHE ĐÂY THẰNG LỒN {message.author.display_name.upper()}:"** 🤡☠️\n\n'
        )

        embed = discord.Embed(
            title="🌻 SUN FLOWER • TOXIC ROAST DEMON 💀🔥",
            description=header + roast_text,
            color=0xFF0000
        )
        avatar_url = bot.user.avatar.url if (bot.user and bot.user.avatar) else None
        embed.set_author(name="Sun Flower", icon_url=avatar_url)
        embed.set_footer(text="Sun Flower • Toxic Roast Demon 💀🔥")

        try:
            await message.reply(embed=embed, mention_author=True)
        except Exception:
            await message.channel.send(content=message.author.mention, embed=embed)

    # ===== ANGEL MODE =====
    elif current_mode == "angel":
        # Trả lời khi người dùng gọi tên hoặc tag bot
        if not (bot_mentioned or called):
            return

        await asyncio.sleep(random.uniform(1.0, 2.0))

        user_msg = message.content.strip() if message.content else "..."
        base = random.choice(ANGEL_LINES)

        reply_text = f"{base}\n\n🌸 **Cậu vừa nói:** `{user_msg}`"

        embed = discord.Embed(
            title="🌸 SUN FLOWER • SWEET PRINCESS 💖",
            description=reply_text,
            color=0xFF69B4
        )
        embed.set_footer(text="Sun Flower • Soft & Gentle 🌸")

        try:
            await message.reply(embed=embed, mention_author=False)
        except Exception:
            await message.channel.send(embed=embed)

bot.run(TOKEN)
