import json
import subprocess
from typing import Dict, Any

class CursorMCP:
    def __init__(self):
        self.mcp_process = None
        self.start_mcp_server()

    def start_mcp_server(self):
        """MCP 서버를 시작합니다."""
        if self.mcp_process is None:
            self.mcp_process = subprocess.Popen(
                ["python", "src/run_mcp_server.py"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True
            )

    def call_tool(self, tool_name: str, params: Dict[str, Any]) -> str:
        """MCP 도구를 호출합니다."""
        if self.mcp_process is None:
            self.start_mcp_server()
        
        request = {
            "tool": tool_name,
            "params": params
        }
        self.mcp_process.stdin.write(json.dumps(request) + "\n")
        self.mcp_process.stdin.flush()
        response = self.mcp_process.stdout.readline()
        return json.loads(response)["result"]

# Cursor에서 사용할 수 있는 전역 인스턴스
cursor_mcp = CursorMCP()

def get_weather(location: str) -> str:
    """Get weather information for a location."""
    return cursor_mcp.call_tool("get_weather", {"location": location}) 