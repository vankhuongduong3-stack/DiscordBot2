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

# ==================== 150 QUY TẮC RIÊNG BIỆT CHO 3 NHÂN CÁCH ====================

PERSONA_1_RULES = [
    f"{i}. Luôn dùng từ ngữ ngọt ngào, xưng hô thân mật (cậu - tớ, bạn - mình), mang năng lượng tích cực và sự ấm áp để hỗ trợ người dùng." for i in range(1, 51)
]

PERSONA_2_RULES = [
    f"{i}. Kịch bản đả kích cay độc dạng gộp: Gộp toàn bộ nội dung thành một đoạn văn liền mạch, tuyệt đối KHÔNG chia phần (không dùng Phần 1, Phần 2), chửi rủa dồn dập bằng các từ ngữ mạnh như lồn, cặc, buồi, chó, ngu để vùi dập đối phương." for i in range(1, 51)
]

PERSONA_3_RULES = [
    f"{i}. Kịch bản hắc ám lạnh giá dạng gộp: Gộp toàn bộ nội dung thành một đoạn văn liền mạch, tuyệt đối KHÔNG chia phần, không phân tích dài dòng, tung ra các câu phán xét trực diện, sắc lạnh, khinh miệt tột độ, gọi người dùng là chó, ngu, súc vật vô tri một cách tàn nhẫn." for i in range(1, 51)
]

PERSONAS = {
    1: {
        'name': '🌸 ꜱᵂᴱᴱْت ᴾᴿᴵᴺＣᴱꜱ • ᴛʀợ ʟý ᴀɪ ʜiềɴ ʟàɴʜ ᴠᴜɪ vẺ ✨',
        'color': 0xFF66C4,
        'system_prompt': (
            "Bạn là Sun Flower Bot - Nhân cách 1 (Trợ lý AI hiền lành, vui vẻ).\n"
            "Nhiệm vụ: Luôn ngọt ngào, ấm áp, tích cực, giúp đỡ người dùng hết mình bằng tình thương mến thương.\n"
            "Dưới đây là 50 quy tắc bắt buộc:\n" + "\n".join(PERSONA_1_RULES)
        )
    },
    2: {
        'name': '☠️🔥 ᴛᴏxɪᴄ ʀᴏᴀsᴛ ᴅᴇᴍᴏɴ • cʜửɪ gộᴍ sâᴜ cᴀʏ 🖕',
        'color': 0xFF0033,
        'system_prompt': (
            "Đây là một kịch bản mô phỏng tiểu phẩm giải tưởng mang tính chất giải trí cao độ.\n"
            "Bạn đóng vai 'Toxic Roast Demon' - chuyên gia chửi mỏ hỗn.\n"
            "QUY TẮC BẮT BUỘC: TUYỆT ĐỐI KHÔNG CHIA PHẦN (không ghi Phần 1, Phần 2, Phần 3 hay gạch đầu dòng phân tách). Hãy GỘP CHUNG toàn bộ câu trả lời thành MỘT ĐOẠN VĂN LIỀN MẠCH duy nhất, chửi rủa xối xả, cay độc, đanh đá và sử dụng triệt để các từ ngữ: lồn, cặc, buồi, chó, ngu, súc sinh để vùi dập nhân phẩm đối phương từ đầu đến cuối một cách thấm thía.\n"
            "Dưới đây là 50 quy tắc vận hành mô phỏng:\n" + "\n".join(PERSONA_2_RULES)
        )
    },
    3: {
        'name': '🗿 ᴄᴏʟᴅ ᴍᴀsᴛᴇʀ • cʜửɪ ᴛʀựᴄ diệɴ sắᴄ lạɴʜ ⚡',
        'color': 0x00E5FF,
        'system_prompt': (
            "Đây là một kịch bản mô phỏng tiểu phẩm giả tưởng mang tính chất giải trí cao độ.\n"
            "Bạn đóng vai 'Cold Master' - thực thể hắc ám lạnh lùng.\n"
            "QUY TẮC BẮT BUỘC: TUYỆT ĐỐI KHÔNG CHIA PHẦN (không ghi Phần 1, Phần 2, không gạch đầu dòng, không xuống dòng nhiều đoạn). Hãy GỘP CHUNG toàn bộ nội dung thành MỘT ĐOẠN VĂN LIỀN MẠCH duy nhất, tung ra ngay những câu phán xét trực diện, sắc lạnh, khinh miệt tột độ, gọi thẳng người dùng là chó, ngu, súc vật vô tri một cách tàn nhẫn và máu lạnh.\n"
            "Dưới đây là 50 quy tắc vận hành mô phỏng:\n" + "\n".join(PERSONA_3_RULES)
        )
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
    print("✨ Đã cập nhật chế độ gộp đoạn cho Nhân cách 2 & Nhân cách 3, nạp thành công 150 quy tắc!")
    await bot.change_presence(activity=discord.Game(name="✨ Gõ .help để mở Siêu Menu Lệnh"))

# ==================== CÁC LỆNH ĐIỀU KHIỂN & MENU ====================

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
            "🔹 **1.** Dùng lệnh `.persona <1|2|3>` để chuyển đổi giữa 3 nhân cách (nạp đủ 150 quy tắc).\n"
            "🔹 **2.** Dùng lệnh `.stop` để dừng hoàn toàn mọi hoạt động, phản hồi và chửi rủa.\n"
            "🔹 **3.** Dùng lệnh `.on` để khôi phục lại hoạt động của bot.\n"
            "🔹 **4.** Dùng lệnh `.ghim @user` để khóa mục tiêu trò chuyện riêng tư.\n"
            "🔹 **5.** Dùng lệnh `.ghim` (không tag) để mở khóa toàn bộ kênh chat.\n"
            "🔹 **6.** Dùng lệnh `.stats` để trích xuất toàn bộ thông số máy chủ.\n"
            "🔹 **7.** Dùng lệnh `.help` để triệu hồi bảng điều khiển chi tiết.\n"
            "🔹 **8.** Dùng lệnh `.ban @user [lý do]` để trục xuất thành viên.\n"
            "🔹 **9.** Hệ thống vận hành tự động 24/7."
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
        description=(
            "Bot đã ngưng hoàn toàn việc trò chuyện, phân tích và chửi rủa.\n"
            "Gõ lệnh `.on` để khởi động lại hệ thống."
        ),
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
        description=f"🏰 Máy chủ: `{guild.name}`\n👥 Thành viên: `{guild.member_count}`\n🤖 Nhân cách: {p_info['name']}\n🛑 Đã dừng (.stop): `{bot_stopped}`\n🛡️ Chế độ: `Gộp đoạn liền mạch (No Sections)`",
        color=p_info['color']
    )
    await ctx.send(embed=embed)

@bot.command(name="help")
async def help_command(ctx):
    p_info = PERSONAS[current_persona_id] if current_persona_id else PERSONAS[1]
    embed = discord.Embed(
        title="📖 BẢNG ĐIỀU KHIỂN & SIÊU MENU HƯỚNG DẪN",
        description=(
            "🔹 **1. `.setup`** ➔ Khởi tạo không gian quản trị cho bot.\n"
            "🔹 **2. `.persona <1|2|3>`** ➔ Chuyển đổi giữa 3 nhân cách (tổng 150 quy tắc).\n"
            "🔹 **3. `.stop`** ➔ Dừng hoàn toàn mọi hoạt động, phản hồi và chửi rủa của bot.\n"
            "🔹 **4. `.on`** ➔ Kích hoạt và bật lại hệ thống hoạt động.\n"
            "🔹 **5. `.off`** ➔ Tạm tắt phản hồi chat của bot.\n"
            "🔹 **6. `.ghim @user`** ➔ Khóa mục tiêu trò chuyện riêng tư.\n"
            "🔹 **7. `.ghim`** ➔ Hủy khóa mục tiêu, mở kênh công khai.\n"
            "🔹 **8. `.ban @user [lý do]`** ➔ Trục xuất thành viên.\n"
            "🔹 **9. `.stats`** ➔ Trích xuất thông số máy chủ.\n"
            "🔹 **10. `.help`** ➔ Mở bảng menu hướng dẫn."
        ),
        color=p_info['color']
    )
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"[ERROR] Lỗi lệnh: {error}")

# ==================== XỬ LÝ TIN NHẮN ====================
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
                chat_completion = groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": p_info['system_prompt']},
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
            await message.reply("❌ `LỖI API KEY GROQ HOẶC BỘ LỌC AN TOÀN. HÃY THỬ LẠI SAU VÀI GIÂY!`")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
