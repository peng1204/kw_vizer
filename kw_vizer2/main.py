import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from engine.query_router import answer_query

def run_chatbot(user_input: str, user_id: str = "kim") -> str:
    return answer_query(user_input, user_id)

# 로컬 테스트용 예시
if __name__ == "__main__":
    while True:
        query = input("질문 입력: ")
        if query.strip().lower() in ["exit", "quit"]:
            break
        print(run_chatbot(query))
