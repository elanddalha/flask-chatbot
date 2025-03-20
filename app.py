import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify

# Render 환경 변수에서 Google Gemini API 키 가져오기
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# API 키 설정
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY가 설정되지 않았습니다. Render 환경 변수에서 설정하세요.")

genai.configure(api_key=GEMINI_API_KEY)

# Flask 앱 생성
app = Flask(__name__)

# ✅ 기본 페이지 추가 ("/" 경로)
@app.route("/")
def home():
    return "✅ Flask 서버 실행 중! 카카오 챗봇과 연결됨!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # 카카오 챗봇에서 받은 데이터
        req_data = request.get_json()
        user_message = req_data["userRequest"]["utterance"]  # 사용자 입력

        # Gemini API에 요청 보내기
        response = genai.generate_text(user_message)

        # 카카오 챗봇 응답 형식 변환
        kakao_response = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": response.result,
                            "extra": {}
                        }
                    }
                ],
                "quickReplies": []
            }
        }

        return jsonify(kakao_response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Flask 서버 실행
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
