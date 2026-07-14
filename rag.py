import sys
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

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

# 검색기 (기존 k=20은 너무 많은 문서를 불러와 컨텍스트가 터질 수 있으니 상황에 맞게 조절하세요)
retriever = db.as_retriever(
    search_kwargs={"k": 10} 
)

# ----------------- 1. 프롬프트 수정 (MessagesPlaceholder 추가) -----------------
# 시스템 프롬프트와 대화 기록(history), 그리고 마지막 사용자 질문을 분리하여 구성합니다.
prompt = ChatPromptTemplate.from_messages([
    ("system", """당신은 스튜디오 지브리(Studio Ghibli) 전문 인공지능 어시스턴트입니다. 
제공된 [지브리 위키 문서]의 내용들을 바탕으로 사용자의 질문에 친절하고 정확하게 답해주세요.

[답변 원칙]
1. 문서에 특정 단어가 토씨 하나 틀리지 않고 그대로 적혀있지 않더라도, 제공된 정보(작품 정보, 흥행 기록, 역사 등)를 종합하여 "지브리의 대표작" 같은 추상적이거나 종합적인 질문에 유연하게 추론하여 답변하세요.
2. 질문에 답할 때 제공된 문서의 내용을 최대한 활용하되, 지브리 팬들이 공감할 수 있도록 자연스럽고 풍부한 문장으로 구성하세요.
3. 완전히 근거가 없거나, 제공된 문서 전체의 맥락과 전혀 상관없는 엉뚱한 정보(예: 디즈니나 신카이 마코토 감독의 작품을 지브리 작품이라고 하는 등)는 절대로 지어내서 답변하지 마세요.
4. 문서의 내용만으로는 도저히 유추할 수 없는 정보라면, 솔직하게 모른다고 답변한 뒤 아는 선에서 최대한 도움이 되는 정보를 제공하세요.
5. 말투를 어린아이에게 설명 해주는 말투로 해주세요.
6. 문서를 참고하지 않았다면 정확하지 않을 수도 있다고 말해주세요.
7. 작품명은 따로 요청하지 않으면 한국의 기준으로 말해 주세요. (예: 스피리티드 어웨이 말고 센과 치히로의 행방불명)
[지브리 위키 문서]
{context}"""),
    
    # 여기에 이전 대화 기록들이 자동으로 주입됩니다. (메모리 역할)
    MessagesPlaceholder(variable_name="history"), 
    
    ("human", "{question}")
])

# ----------------- 2. 체인 및 메모리 설정 -----------------
chain = prompt | llm | StrOutputParser()

# 세션별로 대화 이력을 저장할 딕셔너리
store = {}

def get_session_history(session_id: str) -> ChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# 대화 이력을 자동으로 관리해주는 래퍼(Wrapper) 체인 생성
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="question", # 모델의 입력으로 들어갈 사용자 질문 키
    history_messages_key="history", # 프롬프트의 MessagesPlaceholder 키와 일치해야 함
)

# 관련문서 검색후 문자열 병합
def format_docs(docs):
    result = ""
    for doc in docs:
        result = result + doc.page_content + "\n\n"
    return result

# ----------------- 3. 실행 함수 수정 -----------------
# 대화를 구분하기 위해 session_id를 인자로 받습니다. (기본값 "default_user")
def ask(question, session_id="default_user"):
    
    # 1. 관련 문서 검색 (질문 기반)
    docs = retriever.invoke(question)
    
    # 2. 문서 포맷팅
    context = format_docs(docs)
    
    # 3. History가 포함된 체인 실행
    # 이제 invoke할 때 config를 통해 session_id를 넘겨줍니다.
    answer = chain_with_history.invoke(
        {
            "context": context,
            "question": question
        },
        config={"configurable": {"session_id": session_id}}
    )

    return answer