from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

# OpenAI API 키 설정
openai.api_key = "YOUR_OPENAI_API_KEY"  # OpenAI API 키 입력

@app.route('/')
def home():
    return "Chatbot Webhook is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    user_message = data['userRequest']['utterance']  # 사용자가 보낸 메시지

    # OpenAI ChatGPT API 호출
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_message}]
    )
    bot_message = response['choices'][0]['message']['content']

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
