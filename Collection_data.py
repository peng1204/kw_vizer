import chromadb

# 1. 서버 연결
chroma_client = chromadb.HttpClient(host="localhost", port=8000)

# 2. Collection 열기
collection = chroma_client.get_collection(name="course_registration_info")

# 3. 전체 데이터 조회 (documents 없이, embeddings만 가져오기)
all_data = collection.get(include=["embeddings"])

print(all_data.keys())    # ids, embeddings, metadatas만 조회
print(all_data['embeddings'])  # ✅ 숫자(float) 벡터값만 출력
