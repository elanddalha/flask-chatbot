import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify

# 환경 변수에서 API 키 가져오기
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Gemini API 설정
genai.configure(api_key=GEMINI_API_KEY)

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Gemini Chatbot is Running!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # 클라이언트에서 보낸 JSON 데이터 받기
        data = request.get_json()
        user_input = data["userRequest"]["utterance"]  # 카카오톡에서 사용자의 질문 가져오기

        # Gemini API 호출
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(user_input)
        
        # 응답이 없을 경우 예외 처리
        if not response:
            return jsonify({"error": "No response from Gemini API"}), 500
        
        # Gemini의 응답 텍스트 가져오기
        bot_reply = response.text.strip()

        # 카카오 챗봇 응답 형식에 맞게 변환
        kakao_response = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": bot_reply
                        }
                    }
                ]
            }
        }

        return jsonify(kakao_response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
