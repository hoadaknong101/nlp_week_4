from flask import Flask, render_template, request, jsonify
import llm_service  # Import file logic LLM riêng biệt
import os # Dùng để chạy app

# Khởi tạo ứng dụng Flask
app = Flask(__name__)

@app.route('/')
def index():
    """
    Route chính, phục vụ file 'index.html' cho frontend.
    """
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    """
    Đây là API endpoint chính của backend.
    Nó nhận yêu cầu POST từ JavaScript của frontend.
    
    Yêu cầu JSON đầu vào:
    {
        "text_input": "Nội dung văn bản của người dùng...",
        "task_instruction": "Chỉ thị tác vụ, ví dụ: 'Tóm tắt văn bản này'"
    }
    
    Phản hồi JSON đầu ra:
    {"result": "Kết quả từ Gemma..."}
    hoặc
    {"error": "Chi tiết lỗi..."}
    """
    try:
        # Lấy dữ liệu JSON từ request
        data = request.get_json()

        # --- Xác thực đầu vào ---
        if not data or 'text_input' not in data or 'task_instruction' not in data:
            # Nếu thiếu dữ liệu, trả về lỗi 400 Bad Request
            return jsonify({"error": "Đầu vào không hợp lệ. 'text_input' và 'task_instruction' là bắt buộc."}), 400

        user_text = data['text_input']
        instruction = data['task_instruction']

        # --- Gọi Service Layer ---
        # Chuyển dữ liệu sang llm_service để xử lý (tách biệt logic)
        print(f"DEBUG: Nhận yêu cầu: text='{user_text[:20]}...', instruction='{instruction}'")
        result_text = llm_service.call_gemma(user_text, instruction)

        # --- Trả về kết quả ---
        # Trả về kết quả từ LLM dưới dạng JSON
        return jsonify({"result": result_text})

    except Exception as e:
        # Xử lý các lỗi server chung
        print(f"Lỗi nghiêm trọng tại endpoint /process: {e}")
        return jsonify({"error": "Đã xảy ra lỗi nội bộ máy chủ."}), 500

# Chạy ứng dụng web
if __name__ == '__main__':
    # Chạy ở chế độ debug để tự động tải lại khi có thay đổi code
    # host='0.0.0.0' cho phép truy cập từ các thiết bị khác trong cùng mạng
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)