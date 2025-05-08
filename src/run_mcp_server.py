from mcp.mcp_api import run_server

if __name__ == "__main__":
    print("MCP 서버를 시작합니다...")
    run_server(transport="sse")  # SSE 방식으로 서버 실행 