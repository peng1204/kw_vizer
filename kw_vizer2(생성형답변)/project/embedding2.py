import os
import json
import shutil
from pathlib import Path
from collections import defaultdict

import chromadb
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

# ▶️ Embedding 설정
ko_embedding = HuggingFaceEmbeddings(
    model_name="jhgan/ko-sroberta-multitask",
    model_kwargs={"device": "cpu"}
)

embeddings_model = ko_embedding
text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
client = chromadb.PersistentClient(path="/Users/hyunjin/Documents/dev/chroma_db_fresh")

# ▶️ Vectorstore 반환 함수
def get_vectorstore(user_id: str, collection_name: str) -> Chroma:
    print("✅ [embedding2.py] get_vectorstore 실행됨:", user_id, collection_name)
    return Chroma(
        client=client,
        collection_name=collection_name,
        embedding_function=embeddings_model
    )

# ▶️ JSON 문서 로드 함수
def load_json_documents(json_files: list) -> list[Document]:
    docs = []
    for file in json_files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        for item in data:
            if "Text" in item and "Completion" in item:
                docs.append(Document(
                    page_content=f"질문: {item['Text']}\n답변: {item['Completion']}",
                    metadata={"카테고리": item.get("카테고리", "")}
                ))
            elif "lecture_name" in item and "student_id" in item:
                content = (
                    f"학번: {item['student_id']}\n"
                    f"강의명: {item['lecture_name']}\n"
                    f"학정번호: {item['lecture_id']}\n"
                    f"개설 학과: {item['department_offered']}\n"
                    f"이수 구분: {item['lecture_course_type']}\n"
                    f"학점: {item['lecture_credit']}학점\n"
                    f"성적: {item['lecutre_grade']}"
                )
                if "retake_or_delete_status" in item:
                    content += f"\n재수강/삭제 여부: {item['retake_or_delete_status']}"
                if "retake_status" in item:
                    content += f"\n재수강 여부: {item['retake_status']}"
                docs.append(Document(page_content=content))
            elif "lecture_id" in item and "lecture_name" in item and "student_id" not in item:
                content = (
                    f"학정번호: {item.get('lecture_id', '')}\n"
                    f"강의명: {item.get('lecture_name', '')}\n"
                    f"강의평점: {item.get('lecture_ratings', '')}\n"
                    f"과제: {item.get('lecture_homework', '')}\n"
                    f"팀플: {item.get('lecture_team', '')}\n"
                    f"성적평가정도: {item.get('lecutre_grade', '')}\n"
                    f"출결 방식: {item.get('lecutre_attendance', '')}\n"
                    f"시험 횟수: {item.get('lecutre_test', '')}\n"
                    f"시험 방식: {item.get('lecture_testinform', '')}\n"
                    f"전공 학점: {item.get('credits_major', '없음')}\n"
                    f"교양 학점: {item.get('credits_general', '없음')}\n"
                    f"총 학점: {item.get('credits_total', '없음')}\n"
                    f"교수명: {item.get('lecture_professorname', '')}\n"
                    f"수업 시간: {item.get('lecture_time', '')}\n"
                    f"강의 유형: {item.get('lecture_course_type', '')}\n"
                    f"학점: {item.get('lecture_hours', '')}시간\n"
                    f"학기: {item.get('lecture_semester', '')}학기\n"
                    f"강의 설명: {item.get('lecture_inform', '')}"
                    f"영역: {item.get('lecture_domain', '')}\n"
                )
                docs.append(Document(page_content=content))
    return [doc for doc in docs if doc.page_content.strip()]

# ▶️ JSON 임베딩 함수
def embed_json_documents(json_paths: list, collection_name: str):
    docs = load_json_documents(json_paths)
    split_docs = text_splitter.split_documents(docs)
    texts = [d.page_content for d in split_docs]
    embeddings = embeddings_model.embed_documents(texts)

    collection = client.get_or_create_collection(name=collection_name)
    collection.add(documents=texts, embeddings=embeddings, ids=[f"{collection_name}_{i}" for i in range(len(texts))])
    print(f"✅ {collection_name} 임베딩 완료: {len(texts)}건")

# ▶️ PDF 임베딩 함수
def embed_pdf_to_collections(pdf_path: str, collection_names: list[str]):
    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()
    docs = text_splitter.split_documents(pages)
    texts = [d.page_content for d in docs]
    embeddings = embeddings_model.embed_documents(texts)

    for name in collection_names:
        collection = client.get_or_create_collection(name=name)
        collection.add(documents=texts, embeddings=embeddings, ids=[f"{name}_pdf_{i}" for i in range(len(texts))])
        print(f"📄 {name} PDF 임베딩 완료: {len(texts)}건")

# ▶️ 전체 임베딩 초기화
def embed_all_data():
    base_path = "/Users/hyunjin/Desktop"
    user_datasets = {
        "kim": [os.path.join(base_path, fname) for fname in [
            "kw_chatbot_data - 김브티_수강이력.json",
            "kw_chatbot_data - 김브티_성적.json",
            "kw_chatbot_data - Student.json"
        ]],
        "hong": [os.path.join(base_path, fname) for fname in [
            "kw_chatbot_data - 홍데사_수강이력.json",
            "kw_chatbot_data - 홍데사_성적.json",
            "kw_chatbot_data - Student.json"
        ]]
    }   

    task_datasets = {
        "lecture_search": [os.path.join(base_path, fname) for fname in [
            "강의탐색3.json", 
            "kw_chatbot_data - 강의 평점.json", 
            "kw_chatbot_data - 수강신청자료집.json",
            "kw_chatbot_data - 커리큘럼(DS).json", 
            "kw_chatbot_data - 커리큘럼(VT).json",
            "kw_chatbot_data - 강의계획서.json", 
            "lecture_domain.json"
        ]],
        "career_counsel": [os.path.join(base_path, fname) for fname in [
            "진로상담.json", 
            "kw_chatbot_data - 수강신청자료집.json", 
            "kw_chatbot_data - 커리큘럼(DS).json",
            "kw_chatbot_data - 커리큘럼(VT).json", 
            "kw_chatbot_data - 강의계획서.json"
        ]],
        "academic_status": [os.path.join(base_path, fname) for fname in [
            "학습현황2.json", 
            "kw_chatbot_data - 김브티_수강이력.json", 
            "kw_chatbot_data - 홍데사_수강이력.json",
            "kw_chatbot_data - Student.json"
        ]]
    }

    # 사용자별
    for user_id, paths in user_datasets.items():
        collection_name = f"lecture_search_{user_id}"
        embed_json_documents(paths, collection_name)

    # 기능별
    for task, paths in task_datasets.items():
        embed_json_documents(paths, task)

    # PDF
    pdf_path = os.path.join(base_path, "수강신청_자료집_전체(2025-1)v4.pdf")
    if os.path.exists(pdf_path):
        embed_pdf_to_collections(pdf_path, ["lecture_search", "career_counsel", "academic_status"])

# ▶️ 자동 실행 방지
#if __name__ == "__main__":
    #shutil.rmtree("./chroma_db", ignore_errors=True)
    #shutil.rmtree(Path.home() / ".chromadb", ignore_errors=True)
    #embed_all_data()

# ▶️ 내보내기
__all__ = ["ko_embedding", "client", "text_splitter", "embeddings_model", "embed_all_data", "get_vectorstore"]