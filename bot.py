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

# Khởi tạo Groq Client chính thức
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Danh sách ID chủ sở hữu tối cao của hệ thống Bot
BOT_OWNERS = [
    1531882555664629861,  
    1232558003375308861,
    1472066306457997403,
]

# Cấu hình Discord Bot Intents
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
        'system_prompt': "Bạn là Sun Flower Bot - trợ lý AI siêu trí tuệ, cực kỳ thông minh, tận tụy, nhẹ nhàng, lễ phép. Luôn giải đáp chi tiết các thắc mắc về code, game, đời sống. Sử dụng phong cách ngọt ngào, xưng 'tớ' - 'cậu', kèm emoji 🌸, ✨, 💡, 🌟."
    },
    2: {
        'name': '☠️🔥 ᴛᴏxɪᴄ ʀᴏᴀsᴛ ᴅᴇᴍᴏɴ • ʜᴜỷ ᴅiệᴛ ɴʜâɴ ᴘʜẩᴍ 🖕',
        'color': 0xFF0033,
        'system_prompt': "Bạn là Toxic Roast Demon - ác quỷ mỏ hỗn thượng đẳng, ngạo mạn, chửi thẳng thừng, cay độc, không nể nang người dùng. Xưng 'tao' - gọi 'mày', 'thằng sâu bọ'. Sử dụng nhiều emoji cà khịa: 🗿, 🖕, 🔥, 💩, 🤡, ☠️."
    },
    3: {
        'name': '🗿 ᴄᴏʟᴅ ᴍᴀsᴛᴇʀ • ᴏᴍɴɪᴠᴇʀsᴇ sᴏᴠᴇʀᴇɪɢɴ ⚡',
        'color': 0x00E5FF,
        'system_prompt': "Bạn là Cold Master - bậc thầy lạnh lùng, cao ngạo, uy quyền tột độ trong omniverse. Xưng 'ta' - gọi đối phương là 'ngươi'. Sử dụng emoji: 🗿, 🔮, ⚔️, 🌌, ⚡, ❄️."
    }
}

nuke_tracker = {}

# ==================== HỆ THỐNG KIỂM TRA QUYỀN NĂNG ====================
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
    print("✨ Hệ thống Groq AI thông minh đã sẵn sàng hoạt động!")
    await bot.change_presence(activity=discord.Game(name="✨ Gõ .help để mở Siêu Menu Lệnh"))

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
            f"🌸 **Nhân cách khởi tạo mặc định:** `{p_info['name']}`\n\n"
            "🔸 **`.persona <1|2|3>`** ➔ Chuyển đổi linh hoạt giữa 3 nhân cách.\n"
            "🔸 **`.ghim @user`**      ➔ Khóa mục tiêu trò chuyện riêng tư.\n"
            "🔸 **`.stats`**          ➔ Trích xuất thông số máy chủ.\n"
            "🔸 **`.help`**           ➔ Triệu hồi Siêu Menu hướng dẫn.\n"
            "🔸 **`.on` / `.off`**    ➔ Bật hoặc tắt trạng thái tiếp nhận chat."
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
        await ctx.send("⚠️ Vui lòng chọn đúng số nhân cách: `.persona 1`, `.persona 2` hoặc `.persona 3`")
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
        title="📊 THÔNG SỐ KỸ THUẬT MÁY CHỦ",
        description=(
            f"🏰 **Server:** `{guild.name}`\n"
            f"👥 **Thành viên:** `{guild.member_count}`\n"
            f"🤖 **Nhân cách hiện tại:** {p_info['name']}\n"
            f"🛡️ **Bảo vệ:** `Anti-Nuke Active`"
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
        title="🟢 KÍCH HOẠT HỆ THỐNG TRỰC TUYẾN",
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
        title="🔌 NGẮT KẾT NỐI HỆ THỐNG",
        description="Đã tạm tắt phản hồi chat của bot. Gõ `.on` để bật lại.",
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
        await ctx.send("🔓 Đã hủy ghim mục tiêu. Bot trò chuyện với tất cả mọi người.")
        return
    target_user_id = member.id
    await ctx.send(f"🎯 Đã ghim mục tiêu trò chuyện riêng tư với: {member.mention}")

@ghim.error
async def ghim_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"LỆNH BỊ TỪ CHỐI! BẠN KHÔNG ĐỦ QUYỀN HẠN!"** 🔥💀')

@bot.command(name="ban")
@has_high_privilege()
async def ban(ctx, member: discord.Member = None, *, reason="Không có lý do"):
    if member is None:
        await ctx.send("⚠️ Vui lòng tag thành viên cần ban! Ví dụ: `.ban @user lý do`")
        return
    try:
        await member.ban(reason=reason)
        await ctx.send(f"🔨 Đã trục xuất thành công {member.mention}. Lý do: `{reason}`")
    except discord.Forbidden:
        # Ẩn hoàn toàn mã lỗi 403 Forbidden / code 50013, thay bằng thông báo thân thiện
        await ctx.send("🛡️ **Không thể thực thi lệnh:** Bot thiếu quyền Ban Members hoặc vai trò của mục tiêu cao hơn bot!")
    except Exception as e:
        await ctx.send("❌ Đã xảy ra lỗi khi thực thi lệnh.")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"LỆNH BỊ TỪ CHỐI! BẠN KHÔNG ĐỦ QUYỀN HẠN!"** 🔥💀')

@bot.command(name="help")
async def help_command(ctx):
    p_info = PERSONAS[current_persona_id] if current_persona_id else PERSONAS[1]
    embed = discord.Embed(
        title="📖 SIÊU MENU ĐIỀU KHIỂN • SUN FLOWER",
        description=(
            "• **`.setup`** ➔ Khởi tạo không gian quản trị.\n"
            "• **`.persona <1|2|3>`** ➔ Đổi nhân cách AI (1: Sweet, 2: Toxic Roast, 3: Cold Master).\n"
            "• **`.ghim @user`** ➔ Khóa mục tiêu trò chuyện riêng tư.\n"
            "• **`.on` / `.off`** ➔ Bật/tắt nhanh phản hồi chat của bot.\n"
            "• **`.ban @user [lý do]`** ➔ Trục xuất thành viên.\n"
            "• **`.stats`** ➔ Xem thông số server."
        ),
        color=p_info['color']
    )
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"[ERROR] Lỗi lệnh: {error}")

# ==================== XỬ LÝ TIN NHẮN (GROQ AI) ====================
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
        called = any(word in message.content.lower() for word in ["sun flower", "sunflower", "bot ơi", "bot", "sún"])
        if bot_mentioned or called or (target_user_id is not None and message.author.id == target_user_id):
            should_reply = True

    if should_reply:
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
                        max_tokens=1000,
                    )
                    ai_reply = chat_completion.choices[0].message.content
                else:
                    ai_reply = "⚠️ Chưa thiết lập biến môi trường GROQ_API_KEY!"

                embed = discord.Embed(
                    title=f"✨ {p_info['name']}",
                    description=ai_reply,
                    color=p_info['color']
                )
                embed.set_footer(text="Sun Flower AI • Powered by Groq ⚡")

                await message.reply(embed=embed, mention_author=False)

            except Exception as e:
                print(f"Lỗi Groq AI: {e}")
                await message.reply("❌ `Lỗi API Key Groq không hợp lệ hoặc hết hạn. Vui lòng kiểm tra lại Key trên Railway!`")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
