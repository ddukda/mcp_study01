from flask import Flask, render_template, request
from huggingface_hub import InferenceClient
import requests

app = Flask(__name__)

# OpenAI API Key
OPENAI_API_KEY = ""

@app.route("/")
def home():
  return render_template("home.html")

@app.route("/api", methods=["POST"])
def ai_response():
  user_input = request.form.get("query")
  if not user_input:
    return render_template("result.html", error="질문을 입력하세요!")

  client = InferenceClient(
    provider="cerebras",
    api_key=OPENAI_API_KEY,
  )
  completion = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct",
    messages=[
      {
        "role": "user",
        "content": user_input
      }
    ],
    max_tokens=512,
  )
  print(completion)
  response = completion.choices[0].message.content
  return render_template("result.html", result=response, query=user_input)


if __name__ == "__main__":
  app.run(debug=True)







