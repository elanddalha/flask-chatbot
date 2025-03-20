from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# OpenAI API 클라이언트 생성
client = openai.OpenAI(api_key="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
")  # 여기에 OpenAI API 키 입력

@app.route('/')
def home():
    return "Chatbot Webhook is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    user_message = data['userRequest']['utterance']  # 사용자가 보낸 메시지

    # 최신 OpenAI API 호출 방식 적용
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}]
    )

    bot_message = response.choices[0].message.content  # ChatGPT의 응답 추출

    # 카카오톡 챗봇 응답 형식
    kakao_response = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": bot_message
                    }
                }
            ]
        }
    }

    return jsonify(kakao_response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
