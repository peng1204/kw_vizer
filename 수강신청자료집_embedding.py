import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import json

# 1. ChromaDB 클라이언트 생성
client = chromadb.Client(Settings())

# 2. Collection 만들기
collection = client.get_or_create_collection(name="lecture_data")

# 3. 임베딩 모델 로드
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# 4. JSON 파일 읽기
with open('/Users/hyunjin/Desktop/kw_vizer/수강신청자료집.json', 'r', encoding='utf-8') as f:
    lectures = json.load(f)

# 5. documents, ids, metadatas 준비
documents = []
ids = []
metadatas = []

# 중복 체크용 dict
id_count = {}

for lec in lectures:
    # document 만들기
    doc = f"{lec.get('lecture_name', '')} {lec.get('담당교수', '')} {lec.get('강의시간', '')} {lec.get('강의유형', '')}"
    documents.append(doc)

    # id 처리
    base_id = lec.get('lecture_id', '')
    if base_id in id_count:
        id_count[base_id] += 1
        new_id = f"{base_id}_{id_count[base_id]}"  # 중복될 경우 _1, _2 붙이기
    else:
        id_count[base_id] = 0
        new_id = base_id

    ids.append(new_id)

    # metadata
    metadatas.append({
        "lecture_id": base_id,
        "lecture_name": lec.get('lecture_name', ''),
        "담당교수": lec.get('담당교수', ''),
        "학점": lec.get('학점', ''),
        "이수": lec.get('이수', '')
    })

# 6. 문서들을 임베딩
embeddings = model.encode(documents).tolist()

# 7. ChromaDB에 삽입
collection.add(
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas,
    ids=ids
)

print("✅ 데이터 삽입 완료!\n")

# 8. Embedding 결과 출력
print("📈 생성된 Embedding 벡터들:")
for emb in embeddings:
    print(emb)

    # 9. 질문 입력 받아서 검색하는 기능
while True:
    user_question = input("\n🔎 검색할 내용을 입력하세요 (종료하려면 'exit' 입력): ")
    
    if user_question.lower() == "exit":
        print("👋 검색을 종료합니다.")
        break

    if not user_question.strip():
        print("⚠️ 검색어를 입력해주세요!")
        continue

    # 질문을 임베딩
    query_embedding = model.encode([user_question]).tolist()

    # ChromaDB에서 비슷한 결과 검색
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=5,  # 기본 5개 보여줌
        include=['metadatas', 'documents', 'distances']  # 유사도 점수(distance) 포함해서 받기
    )

    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    distances = results['distances'][0]

    if not documents:
        print("😥 검색 결과가 없습니다. 다른 질문을 해보세요!")
        continue

    print("\n📚 검색 결과:")
    for doc, meta, distance in zip(documents, metadatas, distances):
        similarity_score = (1 - distance) * 100  # 유사도를 %로 변환
        print(f"- [{similarity_score:.2f}% 일치] 강의명: {meta['lecture_name']} | 교수명: {meta['담당교수']} | 학점: {meta['학점']} | 이수구분: {meta['이수']}")