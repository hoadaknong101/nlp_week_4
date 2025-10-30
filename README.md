# Dự án: Ứng dụng Web "Multi-Purpose LLM Tool"

## 1. Tổng quan dự án

**Multi-Purpose LLM Tool** là một ứng dụng web full-stack được thiết kế để cung cấp một giao diện trực quan, đa năng cho người dùng tương tác với mô hình ngôn ngữ lớn (LLM) **Gemma** của Google. Thay vì bị giới hạn bởi các chức năng chat thông thường, ứng dụng này cho phép người dùng thực thi các tác vụ cụ thể, có cấu trúc trên một đoạn văn bản đầu vào.

**Mục tiêu chính:**
* Cung cấp một bộ công cụ AI mạnh mẽ (Tóm tắt, Dịch thuật, Phân tích Cảm xúc, Tạo Code, v.v.).
* Cho phép người dùng định nghĩa các tác vụ của riêng họ thông qua tính năng **"Chỉ thị Tùy chỉnh" (Custom Instruction)**.
* Cung cấp trải nghiệm người dùng hiện đại, responsive, và **song ngữ (Anh/Việt)**.
* Xây dựng trên một ngăn xếp công nghệ nhẹ, phổ biến và dễ triển khai (Flask, JavaScript thuần).

## 2. Kiến trúc giải pháp (Architecture)

Kiến trúc của dự án tuân theo mô hình 3 lớp (3-tier) cổ điển, tách biệt rõ ràng giữa giao diện người dùng, logic nghiệp vụ, và dịch vụ bên thứ ba.

### Luồng dữ liệu (Data Flow)

1.  **Người dùng (Frontend):** Người dùng nhập văn bản vào `<textarea>` và nhấp vào một nút tác vụ (ví dụ: "Tóm tắt").
2.  **JavaScript (`script.js`):**
    * Một sự kiện `click` được kích hoạt.
    * Hàm JavaScript lấy văn bản từ `<textarea>` và **chỉ thị (instruction)** được lập trình sẵn (ví dụ: "Summarize this text...").
    * Hiển thị **spinner** (vòng quay tải).
    * Sử dụng `fetch` API để gửi một yêu cầu `POST` đến endpoint `/process` của backend, đính kèm `text_input` và `task_instruction` trong thân (body) JSON.
3.  **Backend (Flask `app.py`):**
    * Endpoint `/process` nhận yêu cầu JSON.
    * Nó xác thực dữ liệu đầu vào.
    * Nó gọi hàm `call_gemma()` từ `llm_service.py`, truyền `user_text` và `instruction`.
4.  **Service Layer (`llm_service.py`):**
    * Hàm `call_gemma()` thực hiện **Prompt Engineering**: nó kết hợp `instruction` và `user_text` thành một prompt hoàn chỉnh.
    * Nó tải `GOOGLE_API_KEY` từ file `.env` (để bảo mật).
    * Nó khởi tạo `genai.GenerativeModel` và gọi `model.generate_content(prompt)`.
5.  **Google AI Studio (API):** Gemma xử lý prompt và trả về kết quả (dưới dạng đối tượng `response`).
6.  **Quay lại (Return Flow):**
    * `llm_service.py` trích xuất `response.text` và trả nó về cho `app.py`.
    * `app.py` đóng gói văn bản kết quả vào một JSON (ví dụ: `{"result": "..."}`) và trả về cho frontend.
    * `script.js` nhận phản hồi JSON, ẩn **spinner**, và hiển thị `data.result` vào `<div>` kết quả (`result-display`).

## 3. Giải thích Lựa chọn Công nghệ

* **Tại sao chọn Flask?**
    * **Nhẹ và Microservice:** Flask là một "micro-framework". Nó không yêu cầu cấu trúc dự án phức tạp hay các thư viện đi kèm. Điều này làm cho nó trở nên hoàn hảo để xây dựng các API đơn giản, nhanh chóng.
    * **Dễ cài đặt:** Chỉ cần `pip install Flask`.
    * **Linh hoạt:** Cung cấp các công cụ cơ bản (routing, request, response) và để lập trình viên tự quyết định phần còn lại, rất phù hợp cho một dự án demo cần sự rõ ràng.

* **Tại sao chọn Gemma (qua Google AI Studio)?**
    * **Mô hình mạnh mẽ:** Gemma là một họ các mô hình mở, tiên tiến từ Google.
    * **Dễ tích hợp:** Thư viện `google.generativeai` của Python cung cấp một giao diện rất sạch sẽ (`.configure()`, `.GenerativeModel()`, `.generate_content()`) để tương tác với API.
    * **Chi phí thấp/Miễn phí:** Google AI Studio cung cấp một bậc miễn phí (free tier) hào phóng, lý tưởng cho các dự án phát triển và demo cá nhân.

* **Tại sao chọn JavaScript thuần (Vanilla JS) với `fetch`?**
    * **Không cần Framework:** Đối với một ứng dụng một trang (SPA) đơn giản như thế này, việc sử dụng các framework lớn như React hay Vue là không cần thiết (overkill).
    * **Hiện đại:** `fetch` API là tiêu chuẩn web hiện đại để thực hiện các yêu cầu mạng, thay thế cho `XMLHttpRequest` cũ. Nó dựa trên `Promise`, cho phép sử dụng cú pháp `async/await` sạch sẽ, dễ đọc.

## 4. Giải thích chi tiết về "Prompt Engineering"

Đây là trái tim của ứng dụng. Sức mạnh của LLM không nằm ở model, mà ở cách chúng ta *hỏi* (prompt) nó.

Ứng dụng này không chỉ gửi văn bản thô đến LLM. Thay vào đó, nó **"ghép"** một **chỉ thị (instruction)** vào trước văn bản của người dùng.

**Công thức chung:**
`prompt = f"{instruction}\n\n---\n\n{user_text}"`

* `{instruction}`: Đây là chỉ thị chúng ta định nghĩa, cho LLM biết *phải làm gì*.
* `\n\n---\n\n`: Dấu phân cách rõ ràng. Điều này cực kỳ quan trọng, nó giúp LLM phân biệt đâu là mệnh lệnh và đâu là dữ liệu cần xử lý.
* `{user_text}`: Văn bản thô từ người dùng.

### Ví dụ về các Prompt được sử dụng

| Nút bấm | Chỉ thị (Instruction) trong `script.js` |
| --- | --- |
| **Summarize** | "Summarize this text in three clear and concise sentences." |
| **Generate Python** | "Based on the following description, write a Python code snippet. Provide only the code, wrapped in ```python ... ```. Do not include any explanatory text..." |
| **Format as JSON** | "Convert the following unstructured data or description into a valid JSON object. Ensure keys and string values are in double quotes." |
| **Analyze Sentiment** | "Analyze the sentiment of the following text. Respond with only one word: Positive, Negative, or Neutral." |

Bằng cách kiểm soát chặt chẽ các chỉ thị này (ví dụ: "Respond with *only one word*"), chúng ta có thể ép buộc LLM trả về kết quả có cấu trúc, đáng tin cậy thay vì một đoạn văn trò chuyện lan man.

## 5. Tính năng Sáng tạo (Điểm nhấn)

Các tính năng này được thiết kế để vượt qua yêu cầu cơ bản và đạt điểm tối đa (120/120).

### ⭐️ Tính năng 1: Chỉ thị Tùy chỉnh (Custom Instruction)

Đây là tính năng mạnh mẽ nhất của ứng dụng.

* **Vấn đề:** 8 nút bấm được lập trình sẵn bị giới hạn trong trí tưởng tượng của lập trình viên.
* **Giải pháp:** Thêm một ô `<input>` "Chỉ thị Tùy chỉnh" và nút "Run Custom".
* **Cách hoạt động:** Thay vì sử dụng một chỉ thị được lập trình sẵn từ `taskInstructions`, hàm `sendRequest()` sẽ lấy bất kỳ văn bản nào người dùng nhập vào ô `custom-instruction` và sử dụng nó làm `instruction`.
* **Tại sao nó mạnh mẽ?** Nó trao toàn bộ sức mạnh của Prompt Engineering cho người dùng. Họ có thể yêu cầu bất cứ điều gì:
    * "Dịch văn bản này sang tiếng Nhật."
    * "Kiểm tra các lỗi ngữ pháp trong email này."
    * "Biến đoạn văn này thành một bài thơ haiku."
    * "Giải thích đoạn code này từng dòng."

### ⭐️ Tính năng 2: Giao diện Song ngữ (Anh/Việt)

Điều này thể hiện sự chú ý đến trải nghiệm người dùng (UX) và kỹ thuật frontend phức tạp hơn.

* **Cách thực hiện:**
    1.  **HTML:** Mỗi phần tử văn bản (label, button) có các thuộc tính `data-en` và `data-vi` (ví dụ: `<button data-en="Summarize" data-vi="Tóm tắt">`).
    2.  **JavaScript:** Một biến trạng thái `currentLang` theo dõi ngôn ngữ.
    3.  Một từ điển `uiTranslations` chứa các chuỗi văn bản cho các phần tử đặc biệt (như `placeholder`).
    4.  Hàm `toggleLanguage()` lặp qua tất cả các phần tử `[data-en]`, đọc giá trị `dataset` tương ứng (`en` hoặc `vi`) và cập nhật `textContent` của chúng.
* **Điểm mấu chốt:** Logic của nút bấm *luôn* sử dụng `button.dataset.en` làm "key" để tra cứu chỉ thị API. Điều này tách biệt hoàn toàn ngôn ngữ hiển thị (UI) khỏi ngôn ngữ logic (API instruction).

## 6. Hạn chế và Hướng phát triển Tương lai

### Hạn chế hiện tại
* **Giới hạn Ngữ cảnh (Context Window):** Model Gemma có giới hạn về số lượng token (văn bản) đầu vào. Nếu người dùng dán một cuốn sách vào `<textarea>`, API sẽ thất bại.
* **Tốc độ:** Tốc độ phản hồi hoàn toàn phụ thuộc vào API của Google AI Studio. Các tác vụ phức tạp có thể mất vài giây.
* **Không có Lịch sử (Stateless):** Mỗi lần nhấp chuột là một yêu cầu API độc lập. Ứng dụng không "nhớ" các cuộc hội thoại trước đó (ví dụ: người dùng không thể hỏi "Hãy tóm tắt nó ngắn hơn nữa").
* **Rate Limiting:** Bậc miễn phí của API có thể có giới hạn về số lượng yêu cầu mỗi phút.

### Hướng phát triển Tương lai
* **Chế độ Chat (Context-aware):** Thêm một tab "Chat" để duy trì lịch sử hội thoại, cho phép các câu hỏi tiếp theo.
* **Lưu Lịch sử:** Sử dụng `localStorage` của trình duyệt để lưu các kết quả trước đó cho người dùng.
* **Hỗ trợ Nhiều Model:** Thêm một menu thả xuống (`<select>`) để người dùng chọn giữa các model khác nhau (ví dụ: Gemma, Gemini Pro).
* **Xử lý Streaming:** Thay vì chờ toàn bộ phản hồi, hãy sử dụng `model.generate_content(..., stream=True)` và hiển thị kết quả từng từ một (kiểu "gõ máy chữ"), cải thiện trải nghiệm người dùng (UX) rõ rệt.
