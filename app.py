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

# ✅ 기본 페이지 (GET 요청만 허용)
@app.route("/", methods=["GET"])
def home():
    return "✅ Flask 서버 실행 중! 카카오 챗봇과 연결됨!"

# ✅ 웹훅 엔드포인트 (POST 요청 허용)
@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # 카카오 챗봇에서 받은 데이터
        req_data = request.get_json()

        # JSON 데이터가 올바른지 확인
        if not req_data:
            raise ValueError("요청 데이터가 비어 있습니다.")

        user_message = req_data.get("userRequest", {}).get("utterance", "")

        if not user_message:
            raise ValueError("사용자 입력을 찾을 수 없습니다.")

        # Gemini API에 요청 보내기
        response = genai.generate_text(user_message)

        # Gemini 응답 확인
        if not response.result:
            raise ValueError("Gemini API 응답이 없습니다.")

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
        # 🔴 에러 발생 시 로그 출력
        print(f"🚨 오류 발생: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Flask 서버 실행
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
