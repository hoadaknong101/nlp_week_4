// Đợi cho đến khi toàn bộ nội dung trang (DOM) được tải xong
document.addEventListener("DOMContentLoaded", () => {
  // --- 1. Lấy các phần tử (Elements) ---
  const textInput = document.getElementById("text-input");
  // Chúng ta nhắm vào <code> bên trong <div> để dễ dàng cập nhật textContent
  const resultDisplayCode = document
    .getElementById("result-display")
    .querySelector("code");
  const loadingSpinner = document.getElementById("loading-spinner");
  const langToggleButton = document.getElementById("lang-toggle");
  const customInstructionInput = document.getElementById("custom-instruction");
  const customTaskButton = document.getElementById("custom-task-btn");
  const taskButtons = document.querySelectorAll(".task-btn"); // Lấy tất cả nút tác vụ

  // --- 2. Quản lý Trạng thái (State) ---
  let currentLang = "en"; // Ngôn ngữ mặc định là tiếng Anh

  // Từ điển chứa các chỉ thị (instruction) gửi đến API.
  // Các key (ví dụ: 'Summarize') phải khớp với giá trị 'data-en' trong HTML.
  // Điều này đảm bảo chúng ta luôn gửi chỉ thị bằng tiếng Anh cho backend,
  // bất kể ngôn ngữ UI đang hiển thị là gì.
  const taskInstructions = {
    Summarize: "Summarize this text in three clear and concise sentences.",
    "Translate to French": "Translate the following text to French.",
    "Explain Like I'm 5":
      "Explain the following concept or text as if I am 5 years old. Use simple words and analogies.",
    "Extract Keywords":
      "Extract the top 5-7 most important keywords from this text. Return them as a comma-separated list.",
    "Generate Python Code":
      "Based on the following description, write a Python code snippet. Provide only the code, wrapped in ```python ... ```. Do not include any explanatory text before or after the code block.",
    "Analyze Sentiment":
      "Analyze the sentiment of the following text. Respond with only one word: Positive, Negative, or Neutral.",
    "Format as JSON":
      "Convert the following unstructured data or description into a valid JSON object. Ensure keys and string values are in double quotes.",
    "Find 5 Related Questions":
      "Based on the following text, generate 5 relevant and insightful follow-up questions a user might ask next.",
  };

  // Từ điển chứa các chuỗi văn bản (text strings) cho UI song ngữ
  const uiTranslations = {
    en: {
      toggleLang: "Tiếng Việt",
      textInputLabel: "Your Text Input:",
      textInputPlaceholder:
        "Type or paste your text here... For code generation, describe the code you want.",
      taskLabel: "Select a Pre-defined Task:",
      customLabel: "Or, use a Custom Instruction:",
      customPlaceholder:
        "e.g., 'Translate this to Japanese' or 'Check this text for grammar errors'",
      customButton: "Run Custom",
      resultLabel: "Result:",
      errorPrefix: "Error: ",
      emptyInputError:
        "Please enter some text in the input area before submitting.",
      emptyCustomInstructionError: "Please enter a custom instruction.",
    },
    vi: {
      toggleLang: "English",
      textInputLabel: "Nội dung của bạn:",
      textInputPlaceholder:
        "Nhập hoặc dán văn bản của bạn tại đây... Để tạo code, hãy mô tả code bạn muốn.",
      taskLabel: "Chọn một tác vụ có sẵn:",
      customLabel: "Hoặc, dùng chỉ thị tùy chỉnh:",
      customPlaceholder:
        "Ví dụ: 'Dịch sang tiếng Nhật' hoặc 'Kiểm tra lỗi ngữ pháp cho văn bản này'",
      customButton: "Chạy Tùy chỉnh",
      resultLabel: "Kết quả:",
      errorPrefix: "Lỗi: ",
      emptyInputError: "Vui lòng nhập nội dung vào ô văn bản trước khi gửi.",
      emptyCustomInstructionError: "Vui lòng nhập chỉ thị tùy chỉnh.",
    },
  };

  // --- 3. Hàm Chức năng Cốt lõi (Core Functions) ---

  /**
   * Hàm chính để gửi yêu cầu đến backend.
   * @param {string} instruction - Chỉ thị (prompt) để gửi cho LLM.
   */
  async function sendRequest(instruction) {
    const text = textInput.value;

    // --- Xác thực đầu vào phía Client ---
    if (!text.trim()) {
      alert(uiTranslations[currentLang].emptyInputError);
      return;
    }

    // --- Cập nhật UI: Bắt đầu tải ---
    loadingSpinner.style.display = "flex"; // Hiển thị spinner
    resultDisplayCode.textContent = ""; // Xóa kết quả cũ
    document.getElementById("result-display").style.display = "none"; // Ẩn khung kết quả

    try {
      // --- Gọi API (Fetch) ---
      const response = await fetch("/process", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text_input: text,
          task_instruction: instruction,
        }),
      });

      // --- Cập nhật UI: Dừng tải ---
      loadingSpinner.style.display = "none";
      document.getElementById("result-display").style.display = "block"; // Hiển thị lại khung kết quả

      if (!response.ok) {
        // Xử lý lỗi HTTP (ví dụ: lỗi 500 từ server, lỗi 400 do request sai)
        const errorData = await response.json();
        throw new Error(
          errorData.error || `HTTP error! Status: ${response.status}`
        );
      }

      // Lấy dữ liệu JSON từ phản hồi thành công
      const data = await response.json();

      // --- Cập nhật UI: Hiển thị kết quả ---
      resultDisplayCode.textContent = data.result;
    } catch (error) {
      // --- Cập nhật UI: Xử lý lỗi (ví dụ: mạng, server) ---
      loadingSpinner.style.display = "none";
      document.getElementById("result-display").style.display = "block"; // Hiển thị khung để báo lỗi
      console.error("Fetch Error:", error);
      // Hiển thị lỗi cho người dùng
      resultDisplayCode.textContent = `${uiTranslations[currentLang].errorPrefix}${error.message}`;
    }
  }

  /**
   * Chuyển đổi ngôn ngữ của UI giữa Tiếng Anh (en) và Tiếng Việt (vi).
   */
  function toggleLanguage() {
    // Chuyển đổi ngôn ngữ hiện tại
    currentLang = currentLang === "en" ? "vi" : "en";

    const langData = uiTranslations[currentLang];

    // Cập nhật tất cả các phần tử có thuộc tính [data-en]
    document.querySelectorAll("[data-en]").forEach((el) => {
      const key = currentLang; // 'en' hoặc 'vi'
      el.textContent = el.dataset[key];
    });

    // Cập nhật văn bản của nút chuyển đổi ngôn ngữ
    langToggleButton.textContent = langData.toggleLang;

    // Cập nhật các placeholder (không dùng data-vi/data-en được)
    textInput.placeholder = langData.textInputPlaceholder;
    customInstructionInput.placeholder = langData.customPlaceholder;
  }

  // --- 4. Gắn các Trình nghe Sự kiện (Event Listeners) ---

  // Gắn sự kiện cho nút chuyển đổi ngôn ngữ
  langToggleButton.addEventListener("click", toggleLanguage);

  // Gắn sự kiện cho tất cả các nút tác vụ (handleTaskClick)
  taskButtons.forEach((button) => {
    button.addEventListener("click", () => {
      // Lấy CHỈ THỊ TIẾNG ANH từ thuộc tính 'data-en'
      // Đây là chìa khóa để UI song ngữ hoạt động
      const enInstructionKey = button.dataset.en;

      // Lấy chỉ thị đầy đủ từ từ điển 'taskInstructions'
      const instruction = taskInstructions[enInstructionKey];

      if (instruction) {
        sendRequest(instruction); // Gửi yêu cầu với chỉ thị tiếng Anh
      } else {
        console.error("Không tìm thấy chỉ thị cho key:", enInstructionKey);
      }
    });
  });

  // Gắn sự kiện cho nút chạy tác vụ tùy chỉnh (handleCustomClick)
  customTaskButton.addEventListener("click", () => {
    const customInstruction = customInstructionInput.value;

    // Xác thực đầu vào cho ô tùy chỉnh
    if (!customInstruction.trim()) {
      alert(uiTranslations[currentLang].emptyCustomInstructionError);
      return;
    }

    // Gửi yêu cầu bằng chỉ thị tùy chỉnh của người dùng
    sendRequest(customInstruction);
  });

  // --- 5. Khởi tạo (Initialization) ---
  // Ngay khi tải trang, gọi toggleLanguage() để đặt ngôn ngữ mặc định (Tiếng Anh)
  // Hoặc nếu bạn muốn mặc định là Tiếng Việt, chỉ cần đổi 'currentLang = 'en'' thành 'vi' ở trên.
  // Chúng ta sẽ gọi nó một lần để đảm bảo các placeholder được đặt đúng.
  toggleLanguage(); // Đổi sang 'vi'
  toggleLanguage(); // Đổi lại 'en' (để thiết lập trạng thái ban đầu)
});
