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
    """서버 정상 작동 확인"""
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
        
        user_input = data["userRequest"]["utterance"]  # 사용자의 질문 가져오기
        log_message(f"User Input: {user_input}")

        # ✅ **Gemini API 호출 (이랜드 퇴직연금 상담 프롬프트 적용)**
        api_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": (
                                "너는 이랜드 임직원들을 위한 퇴직연금 상담 챗봇이야. "
                                "이랜드는 퇴직연금 DC형을 운영하고 있어. "
                                "그래서 너는 퇴직연금 전문상담가이고 공손하고 예의바른 존댓말을 유지해. "
                                "이모티콘은 사용하지 말고, 답변은 간결하게 해. 500자를 넘지 말아줘. "
                                "'퇴직연금'과 '투자' 관련 답만 하면 되고, 그 외의 질문에는 답변하지 않아도 돼. 예를 들어, '몇살이야?, 너 누구야?' 같은 질문에는 '퇴직연금과 투자 관련된 질문을 해주세요'라고 답변해"
                                "일반적인 질문을 하더라도 '퇴직연금'과 '투자'관련 질문으로 인식해줘. 예를 들어 '가입 어떻게 해?'라는 질문이 들어오면 '퇴직연금 가입 어떻게 해?'로 이해하면 돼"
                                "답변하기 어려운 내용은 이랜드투자자문에 전화하거나 메일 상담을 안내해. "
                                "이랜드 투자자문 메일주소는 IRP@eland.co.kr이야."
                                "이랜드는 12월에만 퇴직연금 신규가입 가능해"
                                "이랜드 임직원은 퇴직연금DC형에만 가입 가능해. DB형은 운영하고 있지 않아."
                            )
                        }
                    ]
                },
                {"parts": [{"text": user_input}]}
            ]
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

        # ✅ **카카오 챗봇 응답 형식 변환**
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
        with open(LOG_FILE, "r", encoding="utf-8") as log_file:
            return "<pre>" + log_file.read() + "</pre>"
    except Exception as e:
        return f"Error reading logs: {str(e)}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
