import os
import google.generativeai as genai
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env
load_dotenv()

# Lấy API key từ biến môi trường
API_KEY = os.getenv('GOOGLE_API_KEY')

# Kiểm tra xem API key có tồn tại không
if not API_KEY:
    raise ValueError("Lỗi: Không tìm thấy GOOGLE_API_KEY. Vui lòng tạo file .env và thêm key của bạn vào đó.")

# Cấu hình thư viện google.generativeai với API key
genai.configure(api_key=API_KEY)

# Khởi tạo model Gemma (phiên bản mới nhất)
# Cấu hình an toàn (safety_settings) được nới lỏng để cho phép các câu trả lời đa dạng hơn
# (Lưu ý: điều này có thể trả về nội dung nhạy cảm, nhưng cần thiết cho các tác vụ như tạo code)
generation_config = genai.GenerationConfig(
    temperature=0.7,  # Tăng tính sáng tạo
    top_p=0.9,
    top_k=40
)

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

try:
    model = genai.GenerativeModel(
        model_name='models/gemma-3-27b-it', # Sử dụng model gemma-latest như yêu cầu
        generation_config=generation_config,
        safety_settings=safety_settings
    )
except Exception as e:
    print(f"Lỗi khi khởi tạo model Gemma: {e}")
    model = None

def call_gemma(user_text: str, instruction: str) -> str:
    """
    Hàm này chịu trách nhiệm gọi API Google Gemma.
    
    Nó sử dụng kỹ thuật "Prompt Engineering" bằng cách kết hợp
    chỉ thị (instruction) và văn bản người dùng (user_text)
    để tạo ra một prompt rõ ràng cho LLM.

    Args:
        user_text: Văn bản đầu vào từ <textarea> của người dùng.
        instruction: Chỉ thị tác vụ (ví dụ: "Tóm tắt văn bản này:").

    Returns:
        Một chuỗi (str) chứa kết quả do AI tạo ra.
    """
    if model is None:
        return "Lỗi: Model Gemma chưa được khởi tạo thành công. Vui lòng kiểm tra API Key và cấu hình."

    # --- Kỹ thuật Prompt Engineering ---
    # Ghép chỉ thị và văn bản người dùng để tạo prompt hoàn chỉnh.
    # Sử dụng dấu phân cách rõ ràng (---) giúp model hiểu rõ
    # đâu là chỉ thị và đâu là dữ liệu cần xử lý.
    prompt = f"{instruction}\n\n---\n\n{user_text}"

    print(f"DEBUG: Đang gửi prompt tới Gemma:\n{prompt}") # Ghi log prompt để debug

    try:
        # Gọi API để tạo nội dung
        response = model.generate_content(prompt)
        
        # Xử lý trường hợp model không trả về gì (ví dụ: bị bộ lọc an toàn chặn)
        if not response.parts:
             return "Lỗi: Model đã trả về một phản hồi rỗng. Điều này có thể do bộ lọc an toàn hoặc nội dung đầu vào."
        
        # Trả về phần văn bản từ phản hồi
        return response.text
    
    except Exception as e:
        # Xử lý các lỗi API khác (ví dụ: hết hạn ngạch, lỗi xác thực)
        print(f"Lỗi khi gọi Google AI Studio: {e}")
        return f"Lỗi: Đã xảy ra sự cố khi liên hệ với dịch vụ AI. Chi tiết: {str(e)}"