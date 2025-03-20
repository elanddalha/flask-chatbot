import os
import json
import requests
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

# Flask 앱 생성
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

        # ✅ Gemini API 호출
        api_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": user_input}]}]
        }

        response = requests.post(api_url, headers=headers, json=payload)
        log_message(f"Gemini API Response: {response.text}")

        # API 응답 확인
        if response.status_code != 200:
            error_message = f"Gemini API Error: {response.status_code} - {response.text}"
            log_message(error_message)
            return jsonify({"error": error_message}), response.status_code

        response_data = response.json()
        bot_reply = response_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "응답을 생성할 수 없습니다.")

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

# ✅ 로그 확인 엔드포인트 추가
@app.route("/logs", methods=["GET"])
def get_logs():
    """log.txt 파일 내용을 확인하는 엔드포인트"""
    try:
        with open("log.txt", "r", encoding="utf-8") as log_file:
            return "<pre>" + log_file.read() + "</pre>"
    except Exception as e:
        return f"Error reading logs: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
