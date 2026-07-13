import os
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from tqdm import tqdm  # 💡 진행률 표시를 위한 라이브러리 추가

# 현재 실행 중인 파이썬 파일이 있는 폴더의 절대 경로
BASE_DIR = Path(__file__).resolve().parent 

# 1. pdf 를 document 객체로 변환
documents = []

for pdf_file in BASE_DIR.glob("ghibli.pdf"): # 폴더에 있는 pdf 파일들을 반환
    loader = PyPDFLoader(str(pdf_file))
    documents.extend(loader.load())

print("페이지수:", len(documents))

# 2. 문서 분할
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100 # 앞뒤로 100글자 겹치게 #chunk_size의 10~20% 정도
)

docs = splitter.split_documents(documents)
total_chunks = len(docs)
print("청크 갯수:", total_chunks)

# 3. 임베딩 작업
embedding = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    # model_kwargs={'device': 'cuda'} 
)

# 4. 크로마 DB 생성 및 tqdm 진행률 적용
DB_PATH = BASE_DIR / "chroma_db_ghibli"

print("\n🚀 Vector DB 인덱싱 및 저장 시작...")

# ① 빈 Chroma DB 객체를 먼저 선언 (경로와 임베딩 모델 연결)
db = Chroma(
    persist_directory=str(DB_PATH),
    embedding_function=embedding
)

# ② 100개씩 쪼개서 넣기 위한 배치 사이즈 설정
BATCH_SIZE = 100

# ③ tqdm으로 감싸서 실시간 게이지 띄우기
with tqdm(total=total_chunks, desc="Chroma DB 저장률", unit="chunk") as pbar:
    for i in range(0, total_chunks, BATCH_SIZE):
        batch = docs[i : i + BATCH_SIZE]
        
        # 100개씩 DB에 추가 (이때 실제 임베딩 연산이 수행됩니다)
        db.add_documents(batch)
        
        # 추가된 개수만큼 진행률 바 갱신
        pbar.update(len(batch))

print("\n✨ Vector DB 저장 완료!")