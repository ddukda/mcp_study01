import asyncio
import json
from typing import Dict, Any, Callable, Awaitable

class MCPTool:
    def __init__(self, name: str, func: Callable[..., Awaitable[str]]):
        self.name = name
        self.func = func

class MCP:
    def __init__(self, name: str):
        self.name = name
        self.tools: Dict[str, MCPTool] = {}
        self.context = {}

    def tool(self, name: str = None):
        def decorator(func: Callable[..., Awaitable[str]]):
            tool_name = name or func.__name__
            self.tools[tool_name] = MCPTool(tool_name, func)
            return func
        return decorator

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        if "tool" not in request:
            return {"error": "No tool specified"}

        tool_name = request["tool"]
        if tool_name not in self.tools:
            return {"error": f"Tool {tool_name} not found"}

        tool = self.tools[tool_name]
        try:
            result = await tool.func(**request.get("params", {}))
            return {"result": result}
        except Exception as e:
            return {"error": str(e)}

    async def run(self, transport: str = "stdio"):
        if transport == "stdio":
            while True:
                try:
                    line = await asyncio.get_event_loop().run_in_executor(None, input)
                    request = json.loads(line)
                    response = await self.handle_request(request)
                    print(json.dumps(response))
                except EOFError:
                    break
                except Exception as e:
                    print(json.dumps({"error": str(e)}))

# MCP 인스턴스 생성
mcp = MCP("weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    # 항상 맑음으로 리턴한다.
    # 실제로는 api를 조회하여 결과를 가져오게 하면 된다.
    return f"{location}은 항상 맑아요~~"

def run_server(transport: str = "stdio"):
    """MCP 서버를 실행합니다."""
    asyncio.run(mcp.run(transport))
