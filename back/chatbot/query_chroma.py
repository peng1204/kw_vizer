#back/chatbot/query_chroma.py

import sys, re
import os
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from utils import filter_lectures_by_team #함수 추가하면 됨

sys.stdout.reconfigure(encoding='utf-8')  # ✅ Python 3.7 이상에서 사용 가능

user_input = sys.argv[1]
openai = OpenAI(api_key="sk-...")

# ✅ 팀플 조건 파악
team_condition = None
if any(k in user_input for k in ["팀플 없는", "팀플이 없는", "조별과제 없는"]):
    team_condition = "없음"
elif any(k in user_input for k in ["팀플 보통", "팀플이 보통"]):
    team_condition = "보통"
elif any(k in user_input for k in ["팀플 많은", "팀플이 많은"]):
    team_condition = "많은"

# ✅ 개수 파악 (ex: 3개만 추천해줘)
match = re.search(r'(\d+)\s*개', user_input)
count = int(match.group(1)) if match else None

# ✅ 팀플 관련 요청이면 룰 기반 처리
if team_condition:
    filtered_lectures = filter_lectures_by_team(
        ["./data/kw_chatbot_data - 강의 평점.json"],
        team_condition
    )

    if not filtered_lectures:
        print(f"팀플이 {team_condition} 강의를 찾을 수 없습니다.")
        exit()

    seen = set()
    unique_lectures = []
    for lec in filtered_lectures:
        if lec["lecture_name"] not in seen:
            seen.add(lec["lecture_name"])
            unique_lectures.append(lec)

    if count:
        unique_lectures = unique_lectures[:count]

    response = f"팀플이 {team_condition} 전공 강의는 다음과 같습니다:\n"
    for i, lec in enumerate(unique_lectures, start=1):
        response += f"{i}. {lec['lecture_name']} (학정번호: {lec['lecture_id']})\n"

    print(response)
    exit()

# ✅ 환경 변수 로드
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is not set. Check your .env file.")

# ✅ OpenAI 클라이언트 초기화
openai = OpenAI(api_key=api_key)
query = sys.argv[1]

# ✅ 최신 방식으로 클라이언트 초기화
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("kw_documents")

query_embedding = openai.embeddings.create(
    model="text-embedding-3-small",
    input=query
).data[0].embedding

results = collection.query(
    query_embeddings=[query_embedding],
    n_results=3
)

contexts = "\n".join(results['documents'][0])

prompt = f"""
당신은 진로 및 학업 상담 챗봇입니다. 아래 정보를 참고하여 학생의 질문에 친절하게 답변하세요.

참고 정보:
{contexts}

질문: {query}
"""

completion = openai.chat.completions.create(
    model="gpt-4",
    messages=[{ "role": "user", "content": prompt }],
    temperature=0.7
)

print(completion.choices[0].message.content.strip())