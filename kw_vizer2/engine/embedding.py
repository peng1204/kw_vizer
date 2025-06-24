#### 임베딩 모델
from langchain_huggingface import HuggingFaceEmbeddings

ko_embedding = HuggingFaceEmbeddings(
    model_name="jhgan/ko-sroberta-multitask", 
    model_kwargs={"device": "cpu"}             
)

import shutil
import os
from pathlib import Path
import torch

# 전체 Chroma DB 삭제 (기본 디렉토리와 시스템 캐시 포함)
shutil.rmtree(".chroma_db", ignore_errors=True)
shutil.rmtree(Path.home() /".chroma_db", ignore_errors=True)

import os
import json
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
import chromadb
from langchain_community.document_loaders import PyPDFLoader

os.environ["OPENAI_API_KEY"] = "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"

embeddings_model  =ko_embedding
text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
client = chromadb.PersistentClient(path="./data/chroma_db")


def load_json_documents(json_files):
    docs = [] 
    for file in json_files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        #시나리오
        for item in data:
            if "Text" in item and "Completion" in item:
                docs.append(Document(
                    page_content=f"질문: {item['Text']}\n답변: {item['Completion']}",
                    metadata={
                        "카테고리": item.get("카테고리", "")
                    }
                ))

            # 수강이력
            if "lecture_name" in item and "student_id" in item:
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

                docs.append(Document(
                    page_content=content,
                    metadata={
                        "lecture_name": item["lecture_name"],
                        "course_type": item["lecture_course_type"]
                    }
                ))

            # 강의 탐색
            if "lecture_id" in item and "lecture_name" in item and "student_id" not in item:
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
                docs.append(Document(
                    page_content=content,
                    metadata={
                        "lecture_id": item.get("lecture_id", ""),
                        "lecture_name": item.get("lecture_name", ""),
                        "lecture_ratings": item.get("lecture_ratings", ""),
                        "lecture_team": item.get("lecture_team", ""),
                        "lecutre_grade": item.get("lecutre_grade", ""),
                        "professor": item.get("lecture_professorname", "")
                    }
                ))
    return [doc for doc in docs if doc.page_content and doc.page_content.strip()]


base_path = r"C:\Users\82103\kw_vizer2\data"
user_datasets = {
        "kim": [os.path.join(base_path, fname) for fname in [
            "김브티_수강이력.json",
            "김브티_성적.json",
            "Student.json"
        ]],
        "hong": [os.path.join(base_path, fname) for fname in [
            "홍데사_수강이력.json",
            "홍데사_성적.json",
            "Student.json"
        ]]
    }   
task_datasets = {
        "lecture_search": [os.path.join(base_path, fname) for fname in [
            "강의탐색.json", 
            "강의 평점.json", 
            "수강신청자료집.json",
            "커리큘럼(DS).json", 
            "커리큘럼(VT).json",
            "강의계획서.json", 
            "lecture_domain.json"
        ]],
        "career_counsel": [os.path.join(base_path, fname) for fname in [
            "진로상담.json", 
            "수강신청자료집.json", 
            "커리큘럼(DS).json",
            "커리큘럼(VT).json", 
            "강의계획서.json"
        ]],
        "academic_status": [os.path.join(base_path, fname) for fname in [
        "학습현황.json", 
        "김브티_수강이력.json", 
        "홍데사_수강이력.json",
        "Student.json"
    ]]

    }

# ✅ 기존 컬렉션 확인
def get_existing_collections():
    try:
        return [c.name for c in client.list_collections()]
    except:
        pass

# ✅ 임베딩 함수
def embed_all_data():
    existing = get_existing_collections()
 # 사용자별
    for user_id, files in user_datasets.items():
        collection_name = f"lecture_search_{user_id}"
        if collection_name in existing:
            print(f"[{collection_name}] 이미 임베딩됨. 생략.")
            continue
        docs = load_json_documents(files)
        split_docs = text_splitter.split_documents(docs)
        texts = [doc.page_content for doc in split_docs]
        embeddings = embeddings_model.embed_documents(texts)
        collection = client.create_collection(name=collection_name)
        collection.add(
            documents=texts,
            embeddings=embeddings,
            ids=[f"{collection_name}_{i}" for i in range(len(texts))]
        )
        print(f"[{collection_name}] 임베딩 완료: {len(texts)}건")

    # 기능별
    for task, files in task_datasets.items():
        if task in existing:
            print(f"[{task}] 이미 임베딩됨. 생략.")
            continue
        docs = load_json_documents(files)
        split_docs = text_splitter.split_documents(docs)
        texts = [doc.page_content for doc in split_docs]
        embeddings = embeddings_model.embed_documents(texts)
        collection = client.create_collection(name=task)
        collection.add(
            documents=texts,
            embeddings=embeddings,
            ids=[f"{task}_{i}" for i in range(len(texts))]
        )
        print(f"[{task}] 임베딩 완료: {len(texts)}건")

    # ✅ PDF 임베딩
    pdf_path = os.path.join(base_path, "수강신청_자료집_전체(2025-1)v4.pdf")
    if os.path.exists(pdf_path):
        loader = PyPDFLoader(pdf_path)
        pages = loader.load_and_split()
        pdf_docs = text_splitter.split_documents(pages)
        texts = [doc.page_content for doc in pdf_docs]
        embeddings = embeddings_model.embed_documents(texts)
        for name in ["lecture_search", "career_counsel", "academic_status"]:
            collection = client.get_or_create_collection(name=name)
            collection.add(
                documents=texts,
                embeddings=embeddings,
                ids=[f"{name}_pdf_{i}" for i in range(len(texts))]
            )
            print(f"[{name}] PDF 임베딩 추가 완료: {len(texts)}건")

# ✅ 내보내기
__all__ = ["ko_embedding", "client", "text_splitter", "embeddings_model", "embed_all_data"]