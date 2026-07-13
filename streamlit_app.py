import streamlit as st
from rag import ask

st.set_page_config(
    page_title="지브리 챗봇",
    page_icon="🤖",
    layout="wide"   
)

st.title("지브리 챗봇 🎬")

# 1. 대화 기록 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. 저장된 모든 이전 대화 출력 (화면 유지)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. 사용자 입력 처리
if question := st.chat_input("지브리 영화에 대해 궁금한 점을 물어보세요!"):
    
    # 사용자 메시지를 화면에 즉시 출력 및 세션 저장
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    # AI 챗봇 응답 생성 및 화면 출력
    with st.chat_message("assistant"):
        with st.spinner("지브리 아카이브를 검색하는 중..."):
            try:
                answer = ask(question)
                st.markdown(answer)
                # 챗봇 응답도 성공적으로 나오면 세션에 저장
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")