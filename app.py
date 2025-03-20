from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

# 환경 변수에서 Gemini API 키 가져오기
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json  # 카카오 챗봇에서 받은 JSON 데이터
        user_message = data['userRequest']['utterance']  # 사용자의 입력값 추출

        # 제미나이 API 호출
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(user_message)

        # 챗봇 응답 JSON 형식으로 변환
        kakao_response = {
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": response.text,  # 제미나이 응답 넣기
                            "extra": {}
                        }
                    }
                ],
                "quickReplies": []
            }
        }

        return jsonify(kakao_response)  # 카카오 챗봇에 응답 보내기

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # 에러 발생 시 500 응답

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
