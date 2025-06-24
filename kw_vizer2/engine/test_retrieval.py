from engine.embedding import ko_embedding
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from engine.retrieval import prompt 
import os

# Chroma DB 경로
vectorstore = Chroma(
    persist_directory="./data/chroma_db",
    collection_name="lecture_search",
    embedding_function=ko_embedding
)

# LLM 설정
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

# QA 체인 구성
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 20}),
    chain_type="stuff",
    chain_type_kwargs={"prompt": prompt}
)

# 테스트 쿼리
query = "조재희 교수님 강의 추천해줘"
result = qa_chain.invoke({"query": query})["result"]
print("[✅ 결과 출력]")
print(result)
