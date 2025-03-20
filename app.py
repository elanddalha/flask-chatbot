import os
from flask import Flask, request, jsonify
import openai
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

app = Flask(__name__)

# 환경 변수에서 OpenAI API 키 가져오기
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

@app.route('/')
def home():
    return "Chatbot Webhook is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    user_message = data['userRequest']['utterance']  # 사용자가 보낸 메시지

    # OpenAI API 호출
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}]
    )

    bot_message = response.choices[0].message.content  # ChatGPT 응답 추출

    # 카카오톡 챗봇 응답 형식 적용
    kakao_response = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": bot_message,
                        "extra": {}  # 필요한 경우 추가 정보 입력 가능
                    }
                }
            ],
            "quickReplies": []  # 빠른 응답 버튼이 필요하면 추가 가능
        }
    }

    return jsonify(kakao_response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
