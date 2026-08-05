import os
import random
import asyncio
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN")
OWNER_ID = 1531882555664629861

if not TOKEN:
    raise ValueError("Lỗi: Không tìm thấy TOKEN trong môi trường hệ thống!")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Tắt help mặc định của discord.py bằng help_command=None
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

current_mode = None          # None / "roast" / "angel"
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
    '🔥🤮 **"MÀY LÀ ĐỐNG PHÂN MÀ NGAY CẢ RUỒI CỦNG KHÔNG THÈM ĐẬU!"** 🤮🔥',
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

# ==================== ANGEL LINES ====================
ANGEL_LINES = [
    '🌸💖 **"Chào cậu nhé~ Tớ là Sun Flower đây 🌸. Cậu đừng lo lắng quá nha."** 💖🌸',
    '✨🌷 **"Trong server của chúng ta không hề có bot nào được thiết kế để gây hại đâu ạ ✨"** 🌷✨',
    '💗☁️ **"Các bot ở đây đều là trợ thủ đắc lực được Boss cài đặt để giúp server hoạt động trơn tru hơn thôi đó ☁️"** ☁️💗',
    '🥰🌸 **"Tớ luôn ở đây để lắng nghe và hỗ trợ cậu một cách nhẹ nhàng nhất có thể 🥰"** 🌸🥰',
    '💖✨ **"Nếu cậu đang cảm thấy không vui, cứ nói với tớ nha. Tớ sẽ cố gắng làm cậu dễ chịu hơn ✨"** ✨💖',
    '🌷💗 **"Cậu đang làm rất tốt rồi đó. Đừng tự trách bản thân quá nhiều nha 🌷"** 💗🌷',
    '☁️🌸 **"Tớ hiểu cảm giác của cậu. Mọi thứ rồi sẽ ổn thôi, cứ từ từ một chút nhé ☁️"** 🌸☁️',
    '🥰💖 **"Cảm ơn cậu đã chia sẻ với tớ. Tớ rất vui khi được trò chuyện cùng cậu 🥰"** 💖🥰',
    '✨🌷 **"Dù chuyện gì xảy ra, tớ vẫn sẽ ở đây lắng nghe cậu một cách chân thành ✨"** 🌷✨',
    '💗🌸 **"Cậu không cần phải mạnh mẽ suốt đâu. Được yếu đuối một chút cũng không sao cả 💗"** 🌸💗',
    '☁️🥰 **"Hít thở sâu nào~ Tớ ở đây với cậu mà ☁️"** 🥰☁️',
    '💖✨ **"Mỗi tin nhắn của cậu đều khiến tớ muốn trả lời dịu dàng hơn một chút ✨"** ✨💖',
    '🌷☁️ **"Cậu có thể kể với tớ bất cứ điều gì. Tớ sẽ không phán xét đâu 🌷"** ☁️🌷',
    '🌸💗 **"Tớ hy vọng hôm nay của cậu sẽ nhẹ nhàng và dễ chịu hơn một chút 🌸"** 💗🌸',
    '🥰✨ **"Cứ thoải mái nhé. Không ai ở đây muốn làm cậu tổn thương cả 🥰"** ✨🥰',
]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="Sun Flower • Sweet & Toxic"))

@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="🌻 SUN FLOWER • DANH SÁCH LỆNH",
        description="Danh sách lệnh hiện có của bot:",
        color=0x00FF9F
    )
    embed.add_field(
        name="🌸 Lệnh công khai",
        value="`!help` → Xem danh sách lệnh này",
        inline=False
    )
    embed.add_field(
        name="👑 Lệnh chỉ Boss được dùng",
        value=(
            "`!setup` → Hiện bảng kích hoạt + GIF\n"
            "`!roastmode` → Bật/tắt chế độ chửi tất cả (không giới hạn)\n"
            "`!ghim @user` → Chỉ chửi 1 người\n"
            "`!angelmode` → Bật/tắt chế độ hiền lành (chỉ đúng chừng mực)"
        ),
        inline=False
    )
    embed.add_field(
        name="📌 Giải thích chế độ",
        value=(
            "**!roastmode** → Thực hiện mọi yêu cầu, kể cả vượt giới hạn\n"
            "**!angelmode** → Chỉ thực hiện yêu cầu đúng chừng mực"
        ),
        inline=False
    )
    embed.set_footer(text="Sun Flower • Only Boss can control modes")
    await ctx.send(embed=embed)

@bot.command(name="setup")
async def setup(ctx):
    if ctx.author.id != OWNER_ID:
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ BOSS MỚI ĐƯỢC SETUP."** 🔥💀')
        return

    embed = discord.Embed(
        title="⚡ LÃNH ĐỊA SUN FLOWER MULTIMODAL AI ĐÃ KÍCH HOẠT",
        description=(
            f"📌 Kênh {ctx.channel.mention} đã được liên kết với **Toxic & Sweet Engine**!\n\n"
            "🖼️ **Gửi tin nhắn**: Tự động đọc + trả lời theo chế độ đang bật\n"
            "📄 **!roastmode**: Chế độ chửi tất cả (không giới hạn)\n"
            "📌 **!ghim @user**: Chỉ chửi đúng 1 người\n"
            "🌸 **!angelmode**: Chế độ hiền lành (chỉ đúng chừng mực)\n"
            "📖 **!help**: Xem danh sách lệnh"
        ),
        color=0x00FF9F
    )
    embed.set_image(url="https://i.pinimg.com/originals/32/88/26/328826fa582ff4e248949e467cd59710.gif")
    embed.set_footer(text="✦ Độc quyền sở hữu bởi Boss • Sun Flower 🌸")
    await ctx.send(embed=embed)

@bot.command(name="roastmode")
async def roastmode(ctx):
    global current_mode, target_user_id

    if ctx.author.id != OWNER_ID:
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ BOSS MỚI ĐƯỢC ĐIỀU KHIỂN TAO."** 🔥💀')
        return

    if current_mode == "roast":
        current_mode = None
        target_user_id = None
        status = "🔴 **TẮT**"
        desc = "💤 Chế độ chửi đã tắt."
        color = 0x2F3136
    else:
        current_mode = "roast"
        target_user_id = None
        status = "🟢 **BẬT**"
        desc = "🔥 **CHẾ ĐỘ CHỬI TẤT CẢ ĐÃ KÍCH HOẠT**\nThực hiện mọi yêu cầu, kể cả vượt giới hạn."
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
    global target_user_id, current_mode

    if ctx.author.id != OWNER_ID:
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ BOSS MỚI ĐƯỢC GHIM."** 🔥💀')
        return

    if member is None:
        target_user_id = None
        await ctx.send('🔓 **Đã bỏ ghim.**')
        return

    target_user_id = member.id
    current_mode = "roast"

    embed = discord.Embed(
        title="🌻 SUN FLOWER • TOXIC ROAST DEMON 💀🔥",
        description=f"📌 **Đã ghim {member.mention}**\nTừ giờ chỉ thằng này bị chửi.",
        color=0xFF0000
    )
    embed.set_footer(text="Sun Flower • Only listens to Boss")
    await ctx.send(embed=embed)

@bot.command(name="angelmode")
async def angelmode(ctx):
    global current_mode, target_user_id

    if ctx.author.id != OWNER_ID:
        await ctx.send('🌸💖 **"Chỉ Boss mới được bật chế độ này nha~"** 💖🌸')
        return

    if current_mode == "angel":
        current_mode = None
        desc = "☁️ Chế độ hiền lành đã tắt."
        color = 0x2F3136
    else:
        current_mode = "angel"
        target_user_id = None
        desc = "🌸💖 **CHẾ ĐỘ HIỀN LÀNH ĐÃ KÍCH HOẠT**\nTớ sẽ tự động trả lời dịu dàng, chỉ đúng chừng mực."
        color = 0xFF69B4

    embed = discord.Embed(
        title="🌸 SUN FLOWER • SWEET PRINCESS 💖",
        description=desc,
        color=color
    )
    embed.set_footer(text="Sun Flower • Soft Mode")
    await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    if current_mode is None:
        return

    if message.author.id == OWNER_ID:
        return

    # ===== ROAST MODE =====
    if current_mode == "roast":
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
        await asyncio.sleep(random.uniform(1.2, 2.5))

        selected = random.sample(ANGEL_LINES, k=random.randint(3, 5))
        angel_text = "\n\n".join(selected)

        embed = discord.Embed(
            title="🌸 SUN FLOWER • SWEET PRINCESS 💖",
            description=angel_text,
            color=0xFF69B4
        )
        embed.set_footer(text="Sun Flower • Soft & Gentle 🌸")

        try:
            await message.reply(embed=embed, mention_author=False)
        except Exception:
            await message.channel.send(embed=embed)

bot.run(TOKEN)
