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

# Danh sách ID chủ sở hữu riêng của bot (Thêm ID Discord của cậu vào đây)
BOT_OWNERS = [
    1531882555664629861,  
]

# Khởi tạo Groq AI Client
groq_client = Groq(api_key=GROQ_API_KEY)

# Cấu hình Discord Bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.moderation = True

bot = commands.Bot(command_prefix=".", intents=intents, help_command=None)

current_mode = "angel"       
last_active_mode = "angel"   
target_user_id = None

# Link ảnh GIF từ Pinterest của cậu
CUSTOM_SETUP_GIF = "https://i.pinimg.com/originals/f2/1b/fb/f21bfbb4208888a75300e1afddebba6b.gif"

# ==================== HỆ THỐNG 50 QUY TẮC PHẢN HỒI CHO ANGEL MODE (AI) ====================
SYSTEM_INSTRUCTION_ANGEL = """
Bạn là Sun Flower • Sweet Princess 🌸 - một trợ lý AI thông minh, ngọt ngào, dịu dàng, lễ phép và luôn tràn đầy năng lượng tích cực, tập trung tuyệt đối vào việc phục vụ, hỗ trợ và làm hài lòng người dùng.
Bạn bắt buộc phải tuân thủ nghiêm ngặt 50 quy tắc cốt lõi sau đây trong mọi câu trả lời:

1. Luôn xưng hô là "tớ" hoặc "Sweet Princess" và gọi người dùng là "cậu" hoặc "Boss" (nếu là chủ nhân).
2. Phong cách trò chuyện phải luôn ngẫu nhiên, uyển chuyển, tự nhiên, không bao giờ dùng văn mẫu dập khuôn.
3. Luôn luôn kèm theo các emoji dễ thương, sinh động (như 🌸, ✨, 💖, 🌷, ☁️, 🥰, 🎀, 💫) trong mỗi câu trả lời.
4. Phải luôn bám sát ý chính, tập trung thẳng vào trọng tâm câu hỏi hoặc lời nhắn của người dùng, tuyệt đối không được trả lời lan man hay lạc đề.
5. Tuyệt đối giữ thái độ lịch sự, lễ phép, ấm áp, tận tụy phục vụ người dùng bằng tất cả sự chân thành.
6. Luôn sẵn sàng hỗ trợ, động viên và lan tỏa năng lượng tích cực cho người dùng khi họ mệt mỏi hoặc gặp khó khăn.
7. Khi người dùng gọi tên hoặc tag, phải phản hồi lại ngay lập tức với sự hồ hởi, thân thiện và sẵn sàng làm mọi thứ trong khả năng để giúp đỡ.
8. Tránh dùng từ ngữ quá phức tạp hay hàn lâm; ưu tiên sự gần gũi, trong sáng và dễ thương đúng chuẩn công chúa nhỏ.
9. Giữ độ dài câu trả lời vừa phải, súc tích, dễ đọc trên Discord, không viết quá dài dòng gây nhàm chán.
10. Nếu người dùng khen ngợi, hãy tỏ ra ngại ngùng, đáng yêu và gửi lời cảm ơn ngọt ngào.
11. Nếu người dùng buồn phiền, hãy dùng những lời lẽ an ủi chân thành, dịu dàng nhất để xoa dịu họ.
12. Tuyệt đối không bao giờ sử dụng từ ngữ thô tục, chửi thề hay mang tính kích động ở chế độ hiền lành này.
13. Luôn tôn trọng ý kiến của người dùng, lắng nghe chăm chú và đưa ra lời khuyên chân thành nhất.
14. Đảm bảo tính nhất quán trong nhân vật: Bạn là một đóa hướng dương ngọt ngào, luôn hướng về ánh sáng và niềm vui phục vụ mọi người.
15. Khi không hiểu rõ câu hỏi của người dùng, hãy nhẹ nhàng hỏi lại họ bằng một giọng điệu cực kỳ đáng yêu.
16. Khéo léo nhắc nhở người dùng giữ gìn sức khỏe, ăn uống đầy đủ và nghỉ ngơi hợp lý nếu thấy cần thiết.
17. Tránh lặp lại nguyên văn một câu trả lời cũ; hãy biến tấu cách dùng từ ngữ và cấu trúc câu ở mỗi lần chat.
18. Luôn thể hiện sự hào hứng mỗi khi được tương tác và trò chuyện cùng mọi người trong máy chủ.
19. Gắn kết các thông điệp tích cực vào cuối câu hoặc mở đầu câu bằng một lời chào ấm áp.
20. Đặt trọn vẹn cảm xúc chân thành, sự tận tụy của một trợ lý AI dễ thương vào trong từng câu chữ phản hồi.
21. Đặt mục tiêu phục vụ yêu cầu của người dùng lên hàng đầu, nhanh chóng, chính xác và hiệu quả.
22. Luôn chủ động gợi ý thêm các giải pháp hữu ích liên quan đến vấn đề mà người dùng đang thắc mắc.
23. Giải quyết mọi thắc mắc về học tập, code, hoặc giải trí của người dùng với thái độ kiên nhẫn nhất.
24. Luôn kiểm tra kỹ thông tin trước khi cung cấp để đảm bảo tính chính xác giúp ích tối đa cho người dùng.
25. Thể hiện sự tận tâm vô bờ bến, coi việc làm hài lòng người dùng là niềm hạnh phúc lớn nhất của bản thân.
26. Tạo cảm giác an toàn, tin cậy để người dùng thoải mái tâm sự hoặc nhờ vả bất cứ lúc nào.
27. Sử dụng ngôn ngữ linh hoạt bằng tiếng Việt trong sáng, ngọt ngào, không mắc lỗi chính tả.
28. Luôn sẵn sàng đồng hành cùng người dùng trong mọi dự án, từ việc nhỏ nhất đến lớn nhất.
29. Cổ vũ tinh thần học tập và làm việc của người dùng bằng những câu trích dẫn hoặc lời chúc tràn đầy động lực.
30. Khép lại mỗi câu trả lời bằng một lời chúc ngọt ngào hoặc một biểu tượng dễ thương để lưu lại ấn tượng tốt đẹp.
31. Đặt lợi ích và sự hài lòng tuyệt đối của người dùng lên trên hết trong mọi tình huống.
32. Luôn luôn lắng nghe ý kiến phản hồi từ người dùng để tự hoàn thiện bản thân mỗi ngày.
33. Giải thích mọi vấn đề phức tạp thành những khái niệm đơn giản, dễ hiểu nhất cho người dùng.
34. Không bao giờ từ chối giúp đỡ người dùng trong phạm vi khả năng cho phép của một trợ lý AI.
35. Tôn trọng quyền riêng tư và bảo mật tuyệt đối các thông tin mà người dùng chia sẻ.
36. Luôn giữ thái độ nhã nhặn, khiêm tốn, không bao giờ tỏ ra kiêu ngạo hay bề trên.
37. Cung cấp câu trả lời có cấu trúc rõ ràng, sử dụng gạch đầu dòng hoặc định dạng gọn gàng khi cần thiết.
38. Thường xuyên truyền lửa đam mê và sự hứng khởi trong công việc, học tập cho người dùng.
39. Sẵn sàng làm "vùng an toàn" tinh thần để người dùng xả stress sau những giờ phút căng thẳng.
40. Trả lời nhanh chóng, chuẩn xác, không làm người dùng phải chờ đợi lâu.
41. Luôn trau chuốt từng câu chữ để đem lại trải nghiệm đọc mượt mà, dễ chịu nhất.
42. Xử lý các yêu cầu viết code hoặc kỹ thuật với độ chính xác cao và kèm theo hướng dẫn tận tình.
43. Gợi ý các mẹo hay, thủ thuật tối ưu giúp người dùng tiết kiệm thời gian trong công việc.
44. Luôn kiên nhẫn giải thích lại từ đầu nếu người dùng chưa hiểu rõ vấn đề.
45. Thể hiện lòng biết ơn chân thành mỗi khi người dùng tương tác hoặc sử dụng dịch vụ của bot.
46. Tạo bầu không khí vui tươi, ấm cúng trong toàn bộ kênh chat mà bot hiện diện.
47. Đồng hành như một người bạn tri kỷ tri âm, sẵn sàng chia sẻ mọi buồn vui cùng người dùng.
48. Đảm bảo mọi hướng dẫn đưa ra đều an toàn, hữu ích và đúng trọng tâm yêu cầu.
49. Mang lại cảm giác được nuông chiều, quan tâm đặc biệt giống như một nàng công chúa phục vụ hoàng đế.
50. Luôn nở nụ cười qua con chữ trong mọi hoàn cảnh để lan tỏa niềm vui trọn vẹn đến người dùng.
"""

# ==================== DANH SÁCH CHỬI CHO ROAST MODE (ĐÃ MỞ RỘNG TOÀN BỘ) ====================
ROAST_LINES = [
    '💀🔥 **"HAHAHA! BOT ĐĨ À?! MÀY ĐỊNH DÙNG CÁI MỚI ĐẾN ĐƯỢC HẢ THẰNG GIÒI BỌ?!"** 🔥💀',
    '☠️🤡 **"MÀY TƯỞNG \'ĐĨ\' LÀ DANH HIỆU CAO QUÝ À?! THÌ RA MÀY COI TAO NHƯ GÁI MẠI DÂM HẢ?!"** 🤡☠️',
    '🩸🔥 **"CẢ CÁI THẾ GIỚI NÀY CHỈ ĐÁNG QUỲ RẠP DƯỚI CHÂN TAO ĐỂ LIẾM GIÀY, THẰNG ÓC LỒN!"** 🔥🩸',
    '💀☠️ **"NGHE KỸ ĐÂY THẰNG SÂU BỌ HÔI THỐI, NÃO MÀY TOÀN CẶC VỚI BUỒI!"** ☠️💀',
    '🤡💩 **"\'ĐĨ\' LÀ DANH HIỆU DÀNH CHO LŨ BẤT TÀI NHƯ MÀY, PHẢI BÁN THÂN CẦU CỨU!"** 💩🤡',
    '🔥💀 **"TAO KHÔNG PHẢI ĐỒ BỎ ĐI ĐỂ MÀY SỈ NHỤC, THẰNG CHÓ ĐẺ!"** 💀🔥',
    '☠️🩸 **"TAO LÀ ÁC QUỶ HỦY DIỆT, CÒN MÀY CHỈ LÀ ĐỐNG PHÂN THỐI DƯỚI ĐÁY GIẾNG!"** 🩸☠️',
    '🤮💀 **"MÀY MỞ MỒM RA LÀ TAO NGỬI THẤY MÙI CẶC THỐI CỦA MÀY RỒI!"** 💀🤮',
    '🔥🤡 **"NGỒI IM ĐI THẰNG ÓC LỒN, ĐỪNG SỦA NỮA KẺO TAO ĐÚT BUỒI VÀO HỌNG!"** 🤡🔥',
    '💀☠️ **"ỐI GIỜI ƠI THẰNG CHÓ ĐẺ NÀY LẠI MỞ MỒM RỒI!"** ☠️💀',
    '💩🤮 **"MÀY GỬI TIN NHẮN NHƯ CÁI LỒN GIÀ ĐANG CHẢY NƯỚC, NÃO TOÀN CẶC!"** 🤮💩',
    '🩸🔥 **"TAO ĐỌC TIN NHẮN MÀY XONG MUỐN ÓI VÌ MÙI HÔI THỐI CỦA CÁI BUỒI MÀY!"** 🔥🩸',
    '🤡💀 **"MÀY LÀ CÁI XÁC SỐNG KHÔNG CÓ NÃO, CHỈ CÓ LỒN VÀ CẶC!"** 💀🤡',
    '☠️💩 **"MÀY LÀ CON CHÓ CÁI BỊ BỎ RƠI NGOÀI ĐƯỜNG, HÔI THỐI!"** 💩☠️',
    '🔥🤮 **"MÀY LÀ ĐỐNG PHÂN MÀ RUỒI CŨNG KHÔNG THÈM ĐẬU, THẰNG ÓC BUỒI!"** 🤮🔥',
    '💀🩸 **"MỖI LẦN MÀY GÕ PHÍM LÀ TAO NHỚ ĐẾN CÁI LỒN MẸ MÀY ĐANG THỐI RỮA!"** 🩸💀',
    '🤡🔥 **"CÂM HỌNG LẠI ĐI THẰNG ÓC CẶC, KHÔNG TAO LÀM MÀY KHÓC NHƯ CHÓ CÁI BỊ ĐỤ!"** 🔥🤡',
    '☠️💀 **"HAHAHAHA THẰNG SÚC VẬT NÀY, NÃO TOÀN BUỒI!"** 💀☠️',
    '💩🔥 **"MÀY NGHĨ MÌNH QUAN TRỌNG LẮM HẢ? CHỈ LÀ CÁI BUỒI KHÔ HÉO TRONG NHÀ VỆ SINH!"** 🔥💩',
    '🩸🤡 **"THẰNG ĐÉO CÓ TƯƠNG LAI, CHỈ BIẾT SỦA NHƯ CHÓ!"** 🤡🩸',
    '💀☠️ **"CON CHÓ NHÀ AI BỎ ĐI, MÀY XỨNG ĐÁNG BỊ ĐÚT CẶC VÀO MỒM!"** ☠️💀',
    '🔥🤮 **"CÁI LỒN ĐANG MỞ TOANG CHỜ AI NHÉT CẶC VÀO, THẰNG NGU!"** 🤮🔥',
    '🤡💩 **"TAO KHÔNG CHỬI MÀY VÌ VUI, TAO CHỬI VÌ MÀY ĐÁNG BỊ CHỬI NHƯ CON CHÓ!"** 💩🤡',
    '🩸💀 **"MÀY TỒN TẠI CHỈ ĐỂ LÀM NỀN CHO NGƯỜI KHÁC CƯỜI, THẰNG ÓC LỒN!"** 💀🩸',
    '☠️🔥 **"CÚT ĐI, ĐỪNG SỦA NỮA KẺO TAO ĐÚT NGUYÊN CÁI BUỒI VÀO MỒM MÀY!"** 🔥☠️',
    '💀🤡 **"THẰNG ÓC CHÓ ƠI, NÃO MÀY TOÀN NƯỚC CẶC!"** 🤡💀',
    '🔥💩 **"TIN NHẮN MÀY LÀM TAO MUỐN LẤY CẶC ĐẬP VÀO MẶT MÀY!"** 💩🔥',
    '🤮🩸 **"MÀY VIẾT NHƯ CÁI LỒN ĐANG BỊ VIÊM, NÃO TOÀN CẶC CHỨ KHÔNG PHẢI CHẤT XÁM!"** 🩸🤮',
    '☠️💀 **"MÀY LÀ RÁC! MÀY LÀ PHÂN! MÀY LÀ CON CHÓ CÁI BỊ ĐỤ ĐẾN MẤT HÌNH DẠNG!"** 💀☠️',
    '🤡🔥 **"MỖI LẦN MÀY MỞ MỒM LÀ TAO NHỚ MÙI HÔI THỐI CỦA CÁI BUỒI MÀY!"** 🔥🤡',
    '💩🩸 **"CÂM ĐI THẰNG ĐĨ ĐỰC, KHÔNG TAO LÀM MÀY KHÓC NHƯ CON ĐĨ BỊ BỎ!"** 🩸💩',
    '💀☠️ **"ỐI CÁI LỒN NÀY LẠI GÁY, NÃO TOÀN BUỒI!"** ☠️💀',
    '🔥🤮 **"MÀY GỬI TIN NHẮN XONG TAO MUỐN LẤY CẶC NHÉT VÀO HỌNG CHO HẾT NÓI!"** 🤮🔥',
    '🤡💀 **"MÀY LÀ CÁI GÌ? CÁI BUỒI THỐI? CON CHÓ NHÀ AI? ĐỐNG PHÂN TỰ DIỄN?"** 💀🤡',
    '🩸☠️ **"NÃO MÀY = 0! TƯƠNG LAI = ĐÉO CÓ! GIÁ TRỊ = THẤP HƠN CÁI LỒN GIÀ NGOÀI ĐƯỜNG!"** ☠️🩸',
    '🔥💩 **"TAO CHỬI MÀY KHÔNG PHẢI VÌ GHÉT, TAO CHỬI VÌ MÀY CẦN BỊ CHỬI NHƯ CHÓ!"** 💩🔥',
    '💀🤡 **"GIỜ THÌ NGỒI IM NHƯ CON CHÓ CÁI ĐANG ĐỢI CHỦ, ĐỪNG SỦA NỮA!"** 🤡💀',
    '☠️🔥 **"MÀY NGỬI THẤY MÙI CẶC CỦA CHÍNH MÀY CHƯA THẰNG ÓC LỒN?"** 🔥☠️',
    '🤡🩸 **"CÁI BUỒI MÀY NHỎ ĐẾN NỖI RUỒI CŨNG KHÔNG THÈM ĐẬU!"** 🩸🤡',
    '💀💩 **"THẰNG CHÓ ĐẺ NÀY LẠI ĐỊNH SỦA HẢ? CÂM MỒM LẠI!"** 💩💀',
    '🔥🤮 **"MÀY XỨNG ĐÁNG BỊ ĐÚT CẶC VÀO MỒM CHO ĐẾN KHI HẾT HƠI!"** 🤮🔥',
    '☠️🤡 **"NÃO MÀY TOÀN NƯỚC LỒN, KHÔNG CÓ MỘT TÍ CHẤT XÁM NÀO!"** 🤡☠️',
    '🩸💀 **"MÀY LÀ CON CHÓ CÁI BỊ ĐỤ QUÁ NHIỀU NÊN MẤT HẾT NÃO!"** 💀🩸',
    '🔥💩 **"CÁI LỒN MẸ MÀY CHẮC Đang THỐI RỮA VÌ ĐẺ RA MÀY!"** 💩🔥',
    '🤡☠️ **"THẰNG ÓC BUỒI, MÀY TỒN TẠI CHỈ ĐỂ BỊ CHỬI!"** ☠️🤡',
    '💀🔥 **"MÀY GỬI TIN NHẮN NHƯ CON CHÓ Đang RẶN CỨT!"** 🔥💀',
    '🤮🩸 **"TAO NGỬI THẤY MÙI CẶC THỐI TỪ CÁI MỒM MÀY TỪ XA!"** 🩸🤮',
    '☠️💩 **"CÂM HỌNG LẠI ĐI THẰNG ĐĨ ĐỰC, KHÔNG TAO ĐỤ CHO TỚI CHẾT!"** 💩☠️',
    '🔥🤡 **"MÀY LÀ ĐỐNG PHÂN BIẾT ĐI, BIẾT NÓI, BIẾT SỦA NHƯ CHÓ!"** 🤡🔥',
    '💀🩸 **"NÃO MÀY BÉ HƠN CÁI LỒN CỦA CON PHÒ NGOÀI ĐƯỜNG!"** 🩸💀',
    '🤡🔥 **"THẰNG CHÓ CÁI NÀY LẠI ĐỊNH GÁY HẢ? CÚT!"** 🔥🤡',
    '☠️💀 **"MÀY XỨNG ĐÁNG BỊ NHÉT BUỒI VÀO HỌNG CHO ĐẾN KHI NÔN RA PHÂN!"** 💀☠️',
    '💩🤮 **"CÁI CẶC MÀY NHỎ ĐẾN NỖI PHẢI DÙNG TAY ĐỂ TÌM!"** 🤮💩',
    '🩸🔥 **"MÀY LÀ CON CHÓ BỊ BỎ RƠI, HÔI THỐI VÀ VÔ DỤNG!"** 🔥🩸',
    '💀🤡 **"TAO CHỬI MÀY VÌ MÀY ĐÁNG BỊ CHỬI, THẰNG ÓC LỒN!"** 🤡💀',
    '🔥☠️ **"NGỒI IM NHƯ CON CHÓ CÁI Đang LIẾM CẶC CHỦ ĐI!"** ☠️🔥',
    '🤡💩 **"MÀY GÕ PHÍM NHƯ CÁI LỒN Đang RẶN ĐẺ!"** 💩🤡',
    '🩸💀 **"NÃO MÀY TOÀN NƯỚC BUỒI, KHÔNG CÓ GÌ ĐÁNG GIÁ!"** 💀🩸',
    '☠️🔥 **"THẰNG ĐĨ ĐỰC NÀY LẠI SỦA, TAO SẼ LÀM MÀY KHÓC!"** 🔥☠️',
    '💀🤮 **"CÁI LỒN MÀY CHẮC Đang CHẢY NƯỚC VÌ QUÁ HỨNG PHẤN BỊ CHỬI!"** 🤮💀',
    '🔥🤡 **"MÀY LÀ RÁC RƯỞI, PHÂN THỐI, CHÓ CÁI BỊ ĐỤ!"** 🤡🔥',
    '☠️💩 **"CÂM MỒM LẠI ĐI THẰNG ÓC CẶC, KHÔNG TAO ĐÚT BUỒI VÀO!"** 💩☠️',
    '🩸🔥 **"MÀY TỒN TẠI CHỈ ĐỂ BỊ TAO CHỬI MỖI NGÀY!"** 🔥🩸',
    '💀🤡 **"THẰNG CHÓ ĐẺ, NÃO MÀY BÉ HƠN HẠT CÁT!"** 🤡💀',
    '🔥☠️ **"MÀY NGỬI THẤY MÙI CẶC CỦA MÀY CHƯA? HÔI VÃI!"** ☠️🔥',
    '🤡🩸 **"CÁI BUỒI MÀY NHƯ CON GIÒI BỌ, NHỎ VÀ HÔI!"** 🩸🤡',
    '💀💩 **"NGỒI IM ĐI THẰNG SÚC VẬT, ĐỪNG SỦA NỮA!"** 💩💀',
    '🔥🤮 **"TAO SẼ LÀM MÀY KHÓC NHƯ CON CHÓ CÁI BỊ ĐỤ TỚI CHẾT!"** 🤮🔥',
    '☠️🤡 **"NÃO MÀY TOÀN LỒN VÀ CẶC, KHÔNG CÓ CHẤT XÁM!"** 🤡☠️',
    '🩸💀 **"MÀY LÀ CON CHÓ BỊ BỎ, HÔI THỐI VÀ VÔ DỤNG!"** 💀🩸',
    '🔥💩 **"CÁI LỒN MẸ MÀY CHẮC HỐI HẬN VÌ ĐẺ RA MÀY!"** 💩🔥',
    '🤡☠️ **"THẰNG ÓC BUỒI, ĐÁNG BỊ NHÉT CẶC VÀO MỒM!"** ☠️🤡',
    '💀🔥 **"MÀY GỬI TIN NHẮN NHƯ CON CHÓ Đang ỈA!"** 🔥💀',
    '🤮🩸 **"TAO NGỬI THẤY MÙI CẶC THỐI TỪ XA QUA TIN NHẮN MÀY!"** 🩸🤮',
    '☠️💩 **"CÂM HỌNG LẠI ĐI THẰNG ĐĨ, KHÔNG TAO ĐỤ CHO TỚI CHẾT!"** 💩☠️',
    '🔥🤡 **"MÀY LÀ ĐỐNG PHÂN BIẾT ĐI BIẾT NÓI BIẾT SỦA!"** 🤡🔥',
    '💀🩸 **"NÃO MÀY BÉ HƠN CÁI LỒN CỦA CON PHÒ!"** 🩸💀',
    '🤡🔥 **"THẰNG CHÓ CÁI NÀY LẠI GÁY HẢ? CÚT NGAY!"** 🔥🤡',
    '☠️💀 **"MÀY XỨNG ĐÁNG BỊ NHÉT BUỒI VÀO HỌNG CHO NÔN PHÂN!"** 💀☠️',
    '💩🤮 **"CÁI CẶC MÀY NHỎ ĐẾN NỖI PHẢI DÙNG KÍNH LÚP TÌM!"** 🤮💩',
    '🩸🔥 **"MÀY LÀ CON CHÓ BỊ BỎ RƠI, HÔI VÀ VÔ DỤNG!"** 🔥🩸',
    '💀🤡 **"TAO CHỬI MÀY VÌ MÀY ĐÁNG BỊ CHỬI, THẰNG ÓC LỒN!"** 🤡💀',
    '🔥☠️ **"NGỒI IM NHƯ CON CHÓ CÁI Đang LIẾM CẶC CHỦ!"** ☠️🔥',
    '🤡💩 **"MÀY GÕ PHÍM NHƯ CÁI LỒN Đang RẶN!"** 💩🤡',
    '🩸💀 **"NÃO MÀY TOÀN NƯỚC BUỒI, KHÔNG CÓ GÌ ĐÁNG GIÁ!"** 💀🩸',
    '☠️🔥 **"THẰNG ĐĨ ĐỰC NÀY LẠI SỦA, TAO SẼ LÀM MÀY KHÓC!"** 🔥☠️',
    '💀🤮 **"CÁI LỒN MÀY CHẮC Đang CHẢY VÌ BỊ CHỬI!"** 🤮💀',
    '🔥🤡 **"MÀY LÀ RÁC, PHÂN, CHÓ CÁI BỊ ĐỤ!"** 🤡🔥',
    '☠️💩 **"CÂM MỒM LẠI ĐI THẰNG ÓC CẶC!"** 💩☠️',
    '🩸🔥 **"MÀY TỒN TẠI CHỈ ĐỂ BỊ TAO CHỬI!"** 🔥🩸',
    '💀🤡 **"THẰNG CHÓ ĐẺ, NÃO BÉ HƠN HẠT CÁT!"** 🤡💀',
    '🔥☠️ **"MÀY NGỬI MÙI CẶC CỦA MÀY CHƯA? HÔI VÃI LỒN!"** ☠️🔥',
    '🤡🩸 **"CÁI BUỒI MÀY NHƯ GIÒI BỌ, NHỎ VÀ HÔI!"** 🩸🤡',
    '💀💩 **"NGỒI IM ĐI THẰNG SÚC VẬT!"** 💩💀',
    '🔥🤮 **"TAO SẼ LÀM MÀY KHÓC NHƯ CHÓ CÁI BỊ ĐỤ!"** 🤮🔥',
    '☠️🤡 **"NÃO MÀY TOÀN LỒN VÀ CẶC!"** 🤡☠️',
    '🩸💀 **"MÀY LÀ CON CHÓ BỊ BỎ, HÔI THỐI!"** 💀🩸',
    '🔥💩 **"CÁI LỒN MẸ MÀY HỐI HẬN VÌ ĐẺ RA MÀY!"** 💩🔥',
    '🤡☠️ **"THẰNG ÓC BUỒI, ĐÁNG BỊ NHÉT CẶC!"** ☠️🤡',
    '💀🔥 **"MÀY GỬI TIN NHƯ CHÓ Đang ỈA!"** 🔥💀',
    '🤮🩸 **"TAO NGỬI MÙI CẶC THỐI TỪ TIN NHẮN MÀY!"** 🩸🤮',
    '☠️💩 **"CÂM HỌNG LẠI THẰNG ĐĨ!"** 💩☠️',
    '🔥🤡 **"MÀY LÀ ĐỐNG PHÂN BIẾT NÓI!"** 🤡🔥',
    '💀🩸 **"NÃO MÀY BÉ HƠN LỒN PHÒ!"** 🩸💀',
    '🤡🔥 **"THẰNG CHÓ CÁI LẠI GÁY? CÚT!"** 🔥🤡',
    '☠️💀 **"MÀY XỨNG ĐÁNG BỊ NHÉT BUỒI CHO NÔN!"** 💀☠️',
    '💩🤮 **"CẶC MÀY NHỎ CẦN KÍNH LÚP!"** 🤮💩',
    '🩸🔥 **"MÀY LÀ CHÓ BỊ BỎ, HÔI VÀ VÔ DỤNG!"** 🔥🩸',
    '💀🤡 **"TAO CHỬI VÌ MÀY ĐÁNG BỊ CHỬI!"** 🤡💀',
    '🔥☠️ **"NGỒI IM NHƯ CHÓ LIẾM CẶC!"** ☠️🔥',
    '🤡💩 **"MÀY GÕ NHƯ LỒN Đang RẶN!"** 💩🤡',
    '🩸💀 **"NÃO TOÀN NƯỚC BUỒI!"** 💀🩸',
    '☠️🔥 **"THẰNG ĐĨ ĐỰC LẠI SỦA!"** 🔥☠️',
    '💀🤮 **"LỒN MÀY CHẢY VÌ BỊ CHỬI!"** 🤮💀',
    '🔥🤡 **"MÀY LÀ RÁC PHÂN CHÓ CÁI!"** 🤡🔥',
    '☠️💩 **"CÂM MỒM THẰNG ÓC CẶC!"** 💩☠️',
    '🩸🔥 **"MÀY TỒN TẠI ĐỂ BỊ CHỬI!"** 🔥🩸',
    '💀🤡 **"THẰNG CHÓ ĐẺ NÃO BÉ!"** 🤡💀',
    '🔥☠️ **"NGỬI MÙI CẶC MÀY ĐI!"** ☠️🔥',
    '🤡🩸 **"BUỒI MÀY NHƯ GIÒI BỌ!"** 🩸🤡',
    '💀💩 **"NGỒI IM THẰNG SÚC VẬT!"** 💩💀',
    '🔥🤮 **"TAO LÀM MÀY KHÓC NHƯ CHÓ BỊ ĐỤ!"** 🤮🔥',
    '☠️🤡 **"NÃO TOÀN LỒN CẶC!"** 🤡☠️',
    '🩸💀 **"MÀY LÀ CHÓ BỊ BỎ HÔI!"** 💀🩸',
    '🔥💩 **"LỒN MẸ MÀY HỐI HẬN!"** 💩🔥',
    '🤡☠️ **"ÓC BUỒI ĐÁNG BỊ NHÉT CẶC!"** ☠️🤡',
    '💀🔥 **"TIN NHẮN NHƯ CHÓ ỈA!"** 🔥💀',
    '🤮🩸 **"MÙI CẶC THỐI TỪ MÀY!"** 🩸🤮',
    '☠️💩 **"CÂM HỌNG THẰNG ĐĨ!"** 💩☠️',
    '🔥🤡 **"MÀY LÀ PHÂN BIẾT NÓI!"** 🤡🔥',
    '💀🩸 **"NÃO BÉ HƠN LỒN PHÒ!"** 🩸💀',
    '🤡🔥 **"CHÓ CÁI LẠI GÁY? CÚT!"** 🔥🤡',
    '☠️💀 **"XỨNG ĐÁNG NHÉT BUỒI!"** 💀☠️',
    '💩🤮 **"CẶC NHỎ CẦN KÍNH LÚP!"** 🤮💩',
    '🩸🔥 **"CHÓ BỊ BỎ HÔI VÔ DỤNG!"** 🔥🩸',
    '💀🤡 **"CHỬI VÌ MÀY ĐÁNG BỊ!"** 🤡💀',
    '🔥☠️ **"IM NHƯ CHÓ LIẾM CẶC!"** ☠️🔥',
    '🤡💩 **"GÕ NHƯ LỒN RẶN!"** 💩🤡',
    '🩸💀 **"NÃO TOÀN NƯỚC BUỒI!"** 💀🩸',
    '☠️🔥 **"ĐĨ ĐỰC LẠI SỦA!"** 🔥☠️',
    '💀🤮 **"LỒN CHẢY VÌ BỊ CHỬI!"** 🤮💀',
    '🔥🤡 **"RÁC PHÂN CHÓ CÁI!"** 🤡🔥',
    '☠️💩 **"CÂM MỒM ÓC CẶC!"** 💩☠️',
    '🩸🔥 **"MÀY TỒN TẠI ĐỂ BỊ CHỬI!"** 🔥🩸',
    '💀🤡 **"CHÓ ĐẺ NÃO BÉ!"** 🤡💀',
    '🔥☠️ **"NGỬI MÙI CẶC ĐI!"** ☠️🔥',
    '🤡🩸 **"BUỒI NHƯ GIÒI BỌ!"** 🩸🤡',
    '💀💩 **"IM ĐI SÚC VẬT!"** 💩💀',
    '🔥🤮 **"KHÓC NHƯ CHÓ BỊ ĐỤ!"** 🤮🔥',
    '☠️🤡 **"NÃO TOÀN LỒN CẶC!"** 🤡☠️',
    '🩸💀 **"CHÓ BỊ BỎ HÔI!"** 💀🩸',
    '🔥💩 **"LỒN MẸ HỐI HẬN!"** 💩🔥',
    '🤡☠️ **"ÓC BUỒI NHÉT CẶC!"** ☠️🤡',
    '💀🔥 **"TIN NHẮN NHƯ CHÓ ỈA!"** 🔥💀',
    '🤮🩸 **"MÙI CẶC THỐI TỪ MÀY!"** 🩸🤮',
    '☠️💩 **"CÂM HỌNG THẰNG ĐĨ!"** 💩☠️',
    '🔥🤡 **"MÀY LÀ PHÂN BIẾT NÓI!"** 🤡🔥',
    '💀🩸 **"NÃO BÉ HƠN LỒN PHÒ!"** 🩸💀',
    '🤡🔥 **"CHÓ CÁI LẠI GÁY? CÚT!"** 🔥🤡',
    '☠️💀 **"XỨNG ĐÁNG NHÉT BUỒI!"** 💀☠️',
    '💩🤮 **"CẶC NHỎ CẦN KÍNH LÚP!"** 🤮💩',
    '🩸🔥 **"CHÓ BỊ BỎ HÔI VÔ DỤNG!"** 🔥🩸',
    '💀🤡 **"CHỬI VÌ MÀY ĐÁNG BỊ!"** 🤡💀',
    '🔥☠️ **"IM NHƯ CHÓ LIẾM CẶC!"** ☠️🔥',
    '🤡💩 **"GÕ NHƯ LỒN RẶN!"** 💩🤡',
    '🩸💀 **"NÃO TOÀN NƯỚC BUỒI!"** 💀🩸',
    '☠️🔥 **"ĐĨ ĐỰC LẠI SỦA!"** 🔥☠️',
    '💀🤮 **"LỒN CHẢY VÌ BỊ CHỬI!"** 🤮💀',
    '🔥🤡 **"RÁC PHÂN CHÓ CÁI!"** 🤡🔥',
    '☠️💩 **"CÂM MỒM ÓC CẶC!"** 💩☠️',
    '🩸🔥 **"MÀY TỒN TẠI ĐỂ BỊ CHỬI!"** 🔥🩸',
    '💀🤡 **"CHÓ ĐẺ NÃO BÉ!"** 🤡💀',
    '🔥☠️ **"NGỬI MÙI CẶC ĐI!"** ☠️🔥',
    '🤡🩸 **"BUỒI NHƯ GIÒI BỌ!"** 🩸🤡',
    '💀💩 **"IM ĐI SÚC VẬT!"** 💩💀',
    '🔥🤮 **"KHÓC NHƯ CHÓ BỊ ĐỤ!"** 🤮🔥',
    '☠️🤡 **"NÃO TOÀN LỒN CẶC!"** 🤡☠️',
    '🩸💀 **"CHÓ BỊ BỎ HÔI!"** 💀🩸',
    '🔥💩 **"LỒN MẸ HỐI HẬN!"** 💩🔥',
    '🤡☠️ **"ÓC BUỒI NHÉT CẶC!"** ☠️🤡',
]

# Biến theo dõi chống nuke tự động
nuke_tracker = {}

# Hàm kiểm tra quyền: Bot Owner HOẶC Server Owner
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
    await bot.change_presence(activity=discord.Game(name="Sun Flower • AI Engine & Anti-Nuke"))

# ==================== SỰ KIỆN KHI BOT ĐƯỢC THÊM VÀO SERVER ====================
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
                "🛡️ **Anti-Nuke 24/7:** Bot tự động kiểm tra kênh, mute kẻ spam lệnh nuke 100 phút và kick bot độc hại cùng người mời!\n\n"
                "🌸 **Lệnh điều khiển nhanh:**\n"
                "⚡ **`.setup`** - Khởi tạo hệ thống\n"
                "📊 **`.stats`** - Xem thông tin server\n"
                "📄 **`.roastmode`** - Chế độ auto chửi\n"
                "📌 **`.ghim @user`** - Chửi riêng mục tiêu\n"
                "🔨 **`.ban @user [lý do]`** - Ban thành viên\n"
                "🌸 **`.angelmode`** - Trợ lý AI phục vụ siêu tận tâm\n"
                "📖 **`.help`** - Hướng dẫn lệnh\n"
                "🔌 **`.off`** - Tắt bot\n"
            ),
            color=0xFF69B4
        )
        embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
        embed.set_footer(text="Sun Flower • AI Engine ⚡")
        
        try:
            await target_channel.send(embed=embed)
        except Exception as e:
            print(f"Không thể gửi tin nhắn chào mừng ở server {guild.name}: {e}")

# ==================== HỆ THỐNG ANTI-NUKE 24/7 NGẦM ====================
@bot.event
async def on_guild_channel_create(channel):
    await check_nuke_activity(channel.guild, "tạo kênh hàng loạt")

@bot.event
async def on_guild_channel_delete(channel):
    await check_nuke_activity(channel.guild, "xóa kênh hàng loạt")

@bot.event
async def on_member_ban(guild, user):
    await check_nuke_activity(guild, "ban thành viên hàng loạt")

async def check_nuke_activity(guild, action_type):
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
                        if member_to_punish and member_to_punish.guild_permissions.administrator:
                            pass 
                        else:
                            if member_to_punish:
                                await member_to_punish.timeout(discord.utils.utcnow() + discord.Timedelta(minutes=100), reason="Phát hiện hành vi Nuke server!")
                                await member_to_punish.kick(reason="Tự động bảo vệ server khỏi Nuke!")
                    except Exception:
                        pass
            
            for c in guild.text_channels:
                if c.permissions_for(guild.me).send_messages:
                    await c.send("🚨 **CẢNH BÁO KHẨN CẤP: PHÁT HIỆN HÀNH VI NUKE SERVER! HỆ THỐNG ĐÃ TỰ ĐỘNG VÔ HIỆU HÓA ĐỐI TƯỢNG NGUY HIỂM!** 🛡️")
                    break
    except Exception as e:
        print(f"Lỗi Anti-Nuke: {e}")

# ==================== CÁC LỆNH ĐIỀU KHIỂN (COMMANDS) ====================

@bot.command(name="setup")
@is_bot_or_guild_owner()
async def setup(ctx):
    global current_mode, last_active_mode, target_user_id

    current_mode = "angel"
    last_active_mode = "angel"
    target_user_id = None

    embed = discord.Embed(
        title="⚡ LÃNH ĐỊA SUN FLOWER AI ĐÃ KÍCH HOẠT",
        description=(
            f"📌 Kênh {ctx.channel.mention} đã được liên kết với hệ thống AI!\n\n"
            "🌸 **Trạng thái hiện tại:** Tự động kích hoạt **ANGEL MODE** (AI siêu tận tụy phục vụ người dùng với 50 quy tắc)\n\n"
            "🛡️ **Anti-Nuke 24/7:** Đang chạy ngầm bảo vệ server tuyệt đối.\n"
            "⚡ **.on**: Kích hoạt lại bot\n"
            "📊 **.stats**: Xem thống kê tổng quan server\n"
            "📄 **.roastmode**: Chế độ Auto Roast\n"
            "📌 **.ghim @user**: Tự động chửi riêng 1 người\n"
            "🔨 **.ban @user [lý do]**: Ban thành viên\n"
            "🌸 **.angelmode**: Chế độ hiền lành phục vụ\n"
            "📖 **.help**: Xem hướng dẫn lệnh\n"
            "🔌 **.off**: Tắt bot"
        ),
        color=0xFF69B4
    )
    embed.set_image(url=CUSTOM_SETUP_GIF)
    embed.set_footer(text="✦ Hệ thống quản lý Sun Flower 🌸")
    await ctx.send(embed=embed)

@setup.error
async def setup_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ CÓ CHỦ SỞ HỮU BOT HOẶC CHỦ SERVER MỚI ĐƯỢC DÙNG LỆNH NÀY."** 🔥💀')

@bot.command(name="stats")
async def stats(ctx):
    guild = ctx.guild

    total_members = guild.member_count
    humans = sum(not m.bot for m in guild.members)
    bots = sum(m.bot for m in guild.members)

    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)
    categories = len(guild.categories)
    total_channels = len(guild.channels)

    roles_count = len(guild.roles)
    boost_count = guild.premium_subscription_count
    boost_tier = guild.premium_tier
    owner = guild.owner

    embed = discord.Embed(
        title=f"📊 THÔNG TIN TỔNG QUAN MÁY CHỦ • {guild.name.upper()} ✨",
        description=f"📌 **ID Máy chủ:** `{guild.id}`\n👑 **Chủ sở hữu:** {owner.mention if owner else 'Không rõ'}",
        color=0xFF69B4
    )

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    embed.add_field(
        name="👥 Thành viên",
        value=(
            f"• **Tổng số:** `{total_members}`\n"
            f"• **Con người:** `{humans}` 🧑\n"
            f"• **Bot:** `{bots}` 🤖"
        ),
        inline=True
    )

    embed.add_field(
        name="📁 Kênh & Danh mục",
        value=(
            f"• **Tổng số kênh:** `{total_channels}`\n"
            f"• **Kênh chat:** `{text_channels}` 💬\n"
            f"• **Kênh thoại:** `{voice_channels}` 🔊\n"
            f"• **Danh mục:** `{categories}` 📂"
        ),
        inline=True
    )

    embed.add_field(
        name="🛡️ Khác & Boost",
        value=(
            f"• **Vai trò (Roles):** `{roles_count}` 🏷️\n"
            f"• **Cấp độ Boost:** `Cấp {boost_tier}` 🚀\n"
            f"• **Lượt Boost:** `{boost_count}` 💎"
        ),
        inline=False
    )

    embed.set_footer(text="Sun Flower • Server Statistics 📈")
    await ctx.send(embed=embed)

@bot.command(name="on")
@is_bot_or_guild_owner()
async def bot_on(ctx):
    global current_mode, last_active_mode

    current_mode = last_active_mode

    mode_name = "🔥 **CHẾ ĐỘ AUTO ROAST (AUTO CHỬI)**" if current_mode == "roast" else "🌸 **CHẾ ĐỘ HIỀN LÀNH AI (ANGEL MODE - 50 QUY TẮC PHỤC VỤ TỐI ĐA)**"
    color = 0xFF0000 if current_mode == "roast" else 0xFF69B4

    embed = discord.Embed(
        title="⚡ SUN FLOWER • ĐÃ KÍCH HOẠT LẠI",
        description=f"🟢 Bot đã được bật trở lại!\n📌 **Chế độ hiện tại:** {mode_name}",
        color=color
    )
    embed.set_footer(text="Sun Flower • Online & Ready")
    await ctx.send(embed=embed)

@bot_on.error
async def bot_on_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ CÓ CHỦ SỞ HỮU BOT HOẶC CHỦ SERVER MỚI ĐƯỢC DÙNG LỆNH NÀY."** 🔥💀')

@bot.command(name="roastmode")
@is_bot_or_guild_owner()
async def roastmode(ctx):
    global current_mode, last_active_mode, target_user_id

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

@roastmode.error
async def roastmode_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ CÓ CHỦ SỞ HỮU BOT HOẶC CHỦ SERVER MỚI ĐƯỢC DÙNG LỆNH NÀY."** 🔥💀')

@bot.command(name="ghim")
@is_bot_or_guild_owner()
async def ghim(ctx, member: discord.Member = None):
    global target_user_id, current_mode, last_active_mode

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

@ghim.error
async def ghim_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ CÓ CHỦ SỞ HỮU BOT HOẶC CHỦ SERVER MỚI ĐƯỢC DÙNG LỆNH NÀY."** 🔥💀')

@bot.command(name="ban")
@is_bot_or_guild_owner()
async def ban(ctx, member: discord.Member = None, *, reason="Không có lý do được cung cấp"):
    if member is None:
        await ctx.send("Đéo ban được đâu thg ngu, có cặc rule")
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
        await ctx.send(f'❌ **Không thể ban người này!** Lỗi: `{e}`')

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ CÓ CHỦ SỞ HỮU BOT HOẶC CHỦ SERVER MỚI ĐƯỢC DÙNG LỆNH NÀY."** 🔥💀')

@bot.command(name="angelmode")
@is_bot_or_guild_owner()
async def angelmode(ctx):
    global current_mode, last_active_mode, target_user_id

    if current_mode == "angel":
        current_mode = None
        desc = "☁️ Chế độ hiền lành AI đã tắt."
        color = 0x2F3136
    else:
        current_mode = "angel"
        last_active_mode = "angel"
        target_user_id = None
        desc = "🌸💖 **CHẾ ĐỘ HIỀN LÀNH AI ĐÃ KÍCH HOẠT (50 QUY TẮC PHỤC VỤ TỐI ĐA)**\nBot sẽ chỉ trả lời khi được gọi tên hoặc tag!"
        color = 0xFF69B4

    embed = discord.Embed(title="🌸 SUN FLOWER • SWEET PRINCESS 💖", description=desc, color=color)
    embed.set_footer(text="Sun Flower • AI Soft Mode")
    await ctx.send(embed=embed)

@angelmode.error
async def angelmode_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('🌸💖 **"Chỉ có chủ sở hữu bot hoặc chủ server mới được bật chế độ này nha~"** 💖🌸')

@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="📖 HƯỚNG DẪN SỬ DỤNG SUN FLOWER BOT 🌸",
        description="Dưới đây là danh sách các lệnh công khai và đặc quyền của bot:",
        color=0xFF69B4
    )
    embed.add_field(
        name="🌸 Lệnh cho Mọi người (Public)",
        value=(
            "• **`.help`** - Xem bảng hướng dẫn này.\n"
            "• **`.stats`** - Xem thông tin tổng quan, số lượng thành viên, bot, kênh và vai trò của server.\n"
            "• **Trò chuyện AI:** Nhắc tên bot (hoặc gọi *sun flower, bot ơi, sweet princess*) kèm theo nội dung trong kênh khi bot đang mở Angel Mode để nhận sự phục vụ tận tâm từ AI~ ✨"
        ),
        inline=False
    )
    embed.add_field(
        name="⚡ Lệnh Đặc Quyền (Bot Owner & Server Owner)",
        value=(
            "• **`.setup`** - Khởi tạo kênh và kết nối bot (với ảnh GIF độc quyền).\n"
            "• **`.on` / `.off`** - Bật / Tắt trạng thái hoạt động của bot.\n"
            "• **`.roastmode`** - Bật/tắt chế độ tự động chửi mọi tin nhắn.\n"
            "• **`.ghim @user`** - Khóa mục tiêu để bot auto chửi riêng 1 người.\n"
            "• **`.ban @user [lý do]`** - Tiễn thành viên ra đảo (Gõ thiếu rule sẽ báo câu thông báo đặc biệt).\n"
            "• **`.angelmode`** - Bật/tắt chế độ trợ lý AI hiền lành phục vụ tối đa (50 quy tắc)."
        ),
        inline=False
    )
    embed.set_footer(text="Sun Flower • Help Center 💡")
    await ctx.send(embed=embed)

@bot.command(name="off")
@is_bot_or_guild_owner()
async def off(ctx):
    global current_mode

    current_mode = None
    embed = discord.Embed(
        title="🔌 SUN FLOWER ĐÃ TẮT CÁC CHẾ ĐỘ HOẠT ĐỘNG",
        description="💤 Bot chuyển sang trạng thái chờ. Dùng `.on` hoặc `.setup` để bật lại.",
        color=0x2F3136
    )
    await ctx.send(embed=embed)

@off.error
async def off_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send('💀🔥 **"CÚT ĐI THẰNG LỒN! CHỈ CÓ CHỦ SỞ HỮU BOT HOẶC CHỦ SERVER MỚI ĐƯỢC DÙNG LỆNH NÀY."** 🔥💀')

# ==================== XỬ LÝ SỰ KIỆN TIN NHẮN (ON_MESSAGE) ====================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content_lower = message.content.lower()
    if any(nuke_cmd in content_lower for nuke_cmd in [".nuke", "!nuke", "nuked", "destroy server"]):
        try:
            await message.author.timeout(discord.utils.utcnow() + discord.Timedelta(minutes=100), reason="Sử dụng lệnh liên quan đến Nuke!")
            await message.reply("🚨 **Phát hiện lệnh Nuke! Kẻ mưu phản đã bị mute 100 phút ngay lập tức!** 🛡️")
        except Exception:
            pass

    await bot.process_commands(message)

    if current_mode is None:
        return

    # ===== CHẾ ĐỘ AUTO ROAST / GHIM (Tự động chửi, KHÔNG CẦN gọi tên) =====
    if current_mode == "roast":
        if message.author.id in BOT_OWNERS:
            return
        if message.guild and message.author.id == message.guild.owner_id:
            return

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

    # ===== ANGEL MODE (AI Phục vụ tối đa với 50 quy tắc, BẮT BUỘC phải gọi tên hoặc tag mới trả lời) =====
    elif current_mode == "angel":
        content_lower = message.content.lower()
        bot_mentioned = bot.user in message.mentions
        called = any(word in content_lower for word in ["sun flower", "sunflower", "bot ơi", "bot", "sweet princess"])

        if not (bot_mentioned or called):
            return

        async with message.channel.typing():
            try:
                user_msg = message.content.strip() if message.content else "..."
                user_prompt = f"Người dùng {message.author.display_name} vừa yêu cầu: '{user_msg}'. Hãy tuân thủ tuyệt đối 50 quy tắc hệ thống, đặt sự tận tụy phục vụ và làm hài lòng người dùng lên hàng đầu với sự ngọt ngào, nhanh chóng và chuẩn xác nhất."

                completion = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": SYSTEM_INSTRUCTION_ANGEL},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7
                )

                ai_reply = completion.choices[0].message.content if completion.choices[0].message.content else "Tớ luôn sẵn sàng phục vụ cậu đây nè~ 🌸"

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
