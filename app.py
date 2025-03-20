import os
from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# Render에서 설정한 환경 변수 사용 (GitHub에는 API 키 저장 ❌)
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
