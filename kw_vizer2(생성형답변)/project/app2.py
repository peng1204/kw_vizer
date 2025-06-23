# ✅ 현재 파일 위치를 모듈 import 경로에 추가
import sys
import os
sys.path.append(os.path.dirname(__file__))  # ← 이 줄 추가!

from flask import Flask, request, jsonify, render_template
from chatbot_engine2 import answer_query  # ✅ 변경된 경로 반영

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        class_number = data.get("class_number")
        password = data.get("password")

        users = {
            "202501": {"password": "1234", "name": "김브티"},
            "202502": {"password": "1234", "name": "홍데사"},
        }

        if class_number in users:
            user = users[class_number]
            if user["password"] == password:
                return jsonify({
                    "success": True,
                    "class_number": class_number,
                    "name": user["name"]
                })

        return jsonify({"success": False, "message": "학번 또는 비밀번호가 틀렸습니다."}), 401

    except Exception as e:
        print("❌ 로그인 오류:", e)
        return jsonify({"success": False, "message": "서버 오류가 발생했습니다."}), 500

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/chat")
def chat_page():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat_api():
    try:
        data = request.get_json()
        user_input = data.get("message", "")
        class_number = data.get("class_number", "")
        function = data.get("function", "lecture_search")  # ✅ 기능명 전달 (기본: lecture_search)

        user_id = "kim" if class_number == "202501" else "hong"
        collection_name = f"{function}_{user_id}" if function == "lecture_search" else function

        # 응답 생성
        answer = answer_query(user_id=user_id, user_input=user_input, collection_name=collection_name)
        return jsonify({"response": answer})

    except Exception as e:
        print("❌ 챗봇 오류:", e)
        return jsonify({"response": "챗봇 처리 중 오류가 발생했습니다."}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5006)