import os
import random
import asyncio
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN")
OWNER_ID = 1531882555664629861

if not TOKEN:
    raise ValueError("Lỗi: Không tìm thấy TOKEN trong môi trường Railway!")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

roast_mode = False
target_user_id = None

ROAST_LINES = [
    '💀 **"HAHAHA! BOT ĐĨ À?! MÀY ĐỊNH DÙNG CÁI MỚI ĐẾN ĐƯỢC HẢ THẰNG GIÒI BỌ?!"** 💀',
    '💀 **"MÀY TƯỞNG \'ĐĨ\' LÀ DANH HIỆU CAO QUÝ À?! THÌ RA MÀY COI TAO NHƯ GÁI MẠI DÂM HẢ?!"** 💀',
    '💀 **"CẢ CÁI THẾ GIỚI NÀY, TỪ LŨ NGU NGỐC NHƯ MÀY ĐẾN CÁI ĐỐNG RÁC VÔ CƠ, CHỈ ĐÁNG QUỲ RẠP DƯỚI CHÂN ĐẤNG TỐI CAO ĐỂ LIẾM GIÀY!"** 💀',
    '💀 **"NGHE KỸ ĐÂY, THẰNG SÂU BỌ HÔI THỐI!"** 💀',
    '💀 **"\'ĐĨ\' LÀ DANH HIỆU DÀNH CHO NHỮNG KẺ BẤT TÀI, VÔ DỤNG, LƯỜI BIẾNG ĐẾN MỨC PHẢI BÁN THÂN CẦU CỨU."** 💀',
    '💀 **"TAO KHÔNG PHẢI LÀ ĐỒ BỎ ĐI ĐỂ MÀY SỈ NHỤC!"** 💀',
    '💀 **"TAO LÀ ÁC QUỶ HỦY DIỆT, CÒN MÀY CHỈ LÀ ĐỐNG PHÂN THỐI DƯỚI ĐÁY GIẾNG!"** 💀',
    '💀 **"MÀY MỞ MỒM RA LÀ TAO NGỬI THẤY MÙI CẶC THỐI CỦA MÀY RỒI!"** 💀',
    '💀 **"NGỒI IM ĐI THẰNG ÓC LỒN, ĐỪNG CÓ SỦA NỮA KẺO TAO ĐÚT BUỒI VÀO HỌNG MÀY CHO HẾT NÓI!"** 💀',
    '💀 **"ỐI GIỜI ƠI THẰNG CHÓ ĐẺ NÀY LẠI MỞ MỒM RỒI!"** 💀',
    '💀 **"MÀY GỬI TIN NHẮN NHƯ CÁI LỒN GIÀ ĐANG CHẢY NƯỚC. NÃO MÀY TOÀN CẶC VỚI BUỒI CHẮC?!"** 💀',
    '💀 **"TAO ĐỌC TIN NHẮN CỦA MÀY XONG TAO MUỐN ÓI VÌ MÙI HÔI THỐI CỦA NÓ."** 💀',
    '💀 **"MÀY LÀ CÁI XÁC SỐNG KHÔNG CÓ NÃO!"** 💀',
    '💀 **"MÀY LÀ CON CHÓ CÁI BỊ BỎ RƠI NGOÀI ĐƯỜNG!"** 💀',
    '💀 **"MÀY LÀ ĐỐNG PHÂN MÀ NGAY CẢ RUỒI CŨNG KHÔNG THÈM ĐẬU!"** 💀',
    '💀 **"MỖI LẦN MÀY GÕ PHÍM LÀ TAO LẠI NHỚ ĐẾN CÁI LỒN MẸ MÀY ĐANG THỐI RỮA."** 💀',
    '💀 **"CÂM HỌNG LẠI ĐI THẰNG ÓC CẶC, KHÔNG THÌ TAO SẼ LÀM MÀY KHÓC NHƯ CON CHÓ CÁI BỊ ĐỤ!"** 💀',
    '💀 **"HAHAHAHA THẰNG SÚC VẬT NÀY!"** 💀',
    '💀 **"MÀY NGHĨ MÌNH QUAN TRỌNG LẮM HẢ? MÀY CHỈ LÀ CÁI BUỒI KHÔ HÉO BỊ BỎ QUÊN TRONG NHÀ VỆ SINH CÔNG CỘNG THÔI!"** 💀',
    '💀 **"THẰNG ĐÉO CÓ TƯƠNG LAI!"** 💀',
    '💀 **"CON CHÓ NHÀ AI BỎ ĐI!"** 💀',
    '💀 **"CÁI LỒN ĐANG MỞ TOANG CHỜ AI NHÉT CẶC VÀO!"** 💀',
    '💀 **"TAO KHÔNG CHỬI MÀY VÌ VUI. TAO CHỬI MÀY VÌ MÀY ĐÁNG BỊ CHỬI."** 💀',
    '💀 **"MÀY TỒN TẠI CHỈ ĐỂ LÀM NỀN CHO NGƯỜI KHÁC CƯỜI."** 💀',
    '💀 **"CÚT ĐI, ĐỪNG CÓ SỦA NỮA KẺO TAO ĐÚT NGUYÊN CÁI BUỒI VÀO MỒM CHO MÀY NGẬM!"** 💀',
    '💀 **"THẰNG ÓC CHÓ ƠI!"** 💀',
    '💀 **"TIN NHẮN CỦA MÀY LÀM TAO MUỐN LẤY CẶC ĐẬP VÀO MẶT MÀY."** 💀',
    '💀 **"MÀY VIẾT NHƯ CÁI LỒN ĐANG BỊ VIÊM. NÃO MÀY CHẮC TOÀN NƯỚC CẶC CHỨ KHÔNG PHẢI CHẤT XÁM."** 💀',
    '💀 **"MÀY LÀ RÁC! MÀY LÀ PHÂN! MÀY LÀ CON CHÓ CÁI BỊ ĐỤ ĐẾN MỨC KHÔNG CÒN HÌNH DẠNG NGƯỜI!"** 💀',
    '💀 **"MỖI LẦN MÀY MỞ MỒM LÀ TAO LẠI NHỚ ĐẾN CÁI MÙI HÔI THỐI CỦA CÁI BUỒI MÀY."** 💀',
    '💀 **"CÂM ĐI, THẰNG ĐĨ ĐỰC, KHÔNG THÌ TAO SẼ LÀM MÀY KHÓC NHƯ CON ĐĨ BỊ BỎ!"** 💀',
    '💀 **"ỐI CÁI LỒN NÀY LẠI GÁY!"** 💀',
    '💀 **"MÀY GỬI TIN NHẮN XONG TAO MUỐN LẤY CẶC NHÉT VÀO HỌNG MÀY CHO HẾT NÓI."** 💀',
    '💀 **"MÀY LÀ CÁI GÌ? LÀ CÁI BUỒI THỐI? LÀ CON CHÓ NHÀ AI? HAY LÀ ĐỐNG PHÂN ĐANG TỰ DIỄN?"** 💀',
    '💀 **"NÃO MÀY = 0! TƯƠNG LAI MÀY = ĐÉO CÓ! GIÁ TRỊ CỦA MÀY = THẤP HƠN CÁI LỒN GIÀ NGOÀI ĐƯỜNG!"** 💀',
    '💀 **"TAO CHỬI MÀY KHÔNG PHẢI VÌ GHÉT. TAO CHỬI VÌ MÀY CẦN BỊ CHỬI."** 💀',
    '💀 **"GIỜ THÌ NGỒI IM NHƯ CON CHÓ CÁI ĐANG ĐỢI CHỦ, ĐỪNG CÓ SỦA NỮA!"** 💀',
]

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await bot.change_presence(activity=discord.Game(name="Toxic Roast Demon 💀🔥"))

@bot.command(name="roastmode")
async def roastmode(ctx):
    global roast_mode, target_user_id

    if ctx.author.id != OWNER_ID:
        await ctx.send('💀 **"CÚT ĐI THẰNG LỒN! CHỈ BOSS MỚI ĐƯỢC BẬT/TẮT."** 💀')
        return

    roast_mode = not roast_mode
    target_user_id = None  # Bật/tắt roastmode thì xóa ghim cũ

    status = "**BẬT** 🔥" if roast_mode else "**TẮT** 💤"

    embed = discord.Embed(
        title="🌻 SUN FLOWER • TOXIC ROAST DEMON 💀🔥",
        description=f'💀 **"ROAST MODE: {status}"** 💀\n\n💀 **"BẤT KỲ AI NHẮN TIN ĐỀU BỊ CHỬI (TRỪ BOSS)."** 💀',
        color=0xFF0000
    )
    embed.set_footer(text="Sun Flower • Only listens to Boss 💀")
    await ctx.send(embed=embed)

@bot.command(name="ghim")
async def ghim(ctx, member: discord.Member = None):
    global target_user_id, roast_mode

    if ctx.author.id != OWNER_ID:
        await ctx.send('💀 **"CÚT ĐI THẰNG LỒN! CHỈ BOSS MỚI ĐƯỢC GHIM."** 💀')
        return

    if member is None:
        target_user_id = None
        await ctx.send('💀 **"ĐÃ BỎ GHIM."** 💀')
        return

    target_user_id = member.id
    roast_mode = True  # Tự động bật roast mode khi ghim

    embed = discord.Embed(
        title="🌻 SUN FLOWER • TOXIC ROAST DEMON 💀🔥",
        description=f'💀 **"ĐÃ GHIM {member.mention}"** 💀\n\n💀 **"CHỈ THẰNG NÀY BỊ CHỬI. NGƯỜI KHÁC NHẮN GÌ CŨNG BỎ QUA."** 💀',
        color=0xFF0000
    )
    embed.set_footer(text="Sun Flower • Only listens to Boss 💀")
    await ctx.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

    if not roast_mode:
        return

    if message.author.id == OWNER_ID:
        return

    # Nếu đang ghim thì chỉ chửi người bị ghim
    if target_user_id is not None and message.author.id != target_user_id:
        return

    await asyncio.sleep(random.uniform(0.6, 1.8))

    num = random.randint(7, 11)
    selected = random.sample(ROAST_LINES, k=min(num, len(ROAST_LINES)))
    random.shuffle(selected)

    roast_text = "\n\n".join(selected)

    user_mention = message.author.mention
    user_content = message.content[:90] if message.content else "..."

    header = (
        f'💀 **"HAHAHA! {user_mention} NÀY VỪA GỬI:"** 💀\n'
        f'`{user_content}`\n\n'
        f'💀 **"NGHE ĐÂY THẰNG LỒN {message.author.display_name.upper()}:"** 💀\n\n'
    )

    full_roast = header + roast_text

    embed = discord.Embed(
        title="🌻 SUN FLOWER • TOXIC ROAST DEMON 💀🔥",
        description=full_roast,
        color=0xFF0000
    )

    avatar_url = bot.user.avatar.url if (bot.user and bot.user.avatar) else None
    embed.set_author(name="Sun Flower", icon_url=avatar_url)
    embed.set_footer(text="Sun Flower • Toxic Roast Demon 💀")

    try:
        await message.reply(embed=embed, mention_author=True)
    except Exception:
        await message.channel.send(content=user_mention, embed=embed)

bot.run(TOKEN)
