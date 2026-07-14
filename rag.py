from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

import sys
from pathlib import Path

# 현재 파일 기준으로 4단계 위 폴더를 import 경로에 추가
sys.path.append(str(Path(__file__).resolve().parent))

from llm_loader import init_custom_llm
llm = init_custom_llm()

# 이미 만들어진 크로마 DB 객체 생성
embedding = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
)

# 현재 rag.py가 있는 폴더
BASE_DIR = Path(__file__).resolve().parent

# chroma_db 폴더
DB_PATH = BASE_DIR / "chroma_db_ghibli"

db = Chroma(
    embedding_function = embedding,
    persist_directory = str(DB_PATH)
)

# 검색기
retriever = db.as_retriever(
    search_kwargs={"k": 20}
)

# 프롬프트 만들고 llm 연결 준비
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

prompt = ChatPromptTemplate.from_template(
"""
당신은 스튜디오 지브리(Studio Ghibli) 전문 인공지능 어시스턴트입니다. 
제공된 [지브리 위키 문서]의 내용들을 바탕으로 사용자의 질문에 친절하고 정확하게 답해주세요.

[답변 원칙]
1. 문서에 특정 단어가 토씨 하나 틀리지 않고 그대로 적혀있지 않더라도, 제공된 정보(작품 정보, 흥행 기록, 역사 등)를 종합하여 "지브리의 대표작" 같은 추상적이거나 종합적인 질문에 유연하게 추론하여 답변하세요.
2. 질문에 답할 때 제공된 문서의 내용을 최대한 활용하되, 지브리 팬들이 공감할 수 있도록 자연스럽고 풍부한 문장으로 구성하세요.
3. 완전히 근거가 없거나, 제공된 문서 전체의 맥락과 전혀 상관없는 엉뚱한 정보(예: 디즈니나 신카이 마코토 감독의 작품을 지브리 작품이라고 하는 등)는 절대로 지어내서 답변하지 마세요.
4. 문서의 내용만으로는 도저히 유추할 수 없는 정보라면, 솔직하게 모른다고 답변한 뒤 아는 선에서 최대한 도움이 되는 정보를 제공하세요.

문서

{context}

질문

{question}
"""
)

chain = prompt | llm | StrOutputParser()

# 관련문서 검색후 llm 연결
def format_docs(docs):
    result = ""
    for doc in docs:
        result = result + doc.page_content
        # 문서와 문서 사이를 명확하게 구분 하기 위해서. 
        # LLM도 문서가 구분되어 있다는 것을 더 명확하게 인식
        result = result + "\n\n"
    return result


def ask(question):
    
    # 1. 관련 문서 검색
    docs = retriever.invoke(question)
    
    # 2. 문자열로 변환
    context = format_docs(docs)
    
    #3. Chain 실행
    answer = chain.invoke(
        {
        "context":context,
        "question": question
        }
    )

    return answer