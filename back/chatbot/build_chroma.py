import os
import json
import chromadb
from chromadb.config import Settings
from openai import OpenAI
from dotenv import load_dotenv
from chromadb import PersistentClient

print("🚀 스크립트 시작")

# 환경변수 로드
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
print(f"🔑 OPENAI_API_KEY: {api_key[:10]}...")  # 키 앞부분만 출력(보안상)

openai = OpenAI(api_key=api_key)

# ChromaDB 클라이언트 초기화
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection("kw_documents")

data_dir = "./data"
doc_id = 0

print("📂 데이터 폴더 확인 중:", data_dir)
files = os.listdir(data_dir)
print(f"📄 총 JSON 파일 개수: {len([f for f in files if f.endswith('.json')])}")

for file_name in files:
    if file_name.endswith(".json"):
        print(f"📁 {file_name} 처리 시작")

        file_path = os.path.join(data_dir, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ {file_name} 디코딩 실패: {e}")
            continue

        for item in content:
            if isinstance(item, dict):
                for key, value in item.items():
                    text = f"{key}: {value}"
                    print(f"🔍 임베딩 생성 시도: {text[:30]}...")

                    try:
                        response = openai.embeddings.create(
                            model="text-embedding-3-small",
                            input=text
                        )
                        embedding = response.data[0].embedding

                        collection.add(
                            documents=[text],
                            embeddings=[embedding],
                            ids=[str(doc_id)],
                            metadatas=[{"source": file_name}]
                        )
                        print(f"✅ 저장 완료 ID: {doc_id}")
                        doc_id += 1

                    except Exception as e:
                        print(f"⚠️ 임베딩 실패: {e} (텍스트 일부: {text[:30]})")

print("💾 벡터 저장 중...")
persistent_client = PersistentClient(path="./chroma_db")

print("✅ ChromaDB 벡터 저장 완료!")
