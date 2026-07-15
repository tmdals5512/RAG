import streamlit as st
from rag import ask
import base64
from PIL import Image

page_icon = Image.open("gaonasi_avatar.png")

st.set_page_config(
    page_title="지브리 백과사전",
    page_icon=page_icon,
    layout="centered", 
    initial_sidebar_state="auto"
)

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

local_image_path = "totoro.png"
BACKGROUND_PATH = "ponyo.jpg"

try:
    img_base64 = get_base64_image(local_image_path)
    img_html = f"data:image/png;base64,{img_base64}" 
    
    st.markdown(f"""
        <div style="text-align: center; padding: 20px; display: flex; align-items: center; justify-content: center; gap: 15px;">
            <img src="{img_html}" style="width: 55px; height: 55px; object-fit: contain;">
            <h1 style="color: #4A7C59; font-family: 'Helvetica Neue', sans-serif; margin: 0;">지브리 백과사전</h1>            
        </div>
    """, unsafe_allow_html=True)

except FileNotFoundError:
    st.error(f"'{local_image_path}' 파일을 찾을 수 없습니다. 파이썬 코드 파일과 같은 폴더에 사진이 있는지 확인해 주세요!")


def set_local_background(image_path):
    try:
        img_base64 = get_base64_image(image_path)
        page_bg_img = f'''
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{img_base64}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        /* 챗봇 대화 가독성을 높이기 위한 반투명 흰색 레이어 박스 */
        .main .block-container {{
            background-color: rgba(255, 255, 255, 0.88); 
            border-radius: 20px;
            padding: 40px;
            margin-top: 30px;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.15);
        }}
        # </style>
        '''
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        # 배경 이미지가 없더라도 에러로 멈추지 않고 경고만 표시 후 계속 진행
        st.warning(f"배경 이미지 '{image_path.name}' 파일을 찾을 수 없어 기본 배경으로 표시합니다.")

# set_local_background(BACKGROUND_PATH)



ASSISTANT_AVATAR = "gaonasi_avatar.png"
USER_AVATAR = "chihiro_avatar.png"

# 1. 대화 기록 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. 저장된 모든 이전 대화 출력 (화면 유지)
for message in st.session_state.messages:
    if message["role"] == "assistant":
        with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
            st.markdown(message["content"])
    else:
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(message["content"])

# 3. 사용자 입력 처리
if question := st.chat_input("가오나시에게 지브리에 대해 궁금한 점을 물어보세요!"):
    
    # 사용자 메시지를 화면에 즉시 출력 및 세션 저장
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    # AI 챗봇 응답 생성 및 화면 출력
    with st.chat_message("assistant", avatar=ASSISTANT_AVATAR):
        with st.spinner("가오나시가 생각하는 중..."):
            try:
                answer = ask(question)
                st.markdown(answer)
                # 챗봇 응답도 성공적으로 나오면 세션에 저장
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")