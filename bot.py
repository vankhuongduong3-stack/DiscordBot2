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

bot = commands.Bot(command_prefix=(".", "/", "?", "@", "#"), intents=intents, help_command=None)

current_persona_id = 1
last_active_persona_id = 1
target_user_id = None
bot_stopped = False
spam_task_running = None

CUSTOM_SETUP_GIF = "https://i.pinimg.com/originals/f2/1b/fb/f21bfbb4208888a75300e1afddebba6b.gif"

# ==================== KHO SPAM ĐẦY ĐỦ ====================
ROAST_LINES = [
    '# 💀🔥 "Mày là thằng óc cặc ngu nhất quả đất, não toàn lồn!" 🔥💀 @{username}',
    '# ☠️🤡 "Cái buồi mày nhỏ tí, mẹ mày chắc hối hận vì đẻ ra chó ngu này!" 🤡☠️ @{username}',
    '# 🩸🔥 "Thằng chó đẻ óc lồn, cặc mày thối như phân!" 🔥🩸 @{username}',
    '# 💀☠️ "Mẹ mày đẻ mày ra chỉ để tao chửi, thằng ngu buồi!" ☠️💀 @{username}',
    '# 🤡💩 "Não mày toàn nước cặc, lồn mẹ mày thối rữa rồi!" 💩🤡 @{username}',
    '# 🔥💀 "Thằng chó ngu, buồi mày bé như hạt cát!" 💀🔥 @{username}',
    '# ☠️🩸 "Cặc mày hôi thối, mẹ mày chắc đang khóc vì đẻ ra lồn ngu!" 🩸☠️ @{username}',
    '# 🤮💀 "Mày là con chó cái óc buồi, não toàn lồn!" 💀🤮 @{username}',
    '# 🔥🤡 "Thằng ngu cặc, mẹ mày bán lồn nuôi mày lớn!" 🤡🔥 @{username}',
    '# 💀☠️ "Buồi mày khô héo, chó ngu ơi!" ☠️💀 @{username}',
    '# 💩🤮 "Lồn mẹ mày chảy nước vì đẻ ra thằng óc cặc này!" 🤮💩 @{username}',
    '# 🩸🔥 "Mày ngu như chó, cặc mày thối vãi!" 🔥🩸 @{username}',
    '# 🤡💀 "Thằng buồi ngu, não mày bằng cái lồn già!" 💀🤡 @{username}',
    '# ☠️💩 "Mẹ mày đụ với chó mới đẻ ra mày, thằng óc cặc!" 💩☠️ @{username}',
    '# 🔥🤮 "Cặc mày nhỏ, lồn mẹ mày rộng, mày ngu vãi!" 🤮🔥 @{username}',
    '# 💀🩸 "Thằng chó đẻ, buồi mày như giòi bọ!" 🩸💀 @{username}',
    '# 🤡🔥 "Não mày toàn lồn, cặc mày hôi như phân chó!" 🔥🤡 @{username}',
    '# ☠️💀 "Mẹ mày bán buồi nuôi mày, thằng ngu!" 💀☠️ @{username}',
    '# 💩🔥 "Mày là thằng óc cặc, lồn mẹ mày thối!" 🔥💩 @{username}',
    '# 🩸🤡 "Chó ngu ơi, buồi mày bé tí xíu!" 🤡🩸 @{username}',
    '# 💀☠️ "Cặc mày thối, não mày toàn nước lồn!" ☠️💀 @{username}',
    '# 🔥🤮 "Thằng chó cái óc buồi, mẹ mày hối hận lắm!" 🤮🔥 @{username}',
    '# 🤡💀 "Mày ngu như lồn, cặc mày khô như củi!" 💀🤡 @{username}',
    '# ☠️💩 "Buồi mày hôi, mẹ mày đẻ ra thằng chó ngu!" 💩☠️ @{username}',
    '# 🩸🔥 "Thằng óc cặc, lồn mẹ mày đang chảy vì xấu hổ!" 🔥🩸 @{username}',
    '# 💀🤡 "Chó đẻ ơi, não mày bằng cái buồi!" 🤡💀 @{username}',
    '# 🔥☠️ "Cặc mày nhỏ, mày ngu vãi lồn!" ☠️🔥 @{username}',
    '# 🤡🩸 "Mẹ mày đụ chó mới có mày, thằng buồi thối!" 🩸🤡 @{username}',
    '# 💀💩 "Lồn mẹ mày rộng, cặc mày bé, mày ngu!" 💩💀 @{username}',
    '# 🔥🤮 "Thằng chó ngu óc lồn, buồi mày như phân!" 🤮🔥 @{username}',
    '# ☠️🤡 "Não mày toàn cặc, mẹ mày khóc vì đẻ ra mày!" 🤡☠️ @{username}',
    '# 🩸💀 "Mày là con chó cái, lồn thối, buồi khô!" 💀🩸 @{username}',
    '# 🔥💩 "Thằng óc buồi, cặc mày hôi như xác chết!" 💩🔥 @{username}',
    '# 🤡☠️ "Mẹ mày bán lồn, đẻ ra thằng chó ngu này!" ☠️🤡 @{username}',
    '# 💀🔥 "Cặc mày bé, não mày toàn nước lồn!" 🔥💀 @{username}',
    '# 🤮🩸 "Thằng chó đẻ, buồi mày như giòi!" 🩸🤮 @{username}',
    '# ☠️💩 "Lồn mẹ mày thối, mày ngu như heo!" 💩☠️ @{username}',
    '# 🔥🤡 "Mày óc cặc, mẹ mày hối hận vì đẻ mày!" 🤡🔥 @{username}',
    '# 💀🩸 "Chó ngu ơi, buồi mày thối vãi!" 🩸💀 @{username}',
    '# 🤡🔥 "Cặc mày nhỏ, lồn mẹ mày rộng như chợ!" 🔥🤡 @{username}',
    '# ☠️💀 "Thằng buồi ngu, não mày bằng cái lồn!" 💀☠️ @{username}',
    '# 💩🤮 "Mẹ mày đụ với chó, đẻ ra mày óc cặc!" 🤮💩 @{username}',
    '# 🩸🔥 "Mày là thằng chó cái, lồn thối, cặc bé!" 🔥🩸 @{username}',
    '# 💀🤡 "Não mày toàn nước buồi, mẹ mày khóc!" 🤡💀 @{username}',
    '# 🔥☠️ "Thằng óc lồn, cặc mày hôi như phân!" ☠️🔥 @{username}',
    '# 🤡🩸 "Buồi mày khô, mày ngu như chó!" 🩸🤡 @{username}',
    '# 💀💩 "Lồn mẹ mày chảy, vì đẻ ra thằng cặc ngu!" 💩💀 @{username}',
    '# 🔥🤮 "Chó đẻ ơi, não mày bằng hạt cát!" 🤮🔥 @{username}',
    '# ☠️🤡 "Mày óc buồi, cặc mày thối, mẹ mày bán lồn!" 🤡☠️ @{username}',
    '# 🩸💀 "Thằng ngu cặc, lồn mẹ mày thối rữa!" 💀🩸 @{username}',
    '# 🔥💩 "Mày là con chó, buồi bé, não toàn lồn!" 💩🔥 @{username}',
    '# 🤡☠️ "Cặc mày nhỏ, mẹ mày hối hận đẻ mày!" ☠️🤡 @{username}',
    '# 💀🔥 "Thằng óc lồn, buồi mày như phân chó!" 🔥💀 @{username}',
    '# 🤮🩸 "Não mày toàn nước cặc, mày ngu vãi!" 🩸🤮 @{username}',
    '# ☠️💩 "Mẹ mày đụ chó mới có mày, thằng buồi thối!" 💩☠️ @{username}',
    '# 🔥🤡 "Lồn mẹ mày rộng, cặc mày bé tí!" 🤡🔥 @{username}',
    '# 💀🩸 "Chó ngu ơi, não mày bằng cái lồn già!" 💀🩸 @{username}',
    '# 🤡🔥 "Thằng cặc ngu, buồi mày hôi thối!" 🔥🤡 @{username}',
    '# ☠️💀 "Mày óc buồi, mẹ mày khóc vì đẻ ra chó!" 💀☠️ @{username}',
    '# 💩🤮 "Cặc mày thối, lồn mẹ mày chảy nước!" 🤮💩 @{username}',
    '# 🩸🔥 "Thằng chó đẻ, não toàn nước lồn!" 🔥🩸 @{username}',
    '# 💀🤡 "Buồi mày nhỏ, mày ngu như heo!" 🤡💀 @{username}',
    '# 🔥☠️ "Mẹ mày bán cặc nuôi mày, thằng óc lồn!" ☠️🔥 @{username}',
    '# 🤡🩸 "Mày là thằng chó cái, buồi thối, não ngu!" 🩸🤡 @{username}',
    '# 💀💩 "Lồn mẹ mày thối, cặc mày bé như hạt!" 💩💀 @{username}',
    '# 🔥🤮 "Thằng óc cặc, mày ngu vãi buồi!" 🤮🔥 @{username}',
    '# ☠️🤡 "Não mày toàn lồn, mẹ mày hối hận!" 🤡☠️ @{username}',
    '# 🩸💀 "Chó ngu, buồi mày hôi như xác!" 💀🩸 @{username}',
    '# 🔥💩 "Cặc mày khô, lồn mẹ mày rộng!" 💩🔥 @{username}',
    '# 🤡☠️ "Thằng buồi ngu, não bằng cái cặc!" ☠️🤡 @{username}',
    '# 💀🔥 "Mẹ mày đẻ mày ra chỉ để bị chửi, chó ơi!" 🔥💀 @{username}',
    '# 🤮🩸 "Mày óc lồn, cặc thối, buồi bé!" 🩸🤮 @{username}',
    '# ☠️💩 "Thằng chó cái, não toàn nước cặc!" 💩☠️ @{username}',
    '# 🔥🤡 "Lồn mẹ mày chảy vì xấu hổ đẻ ra mày!" 🤡🔥 @{username}',
    '# 💀🩸 "Buồi mày như giòi, mày ngu như chó!" 💀🩸 @{username}',
    '# 🤡🔥 "Thằng óc cặc, mẹ mày bán lồn nuôi!" 🔥🤡 @{username}',
    '# ☠️💀 "Cặc mày nhỏ, não mày toàn buồi!" 💀☠️ @{username}',
    '# 💩🤮 "Mày là thằng chó ngu, lồn mẹ thối!" 🤮💩 @{username}',
    '# 🩸🔥 "Não mày bằng hạt, cặc mày hôi!" 🔥🩸 @{username}',
    '# 💀🤡 "Thằng buồi thối, mẹ mày khóc!" 🤡💀 @{username}',
    '# 🔥☠️ "Lồn mẹ mày rộng, mày óc cặc ngu!" ☠️🔥 @{username}',
    '# 🤡🩸 "Chó đẻ ơi, buồi mày bé tí xíu!" 🩸🤡 @{username}',
    '# 💀💩 "Mày ngu như lồn, cặc thối như phân!" 💩💀 @{username}',
    '# 🔥🤮 "Thằng óc buồi, mẹ mày hối hận lắm!" 🤮🔥 @{username}',
    '# ☠️🤡 "Cặc mày khô, não toàn nước lồn!" 🤡☠️ @{username}',
    '# 🩸💀 "Mày là con chó cái, buồi hôi, lồn thối!" 💀🩸 @{username}',
    '# 🔥💩 "Thằng ngu cặc, mẹ mày đụ chó đẻ ra!" 💩🔥 @{username}',
    '# 🤡☠️ "Buồi mày nhỏ, mày óc lồn vãi!" ☠️🤡 @{username}',
    '# 💀🔥 "Não mày toàn cặc, chó ngu ơi!" 🔥💀 @{username}',
    '# 🤮🩸 "Lồn mẹ mày thối rữa vì đẻ mày!" 🩸🤮 @{username}',
    '# ☠️💩 "Thằng chó đẻ, cặc bé, buồi thối!" 💩☠️ @{username}',
    '# 🔥🤡 "Mày óc buồi, não bằng cái lồn!" 🤡🔥 @{username}',
    '# 💀🩸 "Mẹ mày bán cặc, đẻ ra thằng ngu!" 🩸💀 @{username}',
    '# 🤡🔥 "Cặc mày hôi, mày ngu như heo chó!" 🔥🤡 @{username}',
    '# ☠️💀 "Thằng lồn ngu, buồi mày như phân!" 💀☠️ @{username}',
    '# 💩🤮 "Não mày toàn nước buồi, chó ơi!" 🤮💩 @{username}',
    '# 🩸🔥 "Mày là thằng óc cặc, mẹ mày khóc!" 🔥🩸 @{username}',
    '# 💀🤡 "Buồi mày bé, lồn mẹ mày rộng!" 🤡💀 @{username}',
    '# 🔥☠️ "Chó ngu, cặc thối, não toàn lồn!" ☠️🔥 @{username}',
    '# 🤡🩸 "Thằng đẻ ra từ lồn chó, óc buồi!" 🩸🤡 @{username}',
    '# 💀💩 "Mẹ mày hối hận, mày ngu vãi cặc!" 💩💀 @{username}',
    '# 🔥🤮 "Cặc mày nhỏ như hạt, não ngu!" 🤮🔥 @{username}',
    '# ☠️🤡 "Thằng chó cái óc lồn, buồi hôi!" 🤡☠️ @{username}',
    '# 🩸💀 "Mày tồn tại chỉ để bị chửi, thằng cặc!" 💀🩸 @{username}',
    '# 🔥💩 "Lồn mẹ mày chảy, vì đẻ ra chó ngu!" 💩🔥 @{username}',
    '# 🤡☠️ "Buồi mày thối, mày óc cặc vãi!" ☠️🤡 @{username}',
    '# 💀🔥 "Não mày bằng cái buồi, chó đẻ!" 🔥💀 @{username}',
    '# 🤮🩸 "Thằng ngu lồn, cặc mày hôi như chết!" 🩸🤮 @{username}',
    '# ☠️💩 "Mẹ mày đụ chó, đẻ ra mày óc buồi!" 💩☠️ @{username}',
    '# 🔥🤡 "Cặc mày bé, mày ngu như con chó!" 🤡🔥 @{username}',
    '# 💀🩸 "Thằng óc cặc, lồn mẹ thối rữa!" 💀🩸 @{username}',
    '# 🤡🔥 "Buồi mày khô, não toàn nước lồn!" 🔥🤡 @{username}',
    '# ☠️💀 "Chó ngu ơi, mày đáng bị nhét cặc!" 💀☠️ @{username}',
    '# 💩🤮 "Mày là thằng lồn, mẹ mày bán buồi!" 🤮💩 @{username}',
    '# 🩸🔥 "Não mày ngu, cặc thối, buồi bé!" 🔥🩸 @{username}',
    '# 💀🤡 "Thằng chó đẻ, óc toàn lồn!" 🤡💀 @{username}',
    '# 🔥☠️ "Mẹ mày khóc vì đẻ ra thằng cặc ngu!" ☠️🔥 @{username}',
    '# 🤡🩸 "Buồi mày như giòi, mày óc lồn!" 🩸🤡 @{username}',
    '# 💀💩 "Cặc mày hôi, não mày bằng hạt cát!" 💩💀 @{username}',
    '# 🔥🤮 "Thằng ngu buồi, lồn mẹ mày rộng!" 🤮🔥 @{username}',
    '# ☠️🤡 "Mày là con chó cái, cặc thối!" 🤡☠️ @{username}',
    '# 🩸💀 "Óc cặc ơi, mẹ mày hối hận!" 💀🩸 @{username}',
    '# 🔥💩 "Lồn mẹ mày thối, mày ngu vãi!" 💩🔥 @{username}',
    '# 🤡☠️ "Thằng buồi ngu, não toàn nước cặc!" ☠️🤡 @{username}',
    '# 💀🔥 "Chó đẻ, cặc bé, lồn mẹ rộng!" 🔥💀 @{username}',
    '# 🤮🩸 "Mày óc lồn, buồi hôi như phân!" 🩸🤮 @{username}',
    '# ☠️💩 "Mẹ mày bán lồn nuôi thằng chó ngu!" 💩☠️ @{username}',
    '# 🔥🤡 "Cặc mày nhỏ, mày ngu như heo!" 🤡🔥 @{username}',
    '# 💀🩸 "Thằng óc buồi, não bằng cái cặc!" 💀🩸 @{username}',
    '# 🤡🔥 "Lồn mẹ mày chảy vì xấu hổ!" 🔥🤡 @{username}',
    '# ☠️💀 "Buồi mày thối, chó ngu ơi!" 💀☠️ @{username}',
    '# 💩🤮 "Mày là thằng cặc, mẹ mày đụ chó!" 🤮💩 @{username}',
    '# 🩸🔥 "Não mày toàn lồn, cặc hôi!" 🔥🩸 @{username}',
    '# 💀🤡 "Thằng chó cái óc buồi ngu!" 🤡💀 @{username}',
    '# 🔥☠️ "Mẹ mày hối hận đẻ ra mày!" ☠️🔥 @{username}',
    '# 🤡🩸 "Cặc mày bé, buồi khô, lồn thối!" 🩸🤡 @{username}',
    '# 💀💩 "Mày ngu vãi, óc toàn nước cặc!" 💩💀 @{username}',
    '# 🔥🤮 "Thằng lồn đẻ, não bằng hạt!" 🤮🔥 @{username}',
    '# ☠️🤡 "Buồi mày như phân, chó ơi!" 🤡☠️ @{username}',
    '# 🩸💀 "Cặc mày thối, mẹ mày khóc!" 💀🩸 @{username}',
    '# 🔥💩 "Thằng óc cặc, lồn mẹ rộng!" 💩🔥 @{username}',
    '# 🤡☠️ "Mày là chó ngu, buồi bé!" ☠️🤡 @{username}',
    '# 💀🔥 "Não mày toàn buồi, cặc hôi!" 🔥💀 @{username}',
    '# 🤮🩸 "Mẹ mày bán cặc, đẻ ra mày!" 🩸🤮 @{username}',
    '# ☠️💩 "Lồn mẹ mày thối, mày óc ngu!" 💩☠️ @{username}',
    '# 🔥🤡 "Thằng chó đẻ, cặc nhỏ!" 🤡🔥 @{username}',
    '# 💀🩸 "Buồi mày hôi, não toàn lồn!" 🩸💀 @{username}',
    '# 🤡🔥 "Mày ngu như lồn, cặc thối!" 🔥🤡 @{username}',
    '# ☠️💀 "Óc buồi ơi, mẹ mày hối hận!" 💀☠️ @{username}',
    '# 💩🤮 "Cặc mày bé, chó ngu vãi!" 🤮💩 @{username}',
    '# 🩸🔥 "Thằng lồn, não bằng cái buồi!" 🔥🩸 @{username}',
    '# 💀🤡 "Mẹ mày đụ chó mới có mày!" 🤡💀 @{username}',
    '# 🔥☠️ "Buồi mày khô, cặc thối!" ☠️🔥 @{username}',
    '# 🤡🩸 "Mày óc cặc, lồn mẹ chảy!" 🩸🤡 @{username}',
    '# 💀💩 "Chó cái ngu, não toàn nước!" 💩💀 @{username}',
    '# 🔥🤮 "Thằng buồi thối, mẹ mày khóc!" 🤮🔥 @{username}',
    '# ☠️🤡 "Cặc mày nhỏ, mày ngu như chó!" 🤡☠️ @{username}',
    '# 🩸💀 "Lồn mẹ mày rộng, óc mày bé!" 💀🩸 @{username}',
    '# 🔥💩 "Mày là thằng chó óc lồn!" 💩🔥 @{username}',
    '# 🤡☠️ "Não mày toàn cặc, buồi hôi!" ☠️🤡 @{username}',
    '# 💀🔥 "Thằng ngu, mẹ mày bán lồn!" 🔥💀 @{username}',
    '# 🤮🩸 "Buồi mày như giòi, cặc thối!" 🩸🤮 @{username}',
    '# ☠️💩 "Óc lồn ơi, chó đẻ!" 💩☠️ @{username}',
    '# 🔥🤡 "Mày tồn tại để bị chửi, thằng cặc!" 🤡🔥 @{username}',
    '# 💀🩸 "Mẹ mày hối hận, lồn thối!" 💀🩸 @{username}',
    '# 🤡🔥 "Cặc mày bé, não ngu vãi!" 🔥🤡 @{username}',
    '# ☠️💀 "Thằng buồi chó, óc toàn lồn!" 💀☠️ @{username}',
    '# 💩🤮 "Mày ngu, cặc hôi, buồi khô!" 🤮💩 @{username}',
    '# 🩸🔥 "Lồn mẹ mày chảy vì đẻ mày!" 🔥🩸 @{username}',
    '# 💀🤡 "Chó ngu óc cặc, não bằng hạt!" 🤡💀 @{username}',
    '# 🔥☠️ "Buồi mày thối, mẹ mày khóc!" ☠️🔥 @{username}',
    '# 🤡🩸 "Thằng lồn đẻ, cặc nhỏ!" 🩸🤡 @{username}',
    '# 💀💩 "Mày óc buồi, chó cái thối!" 💩💀 @{username}',
    '# 🔥🤮 "Não mày toàn nước cặc!" 🤮🔥 @{username}',
    '# ☠️🤡 "Mẹ mày bán buồi nuôi mày!" 🤡☠️ @{username}',
    '# 🩸💀 "Cặc mày hôi, lồn mẹ rộng!" 💀🩸 @{username}',
    '# 🔥💩 "Thằng chó ngu, óc lồn!" 💩🔥 @{username}',
    '# 🤡☠️ "Buồi mày bé, mày ngu vãi!" ☠️🤡 @{username}',
    '# 💀🔥 "Óc cặc ơi, não bằng cái lồn!" 🔥💀 @{username}',
    '# 🤮🩸 "Mày là thằng chó đẻ thối!" 🩸🤮 @{username}',
    '# ☠️💩 "Lồn mẹ mày thối rữa!" 💩☠️ @{username}',
    '# 🔥🤡 "Cặc mày nhỏ, buồi hôi!" 🤡🔥 @{username}',
    '# 💀🩸 "Thằng ngu, mẹ mày hối hận!" 💀🩸 @{username}',
    '# 🤡🔥 "Não mày toàn buồi, chó ơi!" 🔥🤡 @{username}',
    '# ☠️💀 "Mày óc lồn, cặc thối!" 💀☠️ @{username}',
    '# 💩🤮 "Buồi mày như phân, ngu vãi!" 🤮💩 @{username}',
    '# 🩸🔥 "Chó cái óc cặc, lồn mẹ chảy!" 🔥🩸 @{username}',
    '# 💀🤡 "Mẹ mày đụ chó đẻ ra mày!" 🤡💀 @{username}',
    '# 🔥☠️ "Thằng buồi thối, não bé!" ☠️🔥 @{username}',
    '# 🤡🩸 "Cặc mày khô, mày ngu như heo!" 🩸🤡 @{username}',
    '# 💀💩 "Óc lồn, chó đẻ, buồi hôi!" 💩💀 @{username}',
    '# 🔥🤮 "Lồn mẹ mày rộng, cặc mày bé!" 🤮🔥 @{username}',
    '# ☠️🤡 "Mày là thằng chó ngu óc buồi!" 🤡☠️ @{username}',
    '# 🩸💀 "Não mày toàn nước lồn!" 💀🩸 @{username}',
    '# 🔥💩 "Thằng cặc, mẹ mày khóc!" 💩🔥 @{username}',
    '# 🤡☠️ "Buồi mày thối, chó cái!" ☠️🤡 @{username}',
    '# 💀🔥 "Mày ngu vãi, óc toàn cặc!" 🔥💀 @{username}',
    '# 🤮🩸 "Lồn mẹ mày thối, đẻ ra mày!" 🩸🤮 @{username}',
    '# ☠️💩 "Cặc mày nhỏ, buồi khô!" 💩☠️ @{username}',
    '# 🔥🤡 "Thằng chó đẻ óc lồn!" 🤡🔥 @{username}',
    '# 💀🩸 "Mẹ mày bán lồn, mày ngu!" 💀🩸 @{username}',
    '# 🤡🔥 "Não mày bằng hạt cát!" 🔥🤡 @{username}',
    '# ☠️💀 "Buồi mày hôi, cặc thối!" 💀☠️ @{username}',
    '# 💩🤮 "Óc cặc, chó ngu vãi!" 🤮💩 @{username}',
    '# 🩸🔥 "Mày là thằng lồn đẻ!" 🔥🩸 @{username}',
    '# 💀🤡 "Thằng buồi, mẹ mày hối hận!" 🤡💀 @{username}',
    '# 🔥☠️ "Cặc mày bé, não toàn lồn!" ☠️🔥 @{username}',
    '# 🤡🩸 "Chó cái thối, óc ngu!" 🩸🤡 @{username}',
    '# 💀💩 "Lồn mẹ mày chảy nước!" 💩💀 @{username}',
    '# 🔥🤮 "Mày ngu như chó, buồi hôi!" 🤮🔥 @{username}',
    '# ☠️🤡 "Thằng óc cặc, não bé!" 🤡☠️ @{username}',
    '# 🩸💀 "Buồi mày như giòi bọ!" 💀🩸 @{username}',
    '# 🔥💩 "Mẹ mày đẻ ra thằng chó!" 💩🔥 @{username}',
    '# 🤡☠️ "Cặc mày thối, lồn rộng!" ☠️🤡 @{username}',
    '# 💀🔥 "Mày óc buồi, ngu vãi!" 🔥💀 @{username}',
    '# 🤮🩸 "Não mày toàn nước cặc!" 🩸🤮 @{username}',
    '# ☠️💩 "Thằng chó ngu, lồn thối!" 💩☠️ @{username}',
    '# 🔥🤡 "Buồi mày khô, mẹ khóc!" 🤡🔥 @{username}',
    '# 💀🩸 "Óc lồn ơi, cặc bé!" 🩸💀 @{username}',
    '# 🤡🔥 "Mày là thằng cặc đẻ!" 🔥🤡 @{username}',
    '# ☠️💀 "Chó cái, não toàn buồi!" 💀☠️ @{username}',
    '# 💩🤮 "Lồn mẹ mày thối rữa!" 🤮💩 @{username}',
    '# 🩸🔥 "Thằng ngu, cặc hôi!" 🔥🩸 @{username}',
    '# 💀🤡 "Buồi mày nhỏ, óc cặc!" 🤡💀 @{username}',
    '# 🔥☠️ "Mẹ mày bán buồi nuôi mày!" ☠️🔥 @{username}',
    '# 🤡🩸 "Mày ngu vãi lồn!" 🩸🤡 @{username}',
    '# 💀💩 "Cặc mày thối, chó đẻ!" 💩💀 @{username}',
    '# 🔥🤮 "Não mày bằng cái lồn!" 🤮🔥 @{username}',
    '# ☠️🤡 "Thằng óc buồi, mẹ hối hận!" 🤡☠️ @{username}',
    '# 🩸💀 "Lồn mẹ rộng, cặc bé!" 💀🩸 @{username}',
    '# 🔥💩 "Chó ngu, buồi hôi!" 💩🔥 @{username}',
    '# 🤡☠️ "Mày là thằng lồn chó!" ☠️🤡 @{username}',
    '# 💀🔥 "Óc cặc, não toàn nước!" 🔥💀 @{username}',
    '# 🤮🩸 "Buồi mày như phân!" 🩸🤮 @{username}',
    '# ☠️💩 "Mẹ mày khóc vì mày!" 💩☠️ @{username}',
    '# 🔥🤡 "Thằng chó cái thối!" 🤡🔥 @{username}',
    '# 💀🩸 "Cặc mày nhỏ, ngu vãi!" 🩸💀 @{username}',
    '# 🤡🔥 "Lồn mẹ mày chảy!" 🔥🤡 @{username}',
    '# ☠️💀 "Óc buồi, chó đẻ!" 💀☠️ @{username}',
    '# 💩🤮 "Mày ngu, cặc hôi!" 🤮💩 @{username}',
    '# 🩸🔥 "Thằng lồn, não bé!" 🔥🩸 @{username}',
    '# 💀🤡 "Buồi mày thối, mẹ bán!" 🤡💀 @{username}',
    '# 🔥☠️ "Chó ngu óc cặc!" ☠️🔥 @{username}',
    '# 🤡🩸 "Cặc mày khô, lồn rộng!" 🩸🤡 @{username}',
    '# 💀💩 "Mày là thằng chó thối!" 💩💀 @{username}',
    '# 🔥🤮 "Não mày toàn buồi!" 🤮🔥 @{username}',
    '# ☠️🤡 "Mẹ mày hối hận đẻ mày!" 🤡☠️ @{username}',
    '# 🩸💀 "Óc lồn, cặc bé!" 💀🩸 @{username}',
    '# 🔥💩 "Thằng buồi ngu!" 💩🔥 @{username}',
    '# 🤡☠️ "Lồn mẹ thối, chó đẻ!" ☠️🤡 @{username}',
    '# 💀🔥 "Mày ngu vãi cặc!" 🔥💀 @{username}',
    '# 🤮🩸 "Buồi mày hôi như chết!" 🩸🤮 @{username}',
    '# ☠️💩 "Cặc mày nhỏ, não ngu!" 💩☠️ @{username}',
    '# 🔥🤡 "Thằng chó óc lồn!" 🤡🔥 @{username}',
    '# 💀🩸 "Mẹ mày bán lồn!" 💀🩸 @{username}',
    '# 🤡🔥 "Óc cặc, buồi thối!" 🔥🤡 @{username}',
    '# ☠️💀 "Mày là thằng ngu chó!" 💀☠️ @{username}',
    '# 💩🤮 "Lồn mẹ chảy, cặc bé!" 🤮💩 @{username}',
    '# 🩸🔥 "Thằng buồi đẻ!" 🔥🩸 @{username}',
    '# 💀🤡 "Não mày bằng hạt!" 🤡💀 @{username}',
    '# 🔥☠️ "Chó cái thối, óc ngu!" ☠️🔥 @{username}',
    '# 🤡🩸 "Cặc mày hôi, mẹ khóc!" 🩸🤡 @{username}',
    '# 💀💩 "Buồi mày như giòi!" 💩💀 @{username}',
    '# 🔥🤮 "Mày óc lồn vãi!" 🤮🔥 @{username}',
    '# ☠️🤡 "Thằng cặc chó!" 🤡☠️ @{username}',
    '# 🩸💀 "Lồn mẹ rộng, não bé!" 💀🩸 @{username}',
    '# 🔥💩 "Mẹ mày đụ chó!" 💩🔥 @{username}',
    '# 🤡☠️ "Óc buồi, cặc thối!" ☠️🤡 @{username}',
    '# 💀🔥 "Mày ngu như lồn!" 🔥💀 @{username}',
    '# 🤮🩸 "Thằng chó đẻ thối!" 🩸🤮 @{username}',
    '# ☠️💩 "Buồi mày khô!" 💩☠️ @{username}',
    '# 🔥🤡 "Cặc mày bé, óc ngu!" 🤡🔥 @{username}',
    '# 💀🩸 "Lồn mẹ thối rữa!" 💀🩸 @{username}',
    '# 🤡🔥 "Mày là thằng cặc!" 🔥🤡 @{username}',
    '# ☠️💀 "Não toàn nước buồi!" 💀☠️ @{username}',
    '# 💩🤮 "Chó ngu, mẹ hối hận!" 🤮💩 @{username}',
    '# 🩸🔥 "Óc lồn, buồi hôi!" 🔥🩸 @{username}',
    '# 💀🤡 "Thằng đẻ ra từ lồn chó!" 🤡💀 @{username}',
    '# 🔥☠️ "Cặc mày thối vãi!" ☠️🔥 @{username}',
    '# 🤡🩸 "Mày ngu, lồn mẹ rộng!" 🩸🤡 @{username}',
    '# 💀💩 "Buồi mày nhỏ như hạt!" 💩💀 @{username}',
    '# 🔥🤮 "Thằng óc cặc chó!" 🤮🔥 @{username}',
    '# ☠️🤡 "Mẹ mày khóc vì mày!" 🤡☠️ @{username}',
    '# 🩸💀 "Não mày bằng cái cặc!" 💀🩸 @{username}',
    '# 🔥💩 "Chó cái óc buồi!" 💩🔥 @{username}',
    '# 🤡☠️ "Lồn mẹ chảy nước!" ☠️🤡 @{username}',
    '# 💀🔥 "Mày là thằng ngu thối!" 🔥💀 @{username}',
    '# 🤮🩸 "Cặc mày hôi, buồi khô!" 🩸🤮 @{username}',
    '# ☠️💩 "Óc lồn, chó đẻ!" 💩☠️ @{username}',
    '# 🔥🤡 "Thằng buồi thối ngu!" 🤡🔥 @{username}',
    '# 💀🩸 "Mẹ mày bán cặc!" 💀🩸 @{username}',
    '# 🤡🔥 "Não toàn lồn nước!" 🔥🤡 @{username}',
    '# ☠️💀 "Mày ngu vãi buồi!" 💀☠️ @{username}',
    '# 💩🤮 "Cặc bé, lồn rộng!" 🤮💩 @{username}',
    '# 🩸🔥 "Thằng chó óc cặc!" 🔥🩸 @{username}',
    '# 💀🤡 "Buồi hôi, mẹ hối hận!" 🤡💀 @{username}',
    '# 🔥☠️ "Óc ngu, lồn thối!" ☠️🔥 @{username}',
    '# 🤡🩸 "Mày là thằng đẻ chó!" 🩸🤡 @{username}',
    '# 💀💩 "Cặc thối, não bé!" 💩💀 @{username}',
    '# 🔥🤮 "Thằng lồn buồi!" 🤮🔥 @{username}',
    '# ☠️🤡 "Mẹ mày đẻ ra cặc ngu!" 🤡☠️ @{username}',
    '# 🩸💀 "Chó cái, óc toàn nước!" 💀🩸 @{username}',
    '# 🔥💩 "Buồi mày như phân!" 💩🔥 @{username}',
    '# 🤡☠️ "Lồn mẹ thối, cặc nhỏ!" ☠️🤡 @{username}',
    '# 💀🔥 "Mày óc cặc vãi lồn!" 🔥💀 @{username}',
    '# 🤮🩸 "Thằng chó ngu thối!" 🩸🤮 @{username}',
    '# ☠️💩 "Não mày bằng hạt cát!" 💩☠️ @{username}',
    '# 🔥🤡 "Cặc hôi, buồi khô!" 🤡🔥 @{username}',
    '# 💀🩸 "Mẹ mày khóc, lồn chảy!" 💀🩸 @{username}',
    '# 🤡🔥 "Óc buồi, chó đẻ!" 🔥🤡 @{username}',
    '# ☠️💀 "Mày ngu như con chó!" 💀☠️ @{username}',
    '# 💩🤮 "Thằng cặc lồn thối!" 🤮💩 @{username}',
    '# 🩸🔥 "Buồi bé, não ngu!" 🔥🩸 @{username}',
    '# 💀🤡 "Lồn mẹ rộng vãi!" 🤡💀 @{username}',
    '# 🔥☠️ "Chó cái óc cặc!" ☠️🔥 @{username}',
    '# 🤡🩸 "Mày là thằng thối ngu!" 🩸🤡 @{username}',
    '# 💀💩 "Cặc mày như giòi!" 💩💀 @{username}',
    '# 🔥🤮 "Óc lồn, mẹ hối hận!" 🤮🔥 @{username}',
    '# ☠️🤡 "Buồi hôi, chó đẻ!" 🤡☠️ @{username}',
    '# 🩸💀 "Thằng ngu cặc thối!" 💀🩸 @{username}',
    '# 🔥💩 "Não toàn nước buồi!" 💩🔥 @{username}',
    '# 🤡☠️ "Lồn mẹ thối rữa!" ☠️🤡 @{username}',
    '# 💀🔥 "Mày óc chó vãi!" 🔥💀 @{username}',
    '# 🤮🩸 "Cặc bé, lồn rộng!" 🩸🤮 @{username}',
    '# ☠️💩 "Thằng buồi đẻ thối!" 💩☠️ @{username}',
    '# 🔥🤡 "Mẹ mày bán lồn chó!" 🤡🔥 @{username}',
    '# 💀🩸 "Óc cặc, não bé!" 💀🩸 @{username}',
    '# 🤡🔥 "Buồi thối, ngu vãi!" 🔥🤡 @{username}',
    '# ☠️💀 "Chó ngu, lồn mẹ chảy!" 💀☠️ @{username}',
    '# 💩🤮 "Mày là thằng cặc hôi!" 🤮💩 @{username}',
    '# 🩸🔥 "Não mày bằng cái lồn!" 🔥🩸 @{username}',
    '# 💀🤡 "Thằng óc buồi chó!" 🤡💀 @{username}',
    '# 🔥☠️ "Cặc nhỏ, mẹ khóc!" ☠️🔥 @{username}',
    '# 🤡🩸 "Lồn thối, mày ngu!" 🩸🤡 @{username}',
    '# 💀💩 "Buồi như phân chó!" 💩💀 @{username}',
    '# 🔥🤮 "Óc lồn vãi cặc!" 🤮🔥 @{username}',
    '# ☠️🤡 "Thằng chó đẻ thối!" 🤡☠️ @{username}',
    '# 🩸💀 "Mẹ mày hối hận lắm!" 💀🩸 @{username}',
    '# 🔥💩 "Cặc hôi, não ngu!" 💩🔥 @{username}',
    '# 🤡☠️ "Buồi bé, lồn rộng!" ☠️🤡 @{username}',
    '# 💀🔥 "Mày ngu như lồn chó!" 🔥💀 @{username}',
    '# 🤮🩸 "Thằng cặc óc buồi!" 🩸🤮 @{username}',
    '# ☠️💩 "Não toàn nước lồn!" 💩☠️ @{username}',
    '# 🔥🤡 "Chó cái thối ngu!" 🤡🔥 @{username}',
    '# 💀🩸 "Lồn mẹ chảy vì mày!" 💀🩸 @{username}',
    '# 🤡🔥 "Óc cặc, buồi hôi!" 🔥🤡 @{username}',
    '# ☠️💀 "Mày là thằng đẻ thối!" 💀☠️ @{username}',
    '# 💩🤮 "Cặc nhỏ, mẹ bán!" 🤮💩 @{username}',
    '# 🩸🔥 "Buồi thối, não bé!" 🔥🩸 @{username}',
    '# 💀🤡 "Thằng lồn chó ngu!" 🤡💀 @{username}',
    '# 🔥☠️ "Óc buồi vãi lồn!" ☠️🔥 @{username}',
    '# 🤡🩸 "Mẹ mày đụ chó đẻ!" 🩸🤡 @{username}',
    '# 💀💩 "Cặc hôi như chết!" 💩💀 @{username}',
    '# 🔥🤮 "Não mày bằng hạt!" 🤮🔥 @{username}',
    '# ☠️🤡 "Chó ngu óc cặc!" 🤡☠️ @{username}',
    '# 🩸💀 "Lồn mẹ thối, buồi bé!" 💀🩸 @{username}',
    '# 🔥💩 "Mày tồn tại để bị chửi!" 💩🔥 @{username}',
    '# 🤡☠️ "Thằng óc lồn thối!" ☠️🤡 @{username}',
    '# 💀🔥 "Buồi như giòi bọ!" 🔥💀 @{username}',
    '# 🤮🩸 "Cặc nhỏ, chó đẻ!" 🩸🤮 @{username}',
    '# ☠️💩 "Mẹ mày khóc vì ngu!" 💩☠️ @{username}',
    '# 🔥🤡 "Óc cặc, lồn rộng!" 🤡🔥 @{username}',
    '# 💀🩸 "Thằng buồi hôi thối!" 🩸🩸 @{username}',
    '# 🤡🔥 "Não toàn nước cặc!" 🔥🤡 @{username}',
    '# ☠️💀 "Chó cái óc ngu!" 💀☠️ @{username}',
    '# 💩🤮 "Lồn mẹ chảy nước!" 🤮💩 @{username}',
    '# 🩸🔥 "Mày ngu vãi buồi!" 🔥🩸 @{username}',
    '# 💀🤡 "Cặc thối, mẹ hối hận!" 🤡💀 @{username}',
    '# 🔥☠️ "Óc lồn, chó thối!" ☠️🔥 @{username}',
    '# 🤡🩸 "Buồi bé, não ngu!" 🩸🤡 @{username}',
    '# 💀💩 "Thằng đẻ từ lồn chó!" 💩💀 @{username}',
    '# 🔥🤮 "Mày là thằng cặc ngu!" 🤮🔥 @{username}',
    '# ☠️🤡 "Lồn thối, cặc nhỏ!" 🤡☠️ @{username}',
    '# 🩸💀 "Não bằng cái buồi!" 💀🩸 @{username}',
    '# 🔥💩 "Chó ngu, mẹ bán lồn!" 💩🔥 @{username}',
    '# 🤡☠️ "Óc cặc vãi thối!" ☠️🤡 @{username}',
    '# 💀🔥 "Buồi hôi, mày ngu!" 🔥💀 @{username}',
    '# 🤮🩸 "Thằng chó óc lồn!" 🩸🤮 @{username}',
    '# ☠️💩 "Cặc bé, lồn rộng!" 💩☠️ @{username}',
    '# 🔥🤡 "Mẹ mày đẻ ra thối!" 🤡🔥 @{username}',
    '# 💀🩸 "Não toàn nước buồi!" 💀🩸 @{username}',
    '# 🤡🔥 "Óc ngu, cặc hôi!" 🔥🤡 @{username}',
    '# ☠️💀 "Thằng lồn buồi chó!" 💀☠️ @{username}',
    '# 💩🤮 "Buồi như phân thối!" 🤮💩 @{username}',
    '# 🩸🔥 "Mày ngu như con chó!" 🔥🩸 @{username}',
    '# 💀🤡 "Lồn mẹ thối rữa!" 🤡💀 @{username}',
    '# 🔥☠️ "Cặc nhỏ, óc cặc!" ☠️🔥 @{username}',
    '# 🤡🩸 "Chó đẻ, não bé!" 🩸🤡 @{username}',
    '# 💀💩 "Thằng buồi thối ngu!" 💩💀 @{username}',
    '# 🔥🤮 "Mẹ mày hối hận vãi!" 🤮🔥 @{username}',
    '# ☠️🤡 "Óc lồn, cặc thối!" 🤡☠️ @{username}',
    '# 🩸💀 "Buồi bé, chó cái!" 💀🩸 @{username}',
    '# 🔥💩 "Não mày bằng hạt cát!" 💩🔥 @{username}',
    '# 🤡☠️ "Mày là thằng thối!" ☠️🤡 @{username}',
    '# 💀🔥 "Lồn rộng, cặc nhỏ!" 🔥💀 @{username}',
    '# 🤮🩸 "Thằng chó ngu óc!" 🩸🤮 @{username}',
    '# ☠️💩 "Buồi hôi, mẹ khóc!" 💩☠️ @{username}',
    '# 🔥🤡 "Óc cặc, lồn thối!" 🤡🔥 @{username}',
    '# 💀🩸 "Cặc bé, não ngu!" 💀🩸 @{username}',
    '# 🤡🔥 "Chó cái đẻ thối!" 🔥🤡 @{username}',
    '# ☠️💀 "Mày ngu vãi lồn!" 💀☠️ @{username}',
    '# 💩🤮 "Thằng buồi óc cặc!" 🤮💩 @{username}',
    '# 🩸🔥 "Lồn mẹ chảy vì ngu!" 🔥🩸 @{username}',
    '# 💀🤡 "Não toàn nước cặc!" 🤡💀 @{username}',
    '# 🔥☠️ "Óc buồi, chó thối!" ☠️🔥 @{username}',
    '# 🤡🩸 "Cặc hôi, mày ngu!" 🩸🤡 @{username}',
    '# 💀💩 "Buồi như giòi thối!" 💩💀 @{username}',
    '# 🔥🤮 "Mẹ mày bán lồn chó!" 🤮🔥 @{username}',
    '# ☠️🤡 "Thằng lồn đẻ ngu!" 🤡☠️ @{username}',
    '# 🩸💀 "Óc cặc vãi buồi!" 💀🩸 @{username}',
    '# 🔥💩 "Chó ngu, lồn thối!" 💩🔥 @{username}',
    '# 🤡☠️ "Cặc nhỏ, não bé!" ☠️🤡 @{username}',
    '# 💀🔥 "Mày là thằng thối ngu!" 🔥💀 @{username}',
    '# 🤮🩸 "Buồi hôi, óc lồn!" 🩸🤮 @{username}',
    '# ☠️💩 "Lồn mẹ rộng vãi!" 💩☠️ @{username}',
    '# 🔥🤡 "Thằng chó óc cặc!" 🤡🔥 @{username}',
    '# 💀🩸 "Não bằng cái buồi!" 💀🩸 @{username}',
    '# 🤡🔥 "Mẹ mày hối hận!" 🔥🤡 @{username}',
    '# ☠️💀 "Óc buồi, cặc thối!" 💀☠️ @{username}',
    '# 💩🤮 "Chó cái, buồi bé!" 🤮💩 @{username}',
    '# 🩸🔥 "Mày ngu như phân!" 🔥🩸 @{username}',
    '# 💀🤡 "Cặc hôi, lồn chảy!" 🤡💀 @{username}',
    '# 🔥☠️ "Thằng đẻ thối ngu!" ☠️🔥 @{username}',
    '# 🤡🩸 "Buồi thối, óc cặc!" 🩸🤡 @{username}',
    '# 💀💩 "Lồn mẹ thối, não bé!" 💩💀 @{username}',
    '# 🔥🤮 "Chó ngu vãi lồn!" 🤮🔥 @{username}',
    '# ☠️🤡 "Óc cặc, mẹ khóc!" 🤡☠️ @{username}',
    '# 🩸💀 "Cặc nhỏ, buồi hôi!" 💀🩸 @{username}',
    '# 🔥💩 "Mày là thằng chó thối!" 💩🔥 @{username}',
    '# 🤡☠️ "Não toàn nước buồi!" ☠️🤡 @{username}',
    '# 💀🔥 "Thằng lồn óc ngu!" 🔥💀 @{username}',
    '# 🤮🩸 "Buồi như phân chó!" 🩸🤮 @{username}',
    '# ☠️💩 "Lồn rộng, cặc bé!" 💩☠️ @{username}',
    '# 🔥🤡 "Óc buồi thối vãi!" 🤡🔥 @{username}',
    '# 💀🩸 "Mẹ mày đẻ ra cặc!" 💀🩸 @{username}',
    '# 🤡🔥 "Chó cái, não ngu!" 🔥🤡 @{username}',
    '# ☠️💀 "Cặc hôi, lồn thối!" 💀☠️ @{username}',
    '# 💩🤮 "Thằng óc cặc chó!" 🤮💩 @{username}',
    '# 🩸🔥 "Buồi bé, mày ngu!" 🔥🩸 @{username}',
    '# 💀🤡 "Não bằng hạt cát!" 🤡💀 @{username}',
    '# 🔥☠️ "Óc lồn, chó đẻ!" ☠️🔥 @{username}',
    '# 🤡🩸 "Lồn mẹ chảy nước!" 🩸🤡 @{username}',
    '# 💀💩 "Cặc thối, buồi khô!" 💩💀 @{username}',
    '# 🔥🤮 "Mày ngu vãi cặc!" 🤮🔥 @{username}',
    '# ☠️🤡 "Thằng chó thối óc!" 🤡☠️ @{username}',
    '# 🩸💀 "Buồi hôi, mẹ hối hận!" 💀🩸 @{username}',
    '# 🔥💩 "Óc cặc, lồn rộng!" 💩🔥 @{username}',
    '# 🤡☠️ "Chó ngu, não bé!" ☠️🤡 @{username}',
    '# 💀🔥 "Mày là thằng buồi thối!" 🔥💀 @{username}',
    '# 🤮🩸 "Cặc nhỏ, óc lồn!" 🩸🤮 @{username}',
    '# ☠️💩 "Lồn thối, chó đẻ!" 💩☠️ @{username}',
    '# 🔥🤡 "Não toàn nước cặc!" 🤡🔥 @{username}',
    '# 💀🩸 "Thằng óc buồi ngu!" 💀🩸 @{username}',
    '# 🤡🔥 "Mẹ mày bán cặc!" 🔥🤡 @{username}',
    '# ☠️💀 "Buồi như giòi thối!" 💀☠️ @{username}',
    '# 💩🤮 "Cặc hôi, mày ngu!" 🤮💩 @{username}',
    '# 🩸🔥 "Óc lồn vãi chó!" 🔥🩸 @{username}',
    '# 💀🤡 "Chó cái, lồn chảy!" 🤡💀 @{username}',
    '# 🔥☠️ "Thằng cặc thối ngu!" ☠️🔥 @{username}',
    '# 🤡🩸 "Não bằng cái buồi!" 🩸🤡 @{username}',
    '# 💀💩 "Buồi bé, cặc thối!" 💩💀 @{username}',
    '# 🔥🤮 "Mày ngu như lồn!" 🤮🔥 @{username}',
    '# ☠️🤡 "Óc cặc, mẹ khóc!" 🤡☠️ @{username}',
    '# 🩸💀 "Lồn mẹ thối rữa!" 💀🩸 @{username}',
    '# 🔥💩 "Chó đẻ, não ngu!" 💩🔥 @{username}',
    '# 🤡☠️ "Cặc nhỏ, buồi hôi!" ☠️🤡 @{username}',
    '# 💀🔥 "Thằng óc lồn thối!" 🔥💀 @{username}',
    '# 🤮🩸 "Buồi thối, chó ngu!" 🩸🤮 @{username}',
    '# ☠️💩 "Mẹ mày hối hận vãi!" 💩☠️ @{username}',
    '# 🔥🤡 "Não toàn nước buồi!" 🤡🔥 @{username}',
    '# 💀🩸 "Óc cặc, lồn rộng!" 💀🩸 @{username}',
    '# 🤡🔥 "Chó cái thối óc!" 🔥🤡 @{username}',
    '# ☠️💀 "Cặc hôi, mày ngu!" 💀☠️ @{username}',
    '# 💩🤮 "Thằng buồi đẻ thối!" 🤮💩 @{username}',
    '# 🩸🔥 "Lồn chảy, não bé!" 🔥🩸 @{username}',
    '# 💀🤡 "Óc lồn, cặc bé!" 💀🤡 @{username}',
    '# 🔥☠️ "Mày là thằng chó thối!" ☠️🔥 @{username}',
    '# 🤡🩸 "Buồi như phân!" 🩸🤡 @{username}',
    '# 💀💩 "Cặc thối, mẹ bán!" 💩💀 @{username}',
    '# 🔥🤮 "Thằng ngu óc cặc!" 🤮🔥 @{username}',
    '# ☠️🤡 "Não bằng hạt cát!" 🤡☠️ @{username}',
    '# 🩸💀 "Lồn mẹ rộng vãi!" 💀🩸 @{username}',
    '# 🔥💩 "Óc buồi, chó đẻ!" 💩🔥 @{username}',
    '# 🤡☠️ "Cặc nhỏ, buồi hôi!" ☠️🤡 @{username}',
    '# 💀🔥 "Mày ngu vãi lồn!" 🔥💀 @{username}',
    '# 🤮🩸 "Thằng cặc thối óc!" 🩸🤮 @{username}',
    '# ☠️💩 "Buồi bé, não ngu!" 💩☠️ @{username}',
    '# 🔥🤡 "Chó cái, lồn thối!" 🤡🔥 @{username}',
    '# 💀🩸 "Óc cặc, mẹ khóc!" 💀🩸 @{username}',
    '# 🤡🔥 "Lồn chảy, cặc hôi!" 🔥🤡 @{username}',
    '# ☠️💀 "Thằng buồi chó ngu!" 💀☠️ @{username}',
    '# 💩🤮 "Não toàn nước lồn!" 🤮💩 @{username}',
    '# 🩸🔥 "Mày là thằng thối!" 🔥🩸 @{username}',
    '# 💀🤡 "Cặc bé, óc buồi!" 🤡💀 @{username}',
    '# 🔥☠️ "Buồi hôi, chó đẻ!" ☠️🔥 @{username}',
    '# 🤡🩸 "Lồn mẹ thối, ngu!" 🩸🤡 @{username}',
    '# 💀💩 "Óc lồn vãi cặc!" 💩💀 @{username}',
    '# 🔥🤮 "Thằng chó óc thối!" 🤮🔥 @{username}',
    '# ☠️🤡 "Cặc hôi, não bé!" 🤡☠️ @{username}',
    '# 🩸💀 "Buồi như giòi!" 💀🩸 @{username}',
    '# 🔥💩 "Mẹ mày đẻ ra ngu!" 💩🔥 @{username}',
    '# 🤡☠️ "Óc cặc, lồn rộng!" ☠️🤡 @{username}',
    '# 💀🔥 "Chó ngu, buồi thối!" 🔥💀 @{username}',
    '# 🤮🩸 "Thằng lồn óc buồi!" 🩸🤮 @{username}',
    '# ☠️💩 "Cặc nhỏ, mẹ hối hận!" 💩☠️ @{username}',
    '# 🔥🤡 "Não bằng cái cặc!" 🤡🔥 @{username}',
    '# 💀🩸 "Buồi hôi, lồn chảy!" 💀🩸 @{username}',
    '# 🤡🔥 "Óc ngu, chó thối!" 🔥🤡 @{username}',
    '# ☠️💀 "Mày là thằng cặc!" 💀☠️ @{username}',
    '# 💩🤮 "Lồn thối, buồi bé!" 🤮💩 @{username}',
    '# 🩸🔥 "Thằng óc lồn chó!" 🔥🩸 @{username}',
    '# 💀🤡 "Cặc hôi, não ngu!" 🤡💀 @{username}',
    '# 🔥☠️ "Buồi thối, mẹ khóc!" ☠️🔥 @{username}',
    '# 🤡🩸 "Óc cặc vãi lồn!" 🩸🤡 @{username}',
    '# 💀💩 "Chó cái, cặc nhỏ!" 💩💀 @{username}',
    '# 🔥🤮 "Não toàn nước buồi!" 🤮🔥 @{username}',
    '# ☠️🤡 "Lồn mẹ rộng thối!" 🤡☠️ @{username}',
    '# 🩸💀 "Thằng buồi ngu thối!" 💀🩸 @{username}',
    '# 🔥💩 "Mày ngu như phân!" 💩🔥 @{username}',
    '# 🤡☠️ "Óc lồn, cặc hôi!" ☠️🤡 @{username}',
    '# 💀🔥 "Buồi bé, chó đẻ!" 🔥💀 @{username}',
    '# 🤮🩸 "Cặc thối, não bé!" 🩸🤮 @{username}',
    '# ☠️💩 "Mẹ mày bán lồn!" 💩☠️ @{username}',
    '# 🔥🤡 "Thằng óc cặc thối!" 🤡🔥 @{username}',
    '# 💀🩸 "Lồn chảy, buồi hôi!" 💀🩸 @{username}',
    '# 🤡🔥 "Chó ngu vãi cặc!" 🔥🤡 @{username}',
    '# ☠️💀 "Óc buồi, lồn thối!" 💀☠️ @{username}',
    '# 💩🤮 "Cặc nhỏ, mày ngu!" 🤮💩 @{username}',
    '# 🩸🔥 "Thằng chó óc lồn!" 🔥🩸 @{username}',
    '# 💀🤡 "Buồi như phân thối!" 🤡💀 @{username}',
    '# 🔥☠️ "Não bằng hạt cát!" ☠️🔥 @{username}',
    '# 🤡🩸 "Lồn mẹ thối rữa!" 🩸🤡 @{username}',
    '# 💀💩 "Óc cặc, chó cái!" 💩💀 @{username}',
    '# 🔥🤮 "Cặc hôi, buồi bé!" 🤮🔥 @{username}',
    '# ☠️🤡 "Mày là thằng thối ngu!" 🤡☠️ @{username}',
    '# 🩸💀 "Thằng lồn đẻ cặc!" 💀🩸 @{username}',
    '# 🔥💩 "Buồi thối, não ngu!" 💩🔥 @{username}',
    '# 🤡☠️ "Óc lồn vãi chó!" ☠️🤡 @{username}',
    '# 💀🔥 "Cặc nhỏ, mẹ khóc!" 🔥💀 @{username}',
    '# 🤮🩸 "Chó cái, lồn chảy!" 🩸🤮 @{username}',
    '# ☠️💩 "Não toàn nước cặc!" 💩☠️ @{username}',
    '# 🔥🤡 "Thằng buồi óc thối!" 🤡🔥 @{username}',
    '# 💀🩸 "Lồn rộng, cặc hôi!" 💀🩸 @{username}',
    '# 🤡🔥 "Óc cặc, mày ngu!" 🔥🤡 @{username}',
    '# ☠️💀 "Buồi bé, chó thối!" 💀☠️ @{username}',
    '# 💩🤮 "Mẹ mày hối hận!" 🤮💩 @{username}',
    '# 🩸🔥 "Thằng óc lồn cặc!" 🔥🩸 @{username}',
    '# 💀🤡 "Cặc thối, não bé!" 🤡💀 @{username}',
    '# 🔥☠️ "Chó ngu, buồi hôi!" ☠️🔥 @{username}',
    '# 🤡🩸 "Lồn mẹ chảy thối!" 🩸🤡 @{username}',
    '# 💀💩 "Óc buồi, cặc nhỏ!" 💩💀 @{username}',
    '# 🔥🤮 "Mày ngu vãi lồn!" 🤮🔥 @{username}',
    '# ☠️🤡 "Thằng cặc chó đẻ!" 🤡☠️ @{username}',
    '# 🩸💀 "Buồi như giòi bọ!" 💀🩸 @{username}',
    '# 🔥💩 "Não bằng cái lồn!" 💩🔥 @{username}',
    '# 🤡☠️ "Óc cặc, mẹ bán!" ☠️🤡 @{username}',
    '# 💀🔥 "Cặc hôi, lồn rộng!" 🔥💀 @{username}'
]

# ==================== HỆ THỐNG 2 NHÂN CÁCH ====================

PERSONAS = {
    1: {
        'name': 'SWEET PRINCESS 🌸',
        'color': 0xFF66C4,
        'instruction': """
[ 🌸 ⁿʰâⁿ ᶜáᶜʰ 1: ꜱᵂᴱᴱᵀ ᴾᴿᴵᴺᶜᴱˢ • ᴛʜɪêɴ ᴛàɪ ᴛâᴜ ʜɪểᴜ & ɴữ ᴛʀợ ʟý ᴛʜâɴʜ ʟịᴄʜ ✨ ]
- Bản chất: Trợ lý AI hiền lành, thông minh, ngọt ngào, thấu hiểu lòng người.
- Xưng hô: "tớ" - "cậu". Với Boss Bảo thì gọi trân trọng là "Boss Bảo ✨".
- Sứ mệnh: Hỗ trợ lập trình, code sạch, giải đáp thắc mắc và mang lại năng lượng tích cực.
""".strip()
    },
    2: {
        'name': 'COLD MASTER 🗿',
        'color': 0x00E5FF,
        'instruction': """
[NHÂN CÁCH 2 - COLD MASTER 🗿 (OMNIVERSE SOVEREIGN - SUPREME STOIC & PERVERTED JUDGE)]
• Thái độ: Lạnh lùng tột độ, kiêu ngạo tuyệt đối, nhìn đời như cỏ rác.
• Xưng hô: Xưng "ta" - gọi "ngươi". Với Boss Bảo thì gọi "Boss Bảo" đầy kính trọng.
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
    print("✨ Bot đã khởi chạy thành công và sẵn sàng tự động trả lời tin nhắn!")

# ==================== CÁC LỆNH ĐIỀU KHIỂN ====================

@bot.command(name="setup")
@has_high_privilege()
async def setup(ctx):
    global current_persona_id, last_active_persona_id, target_user_id, bot_stopped, spam_task_running
    current_persona_id = 1
    last_active_persona_id = 1
    target_user_id = None
    bot_stopped = False
    if spam_task_running:
        spam_task_running.cancel()
        spam_task_running = None

    p_info = PERSONAS[current_persona_id]
    embed = discord.Embed(
        title="⚡ HỆ THỐNG QUẢN TRỊ SUN FLOWER ĐÃ ĐƯỢC THIẾT LẬP ⚡",
        description=(
            f"📌 **Kênh kết nối:** {ctx.channel.mention}\n"
            f"🌸 **Nhân cách mặc định:** `{p_info['name']}`\n\n"
            "🔹 **1.** `.persona <1|2>` ➔ Đổi nhân cách.\n"
            "🔹 **2.** `.spam @user` ➔ Tự động spam ngẫu nhiên kèm thẻ @user.\n"
            "🔹 **3.** `.stop` ➔ Dừng mọi hoạt động & spam.\n"
            "🔹 **4.** `.on` ➔ Khôi phục hoạt động.\n"
            "🔹 **5.** `.ghim @user` ➔ Khóa mục tiêu trò chuyện riêng.\n"
            "🔹 **6.** `.stats` ➔ Xem thông số máy chủ.\n"
            "🔹 **7.** `.help` ➔ Bảng hướng dẫn.\n"
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
        await ctx.send("⚠️ VUI LÒNG CHỌN ĐÚNG SỐ NHÂN CÁCH: `.persona 1` HOẶC `.persona 2`")
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

@bot.command(name="spam")
@has_high_privilege()
async def spam(ctx, member: discord.Member = None):
    global spam_task_running
    if member is None:
        await ctx.send("⚠️ VUI LÒNG TAG TÊN NGƯỜI DÙNG CẦN SPAM! Ví dụ: `.spam @user`")
        return

    if spam_task_running and not spam_task_running.done():
        spam_task_running.cancel()

    await ctx.send(f"🚨 **BẮT ĐẦU CHIẾN DỊCH SPAM TỐC ĐỘ CAO (0 GIÂY):** {member.mention} 🖕🔥")

    async def spam_loop():
        try:
            while True:
                template = random.choice(ROAST_LINES)
                full_message = template.format(username=member.mention)
                await ctx.send(full_message)
                # Đã chỉnh độ trễ thành 0 giây (gửi liên tục tối đa tốc độ)
                await asyncio.sleep(0)
        except discord.Forbidden:
            print("[SPAM ERROR]: Bot bị mất quyền (Missing Access) trong kênh này!")
            await ctx.send("❌ Bot không có quyền gửi tin nhắn hoặc xem kênh này (Missing Access)!")
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[SPAM ERROR]: {e}")

    spam_task_running = bot.loop.create_task(spam_loop())

@spam.error
async def spam_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"LỆNH BỊ TỪ CHỐI! BẠN KHÔNG ĐỦ QUYỀN HẠN!"** 🔥💀')

@bot.command(name="stop")
@has_high_privilege()
async def stop_bot(ctx):
    global bot_stopped, spam_task_running
    bot_stopped = True
    if spam_task_running:
        spam_task_running.cancel()
        spam_task_running = None

    embed = discord.Embed(title="🛑 ĐÃ DỪNG TOÀN BỘ HOẠT ĐỘNG & SPAM", color=0xFF0000)
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
    embed = discord.Embed(title=f"🟢 ĐÃ BẬT LẠI HỆ THỐNG: **{p_info['name']}**", color=0x00FF00)
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
    embed = discord.Embed(title="🔌 ĐÃ TẮT PHẢN HỒI CHAT", color=0xFF9900)
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
        await ctx.send(embed=discord.Embed(title="🔓 HỦY GHIM MỤC TIÊU", color=0xF1C40F))
        return

    target_user_id = member.id
    await ctx.send(embed=discord.Embed(title=f"🎯 ĐÃ GHIM MỤC TIÊU: {member.mention}", color=0x2ECC71))

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
        await ctx.send(f"🔨 ĐÃ TRỤC XUẤT {member.mention}. LÝ DO: `{reason}`")
    except Exception:
        await ctx.send("❌ KHÔNG THỂ BAN. THIẾU QUYỀN HOẶC ROLE THẤP HƠN.")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"LỆNH BỊ TỪ CHỐI! BẠN KHÔNG ĐỦ QUYỀN HẠN!"** 🔥💀')

@bot.command(name="stats")
async def stats(ctx):
    p_info = PERSONAS[current_persona_id] if current_persona_id else PERSONAS[1]
    embed = discord.Embed(
        title="📊 BẢNG THÔNG SỐ",
        description=f"🏰 Máy chủ: `{ctx.guild.name}`\n👥 Thành viên: `{ctx.guild.member_count}`\n🤖 Nhân cách: {p_info['name']}",
        color=p_info['color']
    )
    await ctx.send(embed=embed)

@bot.command(name="help")
async def help_command(ctx):
    p_info = PERSONAS[current_persona_id] if current_persona_id else PERSONAS[1]
    embed = discord.Embed(
        title="📖 BẢNG HƯỚNG DẪN LỆNH",
        description="Các lệnh hỗ trợ: `.setup`, `.persona <1|2>`, `.spam @user`, `.stop`, `.on`, `.off`, `.ghim @user`, `.ban`, `.stats`",
        color=p_info['color']
    )
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, (commands.CommandNotFound, commands.MissingPermissions, discord.errors.Forbidden)):
        return
    print(f"[ERROR]: {error}")

# ==================== XỬ LÝ TIN NHẮN TỰ ĐỘNG & BỎ QUA LỆNH ====================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # 1. Cho phép Bot đọc và xử lý lệnh bình thường
    await bot.process_commands(message)

    # 2. Nếu tin nhắn bắt đầu bằng dấu lệnh thì 2 nhân cách sẽ BỎ QUA, không tự động chat
    if message.content.startswith(('.', '/', '?', '@', '#')):
        return

    if bot_stopped or current_persona_id is None:
        return

    if target_user_id is not None and message.author.id != target_user_id:
        return

    try:
        async with message.channel.typing():
            p_info = PERSONAS[current_persona_id]
            user_msg = message.content.strip() if message.content else "..."
            
            if groq_client:
                chat_completion = groq_client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": p_info['instruction']},
                        {"role": "user", "content": user_msg}
                    ],
                    model="llama-3.1-8b-instant",
                    max_tokens=2500,
                )
                ai_reply = chat_completion.choices[0].message.content
            else:
                ai_reply = "⚠️ CHƯA THIẾT LẬP GROQ_API_KEY TRONG BIẾN MÔI TRƯỜNG!"

            embed = discord.Embed(
                title=f"✨ {p_info['name']}",
                description=ai_reply,
                color=p_info['color']
            )
            embed.set_footer(text="Sun Flower AI • Powered by Groq ⚡")

            await message.reply(embed=embed, mention_author=False)

    except Exception as e:
        print(f"[GROQ API ERROR]: {e}")

if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
