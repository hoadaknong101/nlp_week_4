from flask import Flask, render_template, request, jsonify, session
import uuid
import llm_service  # Import file logic LLM riêng biệt
import os # Dùng để chạy app

# Khởi tạo ứng dụng Flask
app = Flask(__name__)
app.secret_key = 'mot_key_bi_mat_rat_an_toan' # BẮT BUỘC để sử dụng session

@app.route('/')
def index():
    """
    Route chính, phục vụ file 'index.html' cho frontend.
    """
    return render_template('index.html')

@app.route('/api/model-table/<lang>')
def model_table_partial(lang):
    # Tên template được sử dụng trong render_template phải khớp với tên file
    return render_template(f'model-table-{lang}.html')

# Route để tải lịch sử
@app.route('/api/history', methods=['GET'])
def get_history():
    # Lấy danh sách lịch sử (hoặc danh sách rỗng nếu chưa có)
    history = session.get('history', [])
    # Chỉ gửi các trường cần thiết ra Front-end
    return jsonify([
        {'id': item['id'], 'summary': item['summary'], 'prompt': item['prompt'], 'result': item['result']}
        for item in history
    ])

# Route để lưu một tương tác mới
def save_interaction(prompt, result, model):
    # Tạo một mục tương tác mới
    new_interaction = {
        'id': str(uuid.uuid4()), # ID duy nhất
        'prompt': prompt,
        # Lấy một đoạn ngắn của prompt để làm tiêu đề lịch sử
        'summary': prompt[:30] + '...' if len(prompt) > 30 else prompt,
        'result': result,
        'model': model
    }
    
    # Lấy history từ session, nếu chưa có thì tạo danh sách rỗng
    history = session.get('history', [])
    
    # Thêm mục mới vào đầu danh sách (mục mới nhất nằm trên cùng)
    history.insert(0, new_interaction)
    
    # Giới hạn số lượng mục (ví dụ: 10 mục gần nhất)
    session['history'] = history[:10]
    session.modified = True # Đánh dấu session đã thay đổi

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
        if not data or 'text_input' not in data or 'task_instruction' not in data or 'model' not in data:
            # Nếu thiếu dữ liệu, trả về lỗi 400 Bad Request
            return jsonify({"error": "Đầu vào không hợp lệ. 'text_input', 'task_instruction', và 'model' là bắt buộc."}), 400

        user_text = data['text_input']
        instruction = data['task_instruction']
        model = data['model']

        # --- Gọi Service Layer ---
        # Chuyển dữ liệu sang llm_service để xử lý (tách biệt logic)
        print(f"DEBUG: Nhận yêu cầu: text='{user_text[:20]}...', instruction='{instruction}', model='{model}'")
        result_text = llm_service.call_llm(user_text, instruction, model)

        save_interaction(user_text, result_text, model)

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