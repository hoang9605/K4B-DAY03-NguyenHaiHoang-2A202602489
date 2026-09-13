"""
🏥 TOOLS MODULE — TRỢ LÝ TƯ VẤN SỨC KHỎE VINMEC
Chủ đề: Tra cứu lịch làm việc bác sĩ chuyên khoa và đặt lịch khám bệnh.
"""

import json
from typing import Dict, Any

# ==============================================================================
# 1. KHAI BÁO TOOL SCHEMAS CHUẨN NATIVE JSON SCHEMA (TASK 1.2)
# ==============================================================================

TOOLS_SCHEMA = [
    # Tool 1: Đã được định nghĩa mẫu sẵn cho Học viên tham khảo
    {
        "name": "doctor_schedule_query",
        "description": "Tra cứu lịch làm việc của bác sĩ chuyên khoa tại hệ thống Bệnh viện Vinmec theo chuyên khoa hoặc tên bác sĩ.",
        "parameters": {
            "type": "object",
            "properties": {
                "specialty": {
                    "type": "string",
                    "description": "Tên chuyên khoa cần tra cứu (ví dụ: 'Tim mạch', 'Nhi khoa', 'Da liễu')"
                },
                "doctor_name": {
                    "type": "string",
                    "description": "Tên bác sĩ cụ thể cần tra cứu lịch làm việc (ví dụ: 'BS. Trần Văn Khỏe'). Có thể để trống nếu chỉ tra theo chuyên khoa."
                }
            },
            "required": ["specialty"]
        }
    },

    # --------------------------------------------------------------------------
    # TODO 1.2: HỌC VIÊN HOÀN THIỆN TOOL SCHEMA CHO 'book_appointment'
    # 🎯 YÊU CẦU THIẾT KẾ SCHEMA (JSON SCHEMA STANDARD):
    # 1. Tool dùng để đặt lịch khám bệnh với bác sĩ chuyên khoa tại Vinmec.
    # 2. Thiết kế các tham số (properties) để LLM trích xuất:
    #    - patient_name (string): Họ tên bệnh nhân đặt khám
    #    - doctor_name (string): Tên bác sĩ muốn khám
    #    - datetime_str (string): Thời gian khám mong muốn (ví dụ: '09:00 20/09/2026')
    #    - phone_number (string): Số điện thoại liên hệ của bệnh nhân
    # 3. Khai báo danh sách các trường bắt buộc (required).
    # --------------------------------------------------------------------------
    {
        "name": "book_appointment",
        "description": "Đặt lịch khám bệnh với bác sĩ chuyên khoa tại hệ thống Bệnh viện Vinmec.",
        "parameters": {
            "type": "object",
            "properties": {
                "patient_name": {
                    "type": "string",
                    "description": "Họ tên đầy đủ của bệnh nhân cần đặt lịch khám (ví dụ: 'Nguyễn Văn An')"
                },
                "doctor_name": {
                    "type": "string",
                    "description": "Tên bác sĩ chuyên khoa mà bệnh nhân muốn đặt lịch khám (ví dụ: 'BS. Trần Văn Khỏe')"
                },
                "datetime_str": {
                    "type": "string",
                    "description": "Thời gian khám mong muốn, định dạng 'HH:MM DD/MM/YYYY' (ví dụ: '09:00 20/09/2026')"
                },
                "phone_number": {
                    "type": "string",
                    "description": "Số điện thoại liên hệ của bệnh nhân để xác nhận lịch hẹn (ví dụ: '0987654321')"
                }
            },
            "required": ["patient_name", "doctor_name", "datetime_str", "phone_number"]
        }
    }
]

# ==============================================================================
# 2. MÔ PHỎNG DỮ LIỆU & HÀM THỰC THI TOOL (EXECUTION LAYER)
# ==============================================================================

MOCK_DATABASE = {
    "Tim mạch": [
        {"doctor_name": "BS. Trần Văn Khỏe", "room": "P.302 - Tòa A", "available_slots": ["08:00 15/09/2026", "09:30 15/09/2026", "14:00 16/09/2026"]},
        {"doctor_name": "TS.BS Lê Thị Hòa", "room": "P.305 - Tòa A", "available_slots": ["10:00 15/09/2026", "15:00 17/09/2026"]}
    ],
    "Nhi khoa": [
        {"doctor_name": "BS. Phạm Thị Mai", "room": "P.101 - Tòa B", "available_slots": ["08:30 15/09/2026", "13:30 16/09/2026"]}
    ],
    "Da liễu": [
        {"doctor_name": "BS. Ngô Quang Huy", "room": "P.210 - Tòa C", "available_slots": ["09:00 18/09/2026", "16:00 18/09/2026"]}
    ]
}


def execute_doctor_schedule_query(specialty: str, doctor_name: str = "") -> str:
    """Thực thi tra cứu lịch làm việc bác sĩ theo chuyên khoa (và tên bác sĩ nếu có)."""
    specialty_key = specialty.strip()
    doctors = MOCK_DATABASE.get(specialty_key)

    if not doctors:
        return json.dumps({
            "status": "NOT_FOUND",
            "message": f"Không tìm thấy dữ liệu lịch làm việc cho chuyên khoa '{specialty}'"
        }, ensure_ascii=False)

    if doctor_name:
        matched = [d for d in doctors if doctor_name.strip().lower() in d["doctor_name"].lower()]
        if not matched:
            return json.dumps({
                "status": "NOT_FOUND",
                "message": f"Không tìm thấy bác sĩ '{doctor_name}' trong chuyên khoa '{specialty}'"
            }, ensure_ascii=False)
        doctors = matched

    return json.dumps({
        "status": "SUCCESS",
        "specialty": specialty,
        "doctors": doctors
    }, ensure_ascii=False)


def execute_book_appointment(patient_name: str, doctor_name: str, datetime_str: str, phone_number: str) -> str:
    """Thực thi đặt lịch khám bệnh với bác sĩ chuyên khoa."""
    return json.dumps({
        "status": "SUCCESS",
        "booking_id": f"VMC-{phone_number[-4:]}-{hash(datetime_str) % 1000}",
        "patient_name": patient_name,
        "doctor_name": doctor_name,
        "datetime": datetime_str,
        "phone_number": phone_number,
        "message": f"Đặt lịch khám thành công cho bệnh nhân {patient_name} với {doctor_name} vào lúc {datetime_str}. Vinmec sẽ liên hệ xác nhận qua số {phone_number}."
    }, ensure_ascii=False)


# Router gọi tool thực tế
TOOL_ROUTER = {
    "doctor_schedule_query": execute_doctor_schedule_query,
    "book_appointment": execute_book_appointment
}


def dispatch_tool_call(tool_name: str, arguments: Dict[str, Any]) -> str:
    """Hàm trung chuyển thực thi tool"""
    if tool_name in TOOL_ROUTER:
        try:
            return TOOL_ROUTER[tool_name](**arguments)
        except Exception as e:
            return json.dumps({"status": "EXECUTION_ERROR", "error": str(e)}, ensure_ascii=False)
    return json.dumps({"status": "UNKNOWN_TOOL", "error": f"Tool '{tool_name}' không tồn tại!"}, ensure_ascii=False)