"""
🔌 MODEL CONTEXT PROTOCOL (MCP) SERVER MODULE
Mô phỏng kiến trúc MCP Server (Client-Server Architecture) cung cấp công cụ chuẩn hóa.
Chủ đề: Trợ lý Tư vấn Sức khỏe Vinmec — Tra cứu lịch bác sĩ & Đặt lịch khám bệnh.
"""

import json
import sys
from typing import Dict, Any, List
from tools import TOOLS_SCHEMA, dispatch_tool_call

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


class MCPHealthServer:
    """
    Giả lập MCP Server tuân thủ chuẩn giao thức Model Context Protocol
    cho hệ thống Trợ lý Tư vấn Sức khỏe Vinmec.
    """
    def __init__(self, server_name: str = "vinmec-health-mcp-server"):
        self.server_name = server_name
        self.version = "2026.1.0"

    def list_tools(self) -> List[Dict[str, Any]]:
        """Trả về danh sách các Tools chuẩn giao thức MCP"""
        return TOOLS_SCHEMA

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        [TASK 2.1] HỌC VIÊN HOÀN THIỆN HÀM THỰC THI TOOL TRÊN MCP SERVER
        Thực thi request gọi Tool theo chuẩn MCP JSON-RPC
        """
        # 1. Gọi Tool Router để thực thi Tool tương ứng, nhận về chuỗi JSON kết quả
        raw_result = dispatch_tool_call(tool_name, arguments)

        # 2. Chuyển đổi chuỗi JSON kết quả thành Python Dictionary
        try:
            content = json.loads(raw_result)
        except (json.JSONDecodeError, TypeError) as e:
            content = {
                "status": "PARSE_ERROR",
                "error": f"Không thể phân giải kết quả Tool trả về: {str(e)}"
            }

        # 3. Đóng gói phản hồi theo chuẩn giao thức MCP JSON-RPC 2.0
        return {
            "jsonrpc": "2.0",
            "server": self.server_name,
            "tool": tool_name,
            "result": content
        }


if __name__ == "__main__":
    print("==========================================================")
    print("🔌 KIỂM THỬ ĐỘC LẬP MCP SERVER (vinmec-health-mcp-server)")
    print("==========================================================")

    server = MCPHealthServer()
    tools = server.list_tools()
    print(f"✅ Khởi tạo thành công MCP Server: {server.server_name} (Version: {server.version})")
    print(f"📦 Số lượng Tools công bố: {len(tools)}")

    # Kiểm tra trạng thái TODO 1.2 (Tool Schema)
    booking_tool = next((t for t in tools if t.get("name") == "book_appointment"), None)
    if booking_tool and not booking_tool.get("parameters", {}).get("properties"):
        print("⏳ [TODO 1.2]: Tool 'book_appointment' chưa được định nghĩa properties trong 'src/tools.py'.")
    else:
        print("✅ [TODO 1.2]: Tool 'book_appointment' đã có schema đầy đủ.")

    # Kiểm tra trạng thái TODO 2.1 (call_tool) — tra cứu lịch bác sĩ
    test_result = server.call_tool("doctor_schedule_query", {"specialty": "Tim mạch"})
    if not test_result:
        print("⏳ [TODO 2.1]: Hàm call_tool() đang trả về rỗng. Học viên hãy hoàn thiện TODO 2.1 trong 'src/mcp_server.py'!")
    else:
        print("✅ [TODO 2.1]: Test dispatch tool 'doctor_schedule_query' thành công:")
        print(f"   Phản hồi JSON-RPC: {json.dumps(test_result, ensure_ascii=False)}")

    # Test bổ sung: đặt lịch khám bệnh
    booking_result = server.call_tool("book_appointment", {
        "patient_name": "Nguyễn Văn An",
        "doctor_name": "BS. Trần Văn Khỏe",
        "datetime_str": "08:00 15/09/2026",
        "phone_number": "0987654321"
    })
    print("✅ Test dispatch tool 'book_appointment' thành công:")
    print(f"   Phản hồi JSON-RPC: {json.dumps(booking_result, ensure_ascii=False)}")