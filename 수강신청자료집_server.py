import json
import uuid
import chromadb
from embedding import get_sentence_embedding

# 1. Chroma 서버 연결
chroma_client = chromadb.HttpClient(host="localhost", port=8000)

# 2. Collection 생성
collection = chroma_client.get_or_create_collection(
    name="course_registration_info"
)

# 3. JSON 데이터 로드
JSON_PATH = "json/kw_chatbot_data - 수강신청자료집.json"
with open(JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# 4. Document 준비
documents = [json.dumps(item, ensure_ascii=False) for item in data]
ids = [str(uuid.uuid4()) for _ in documents]
metadatas = [{"index": idx} for idx in range(len(documents))]

# 5. 텍스트를 직접 임베딩해서 벡터로 변환
embeddings = get_sentence_embedding(documents)

# 6. Chroma에 벡터 저장
collection.add(
    embeddings=embeddings,
    documents=None,
    ids=ids,
    metadatas=metadatas
)

print("✅ 벡터 저장 완료")
