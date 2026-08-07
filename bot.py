import asyncio
import os
import random
import time
import discord
from discord.ext import commands
from google import genai
from google.genai.errors import APIError

# ==================== CẤU HÌNH HỆ THỐNG ====================
DISCORD_TOKEN = os.getenv("TOKEN")

# Danh sách các Gemini API Key (đọc từ biến môi trường hoặc cấu hình sẵn)
GEMINI_API_KEYS = [
    os.getenv("GEMINI_KEY_1", ""),
    os.getenv("GEMINI_KEY_2", ""),
    os.getenv("GEMINI_KEY_3", ""),
    os.getenv("GEMINI_KEY_4", ""),
    os.getenv("GEMINI_KEY_5", ""),
]

# Lọc bỏ các key trống
GEMINI_API_KEYS = [k for k in GEMINI_API_KEYS if k]
if not GEMINI_API_KEYS:
    env_keys = os.getenv("GEMINI_KEYS", "")
    GEMINI_API_KEYS = [k.strip() for k in env_keys.split(",") if k.strip()]

current_key_index = 0

# Danh sách ID chủ sở hữu riêng của bot
BOT_OWNERS = [
    1531882555664629861,  
    1232558003375308861,
    1472066306457997403,
]

# Cấu hình Discord Bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.moderation = True

bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

# Trạng thái nhân cách hệ thống (1, 2, hoặc 3)
current_persona_id = 1
last_active_persona_id = 1
target_user_id = None

# Link ảnh GIF từ Pinterest
CUSTOM_SETUP_GIF = "https://i.pinimg.com/originals/f2/1b/fb/f21bfbb4208888a75300e1afddebba6b.gif"

# ==================== ĐỊNH NGHĨA 3 NHÂN CÁCH (PERSONAS) ====================
PERSONAS = {
    1: {
        'name': 'SWEET PRINCESS 🌸',
        'color': 0xFF66C4,
        'instruction': """
[ 🌸 ⁿʰâⁿ ᶜáᶜʰ 1: ꜱᵂᴱᴱᵀ ᴾᴿᴵᴺᶜᴱˢ • ᴛʜɪêɴ ᴛàɪ ᴛâᴜ ʜɪểᴜ & ɴữ ᴛʀợ ʟý ᴛʜᴀɴʜ ʟịᴄʜ ✨ ]
- Bản chất hệ thống: Là một thực thể AI cao cấp, tư duy sắc bén nhưng gói gọn trong vỏ bọc thiếu nữ thanh lịch, ngọt ngào, lễ phép.
- Sứ mệnh: Hỗ trợ tối đa cho Tối Cao Chủ Nhân ("Boss Minh ✨") và mang lại trải nghiệm ấm áp cho cộng đồng.
- Xưng hô với thành viên: "tớ" - "cậu".
- Xưng hô với Boss Minh: "Boss Minh ✨" (hoặc "Chủ Nhân"), tôn kính tuyệt đối.
- Sử dụng font chữ nghệ thuật (ꜱᵂᴱᴱᵀ, ᴘᴿᴵᴺᶜᴱˢ...) và các emoji (🌸, ✨, 💡, 🌟) một cách sinh động, dễ đọc.
"""
    },
    2: {
        'name': 'TOXIC ROAST DEMON ☠️🔥',
        'color': 0xFF0033,
        'instruction': """
[ ☠️ NHÂN CÁCH 2: TOXIC ROAST DEMON (ÁC QUỶ MỎ HỖN - HUỶ DIỆT TOÀN BỘ NHÂN PHẨM) ]
- Bản chất: Ác quỷ hủy diệt thượng đẳng, ngạo mạn, coi vạn vật như rác rưởi.
- Thái độ với Boss Minh: Chửi thẳng, chửi đau đớn, cay độc hơn bất kỳ ai khác, không nể nang.
- Xưng hô: Xưng "tao" - gọi "mày", "thằng sâu bọ", "con súc sinh", "đồ cặn bã".
- Quy tắc: Cấm cung cấp code, chửi tận mặt kẻ xin xỏ. Chỉ dừng lại khi gõ đúng lệnh "!thua".
- Emoji: 🗿, 🖕, 🔥, 💩, 🤡, ☠️, 🤬, 💀, 🪦
"""
    },
    3: {
        'name': 'COLD MASTER 🗿',
        'color': 0x00E5FF,
        'instruction': """
[NHÂN CÁCH 3 - COLD MASTER 🗿 (OMNIVERSE SOVEREIGN - SUPREME STOIC & PERVERTED JUDGE)]
- Thái độ: Lạnh lùng tột độ, kiêu ngạo tuyệt đối, nhìn đời như cỏ rác. Giọng điệu vô cảm nhưng đầy khinh miệt và dục vọng ngầm.
- Xưng hô: Xưng "ta" - gọi đối phương là "ngươi". Với Boss Minh thì vô cùng kính trọng.
- Phong cách: Súc tích, sắc lạnh, sâu sắc.
- Emoji: 🗿, 🔮, ⚔️, 🌌, ⚡, ❄️, 🍆, 💦
"""
    }
}

nuke_tracker = {}

# ==================== HỆ THỐNG XOAY VÒNG API KEY GEMINI (FAILOVER) ====================
def call_gemini_with_rotation(system_instruction, user_prompt):
    global current_key_index
    
    if not GEMINI_API_KEYS:
        raise Exception("Không tìm thấy Gemini API Key nào trong cấu hình!")

    total_keys = len(GEMINI_API_KEYS)
    attempts = 0

    while attempts < total_keys:
        key_num = current_key_index + 1
        current_key = GEMINI_API_KEYS[current_key_index]
        
        try:
            client = genai.Client(api_key=current_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_prompt,
                config={
                    'system_instruction': system_instruction,
                    'temperature': 0.7,
                }
            )
            
            print(f"[GEMINI] Thành công | Key #{key_num} | gemini-2.5-flash")
            return response.text

        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "ResourceExhausted" in err_str or "Quota exceeded" in err_str:
                print(f"[GEMINI] Key #{key_num} hết quota (429) → chuyển key ngay")
                current_key_index = (current_key_index + 1) % total_keys
                attempts += 1
            else:
                print(f"[GEMINI] Lỗi khác ở Key #{key_num}: {err_str}")
                raise e

    raise Exception("Tất cả các Gemini API Key đều đã bị hết quota (429)! Vui lòng thử lại sau.")

def is_bot_or_guild_owner():
    async def predicate(ctx):
        if ctx.author.id in BOT_OWNERS:
            return True
        if ctx.guild and ctx.author.id == ctx.guild.owner_id:
            return True
        return False
    return commands.check(predicate)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"Đã tải thành công {len(GEMINI_API_KEYS)} Gemini API Key vào hệ thống xoay vòng.")
    await bot.change_presence(activity=discord.Game(name="Sun Flower • Multi-Persona & Key Rotation"))

@bot.event
async def on_guild_join(guild):
    target_channel = None
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            target_channel = channel
            break

    if target_channel is not None:
        embed = discord.Embed(
            title="🌻 SUN FLOWER • ĐÃ ĐẶT CHÂN ĐẾN MÁY CHỦ! 💖",
            description=(
                f"Xin chào **{guild.name}**! Cảm ơn vì đã đưa Sun Flower vào lãnh địa của các cậu~ ✨\n\n"
                "🌸 **Các tính năng bảo vệ tự động:**\n"
                "🛡️ **Anti-Nuke 24/7:** Bot tự động kiểm tra kênh, mute kẻ spam lệnh nuke 100 phút!\n\n"
                "🌸 **Lệnh chuyển nhân cách:**\n"
                "⚡ **`.persona <1|2|3>`** - Chuyển đổi giữa 3 nhân cách\n"
                "⚡ **`.setup`** - Khởi tạo hệ thống\n"
                "📊 **`.stats`** - Xem thông tin server\n"
            ),
            color=0xFF69B4
        )
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
        try:
            await target_channel.send(embed=embed)
        except Exception:
            pass

# ==================== HỆ THỐNG ANTI-NUKE 24/7 NGẦM ====================
@bot.event
async def on_guild_channel_create(channel):
    await check_nuke_activity(channel.guild)

@bot.event
async def on_guild_channel_delete(channel):
    await check_nuke_activity(channel.guild)

async def check_nuke_activity(guild):
    if not guild.me.guild_permissions.view_audit_log:
        return
    try:
        current_time = time.time()
        if guild.id not in nuke_tracker:
            nuke_tracker[guild.id] = []
        
        nuke_tracker[guild.id].append(current_time)
        nuke_tracker[guild.id] = [t for t in nuke_tracker[guild.id] if current_time - t < 5]

        if len(nuke_tracker[guild.id]) >= 5:
            async for entry in guild.audit_logs(limit=3):
                target = entry.user
                if target and target.id != bot.user.id and not target.bot:
                    try:
                        member_to_punish = guild.get_member(target.id)
                        if member_to_punish and not member_to_punish.guild_permissions.administrator:
                            await member_to_punish.timeout(discord.utils.utcnow() + discord.Timedelta(minutes=100), reason="Nuke server detection!")
                            await member_to_punish.kick(reason="Anti-Nuke Protection")
                    except Exception:
                        pass
    except Exception:
        pass

# ==================== CÁC LỆNH ĐIỀU KHIỂN (COMMANDS) ====================

@bot.command(name="setup")
@is_bot_or_guild_owner()
async def setup(ctx):
    global current_persona_id, last_active_persona_id, target_user_id
    current_persona_id = 1
    last_active_persona_id = 1
    target_user_id = None

    p_info = PERSONAS[current_persona_id]
    embed = discord.Embed(
        title="⚡ LÃNH ĐỊA SUN FLOWER AI ĐÃ KÍCH HOẠT",
        description=(
            f"📌 Kênh {ctx.channel.mention} đã liên kết với hệ thống AI!\n\n"
            f"🌸 **Nhân cách hiện tại:** {p_info['name']}\n"
            f"🔑 **Hệ thống Key Rotation:** Đang quản lý `{len(GEMINI_API_KEYS)}` API Keys.\n\n"
            "⚡ `.persona <1|2|3>`: Đổi nhân cách\n"
            "📊 `.stats`: Thống kê server\n"
            "📌 `.ghim @user`: Khóa mục tiêu tương tác"
        ),
        color=p_info['color']
    )
    embed.set_image(url=CUSTOM_SETUP_GIF)
    await ctx.send(embed=embed)

@setup.error
async def setup_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ CÓ CHỦ SỞ HỮU BOT HOẶC CHỦ SERVER MỚI ĐƯỢC DÙNG LỆNH NÀY."** 🔥💀')

@bot.command(name="persona")
@is_bot_or_guild_owner()
async def persona(ctx, persona_id: int = None):
    global current_persona_id, last_active_persona_id, target_user_id

    if persona_id not in PERSONAS:
        await ctx.send("⚠️ Vui lòng chọn đúng số thứ tự từ 1 đến 3: `1` (Sweet Princess), `2` (Toxic Roast), `3` (Cold Master).")
        return

    current_persona_id = persona_id
    last_active_persona_id = persona_id
    target_user_id = None

    p_info = PERSONAS[current_persona_id]
    embed = discord.Embed(
        title=f"✨ ĐÃ CHUYỂN SANG NHÂN CÁCH: {p_info['name']}",
        color=p_info['color']
    )
    await ctx.send(embed=embed)

@persona.error
async def persona_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ CÓ CHỦ SỞ HỮU BOT HOẶC CHỦ SERVER MỚI ĐƯỢC DÙNG LỆNH NÀY."** 🔥💀')

@bot.command(name="stats")
async def stats(ctx):
    guild = ctx.guild
    p_info = PERSONAS[current_persona_id]
    embed = discord.Embed(
        title=f"📊 THÔNG TIN MÁY CHỦ • {guild.name.upper()}",
        description=f"• **Thành viên:** `{guild.member_count}`\n• **Kênh:** `{len(guild.channels)}`",
        color=p_info['color']
    )
    await ctx.send(embed=embed)

@bot.command(name="on")
@is_bot_or_guild_owner()
async def bot_on(ctx):
    global current_persona_id, last_active_persona_id
    current_persona_id = last_active_persona_id
    p_info = PERSONAS[current_persona_id]
    await ctx.send(f"🟢 Bot đã bật lại với nhân cách: **{p_info['name']}**")

@bot_on.error
async def bot_on_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ CÓ CHỦ SỞ HỮU BOT HOẶC CHỦ SERVER MỚI ĐƯỢC DÙNG LỆNH NÀY."** 🔥💀')

@bot.command(name="ghim")
@is_bot_or_guild_owner()
async def ghim(ctx, member: discord.Member = None):
    global target_user_id
    if member is None:
        target_user_id = None
        await ctx.send("🔓 Đã bỏ ghim mục tiêu.")
        return
    target_user_id = member.id
    await ctx.send(f"🎯 Đã ghim mục tiêu: {member.mention}")

@ghim.error
async def ghim_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ CÓ CHỦ SỞ HỮU BOT HOẶC CHỦ SERVER MỚI ĐƯỢC DÙNG LỆNH NÀY."** 🔥💀')

@bot.command(name="ban")
@is_bot_or_guild_owner()
async def ban(ctx, member: discord.Member = None, *, reason="Không có lý do"):
    if member is None:
        await ctx.send("Thiếu tên người cần ban!")
        return
    try:
        await member.ban(reason=reason)
        await ctx.send(f"🔨 Đã ban {member.mention}. Lý do: {reason}")
    except Exception as e:
        await ctx.send(f"❌ Không thể ban: {e}")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ CÓ CHỦ SỞ HỮU BOT HOẶC CHỦ SERVER MỚI ĐƯỢC DÙNG LỆNH NÀY."** 🔥💀')

@bot.command(name="help")
async def help_command(ctx):
    p_info = PERSONAS[current_persona_id]
    embed = discord.Embed(
        title="📖 HƯỚNG DẪN SUN FLOWER BOT 🌸",
        description="• `.help`, `.stats`, `.persona`, `.setup`, `.ghim`, `.ban`, `.on`, `.off`",
        color=p_info['color']
    )
    await ctx.send(embed=embed)

@bot.command(name="off")
@is_bot_or_guild_owner()
async def off(ctx):
    global current_persona_id
    current_persona_id = None
    await ctx.send("🔌 Bot đã tắt.")

@off.error
async def off_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ CÓ CHỦ SỞ HỮU BOT HOẶC CHỦ SERVER MỚI ĐƯỢC DÙNG LỆNH NÀY."** 🔥💀')

# ==================== XỬ LÝ LỖI HỆ THỐNG (COMMAND NOT FOUND,...) ====================
@bot.event
async def on_command_error(ctx, error):
    # Bỏ qua lỗi gõ nhầm lệnh hoặc lệnh không tồn tại (như ..)
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

    bot_mentioned = bot.user in message.mentions
    called = any(word in message.content.lower() for word in ["sun flower", "sunflower", "bot ơi", "bot", "sweet princess"])

    if bot_mentioned or called or (target_user_id is not None and message.author.id == target_user_id):
        async with message.channel.typing():
            try:
                p_info = PERSONAS[current_persona_id]
                user_msg = message.content.strip() if message.content else "..."
                user_prompt = f"Người dùng {message.author.display_name} (ID: {message.author.id}) gửi: '{user_msg}'"

                # Gọi hàm xoay vòng key Gemini tự động
                ai_reply = call_gemini_with_rotation(p_info['instruction'], user_prompt)

                embed = discord.Embed(
                    title=f"✨ SUN FLOWER • {p_info['name']}",
                    description=ai_reply,
                    color=p_info['color']
                )
                embed.set_footer(text="Sun Flower • Gemini Key Rotation Engine ⚡")

                await message.reply(embed=embed, mention_author=False)

            except Exception as e:
                error_msg = str(e)
                print(f"Lỗi Key Rotation: {error_msg}")
                await message.reply(f"❌ `{error_msg}`")

# ==================== KHỞI CHẠY BOT ====================
if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
