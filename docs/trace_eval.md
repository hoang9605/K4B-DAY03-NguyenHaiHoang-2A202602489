# 📊 BÁO CÁO THU HOẠCH NGHIỆM THU BÀI LAB 3 (BƯỚC 3 — SUBMISSION ARTIFACT)

> **Họ và Tên Học viên:** Nguyễn Hải Hoàng
> **Mã Sinh Viên / Mã Học viên:** 2A202602489  
> **Chủ đề Lựa chọn:** Trợ lý Tư vấn Sức khỏe Vinmec: Tra cứu lịch làm việc bác sĩ chuyên khoa và đặt lịch khám bệnh.  

---

## 1. BẢNG CHẤM ĐIỂM AGENTIC FIT SCORING MATRIX (ĐÁNH GIÁ CHỦ ĐỀ)

| Tiêu chí Đánh giá | Mức độ (1 - 5) | Giải trình chi tiết lý do chọn điểm |
| :--- | :---: | :--- |
| **1. Multi-step Reasoning** | 4 / 5 | (1) xác định triệu chứng/nhu cầu → suy luận ra chuyên khoa phù hợp, (2) tra cứu danh sách bác sĩ thuộc chuyên khoa đó, (3) đối chiếu lịch trống theo khung giờ người dùng mong muốn, (4) xác nhận thông tin bệnh nhân (tên, SĐT, bảo hiểm), (5) chốt lịch và tạo phiếu hẹn |
| **2. Tool Interaction** | 5 / 5 | Hệ thống bắt buộc phải kết nối với hệ thống lõi bên ngoài: cơ sở dữ liệu lịch làm việc bác sĩ (HIS - Hospital Information System của Vinmec), module đặt lịch/booking engine, có thể cả hệ thống thanh toán/bảo hiểm và gửi SMS/email xác nhận |
| **3. Dynamic Decision** | 4 / 5 | Bước tiếp theo phụ thuộc rất nhiều vào kết quả quan sát được: nếu bác sĩ A không còn lịch trống ở khung giờ mong muốn → agent phải tự động đề xuất bác sĩ khác cùng chuyên khoa hoặc khung giờ thay thế; nếu chuyên khoa ban đầu không đúng với triệu chứng mô tả thêm → phải điều chỉnh lại tra cứu |
| **4. Long Horizon Goal** | 3 / 5 | Mục tiêu "đặt lịch khám thành công cho đúng người, đúng bác sĩ, đúng giờ" phải được giữ xuyên suốt qua nhiều lượt hội thoại, người dùng có thể đổi ý giữa chừng (đổi bác sĩ, đổi ngày), cung cấp thông tin rải rác qua nhiều tin nhắn, hoặc quay lại sau để xác nhận/hủy lịch. Agent cần duy trì trạng thái (state) của phiên đặt lịch cho đến khi hoàn tất |
| **TỔNG ĐIỂM AGENTIC FIT** | **16 / 20** | *Nếu tổng điểm > 12/20: Bài toán rất phù hợp triển khai Agentic System.* |

---

## 2. TRÍCH XUẤT KẾT QUẢ WATERFALL TRACE LOG (SAU KHI CHẠY TEST SUITE TRÊN API THẬT)

> ⚠️ **YÊU CẦU NGHIỆM THU:** Mở tệp `.env` điền `GEMINI_API_KEY` (hoặc `OPENAI_API_KEY`) để kết nối LLM thật trước khi thực thi `python src/app.py --all`. Bài nộp chỉ dùng Mock Offline Provider sẽ không đạt điểm nghiệm thực tế.

Dán 1 đoạn trích xuất log tiêu biểu từ file `docs/trace_waterfall.json` sinh ra từ phản hồi LLM API thật:

```json
[
  {
    "step": 1,
    "query": "Tôi tên Nguyễn Văn An, số điện thoại 0987654321, muốn đặt lịch khám với BS. Trần Văn Khỏe vào lúc 08:00 ngày 15/09/2026.",
    "action_type": "TOOL_EXECUTION",
    "tool_name": "book_appointment",
    "arguments": {
      "doctor_name": "BS. Trần Văn Khỏe",
      "phone_number": "0987654321",
      "patient_name": "Nguyễn Văn An",
      "datetime_str": "08:00 15/09/2026"
    },
    "observation": {
      "status": "SUCCESS",
      "booking_id": "VMC-4321-319",
      "patient_name": "Nguyễn Văn An",
      "doctor_name": "BS. Trần Văn Khỏe",
      "datetime": "08:00 15/09/2026",
      "phone_number": "0987654321",
      "message": "Đặt lịch khám thành công cho bệnh nhân Nguyễn Văn An với BS. Trần Văn Khỏe vào lúc 08:00 15/09/2026. Vinmec sẽ liên hệ xác nhận qua số 0987654321."
    },
    "latency_ms": 1711.52
  },
  {
    "step": 2,
    "query": "Tôi tên Nguyễn Văn An, số điện thoại 0987654321, muốn đặt lịch khám với BS. Trần Văn Khỏe vào lúc 08:00 ngày 15/09/2026.",
    "action_type": "FINAL_ANSWER",
    "thought": "Tổng hợp kết quả từ MCP Server thành công.",
    "output": "Đặt lịch khám thành công cho bệnh nhân Nguyễn Văn An với BS. Trần Văn Khỏe vào lúc 08:00 15/09/2026. Vinmec sẽ liên hệ xác nhận qua số 0987654321.",
    "latency_ms": 10.0
  }
]
```

---

## 3. TỔNG KẾT KẾT QUẢ NGHIỆM THU & NỘP BÀI

- [x] Đã điền API Key thật trong `.env` và xác nhận Agent chạy mượt mà trên LLM API thật (Gemini/OpenAI).
- **Tổng số Test Cases đã chạy thành công:** ___ / 5 test cases.
- **Số lượt gọi Tool qua MCP Server chính xác:** ___ lượt.
- **Kết quả đẩy Repo nộp bài:** [ ] Đã Commit và Push mã nguồn thành công lên GitHub cá nhân.

---

> ✅ **HOÀN TẤT NỘP BÀI:** Sao chép đường link GitHub Repository cá nhân của bạn và dán vào ô nộp bài trên hệ thống LMS VLearn để hoàn tất Bài Lab 3!
