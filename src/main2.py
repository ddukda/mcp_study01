from flask import Flask, render_template, request, session
from huggingface_hub import InferenceClient
import requests
import os
import json
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "ai_chat_secret_key")

# Hugging Face API Key
API_KEY = os.getenv("HUGGINGFACE_API_KEY")
if not API_KEY:
    raise ValueError("HUGGINGFACE_API_KEY environment variable is not set")

# 사용자 제공 검색 API 주소
SEARCH_API_URL = os.getenv("SEARCH_API_URL", "https://your-search-api.com/search")
SEARCH_TRIGGER = "검색:"
WEATHER_TRIGGER = "@get_weather"

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# MCP 프로세스 관리
mcp_process = None

def start_mcp_server():
    global mcp_process
    if mcp_process is None:
        mcp_process = subprocess.Popen(
            ["python", "src/run_mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True
        )

def call_mcp_tool(tool_name: str, params: dict) -> str:
    global mcp_process
    if mcp_process is None:
        start_mcp_server()
    
    request = {
        "tool": tool_name,
        "params": params
    }
    mcp_process.stdin.write(json.dumps(request) + "\n")
    mcp_process.stdin.flush()
    response = mcp_process.stdout.readline()
    return json.loads(response)["result"]

@app.route("/")
def home():
    if 'messages' not in session:
        session['messages'] = []
    return render_template("chat.html", messages=session['messages'])

@app.route("/api", methods=["POST"])
def ai_response():
    user_input = request.form.get("query")
    if not user_input:
        return render_template("chat.html", error="메시지를 입력하세요!", messages=session.get('messages', []))

    if 'messages' not in session:
        session['messages'] = []

    session['messages'].append({"role": "user", "content": user_input})

    # 검색 키워드가 포함되었는지 확인
    augmented_input = user_input
    if user_input.startswith(SEARCH_TRIGGER):
        query = user_input[len(SEARCH_TRIGGER):].strip()
        search_result = call_search_api(query)
        augmented_input += f"\n\n[검색 결과 요약]: {search_result}"
    elif user_input.startswith(WEATHER_TRIGGER):
        location = user_input[len(WEATHER_TRIGGER):].strip()
        try:
            weather_result = call_mcp_tool("get_weather", {"location": location})
            session['messages'].append({"role": "assistant", "content": weather_result})
            session.modified = True
            return render_template("chat.html", messages=session['messages'])
        except Exception as e:
            return render_template("chat.html", error=f"날씨 조회 오류: {str(e)}", messages=session.get('messages', []))

    # Hugging Face 클라이언트 생성
    client = InferenceClient(provider="cerebras", api_key=API_KEY)

    try:
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct",
            messages=[{"role": "user", "content": augmented_input}],
            max_tokens=512,
        )
        response = completion.choices[0].message.content

        session['messages'].append({"role": "assistant", "content": response})
        session.modified = True

        return render_template("chat.html", messages=session['messages'])
    except Exception as e:
        return render_template("chat.html", error=f"오류 발생: {str(e)}", messages=session.get('messages', []))

def call_search_api(query: str) -> str:
    try:
        response = requests.get(SEARCH_API_URL, params={"q": query}, timeout=5)
        if response.status_code == 200:
            return response.json().get("result", "검색 결과 없음")
        else:
            return f"검색 오류 (코드: {response.status_code})"
    except Exception as e:
        return f"검색 API 호출 실패: {str(e)}"

@app.route("/clear")
def clear_chat():
    session['messages'] = []
    return render_template("chat.html", messages=[])

if __name__ == "__main__":
    start_mcp_server()
    app.run(debug=True)
