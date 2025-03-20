import os
import json
import google.generativeai as genai
from flask import Flask, request, jsonify

# 로그 파일 경로
LOG_FILE = "log.txt"

def log_message(message):
    """로그 파일에 메시지 저장"""
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")
    print(message)  # 콘솔에도 출력

# 환경 변수에서 API 키 가져오기
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
log_message(f"Loaded GEMINI_API_KEY: {GEMINI_API_KEY}")

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
        log_message(f"Received data: {json.dumps(data, ensure_ascii=False)}")  # [로그] 요청 데이터 저장

        if "userRequest" not in data or "utterance" not in data["userRequest"]:
            log_message("Invalid request format")
            return jsonify({"error": "Invalid request format"}), 400
        
        user_input = data["userRequest"]["utterance"]  # 사용자의 발화 가져오기
        log_message(f"User Input: {user_input}")

        # Gemini API 호출
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(user_input)

        if not response or not hasattr(response, "text"):
            log_message("No response from Gemini API")
            return jsonify({"error": "No response from Gemini API"}), 500
        
        bot_reply = response.text.strip()
        log_message(f"Gemini Response: {bot_reply}")

        # 카카오 챗봇 응답 형식으로 변환
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
        error_message = f"Error occurred: {str(e)}"
        log_message(error_message)  # [로그] 에러 메시지 저장
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
