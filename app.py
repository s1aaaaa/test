import os
import queue
import threading
import cv2
import numpy as np
import pyttsx3
import streamlit as st
from ultralytics import YOLO

# ==========================================
# 1. 시스템 설정 및 TTS(음성 합성) 엔진 초기화
# ==========================================
st.set_page_config(
    page_title="시각 보조 AI 카메라",
    page_icon="👁️",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# TTS 음성 출력 큐 (스레드 충돌 방지)
tts_queue = queue.Queue()


def tts_worker():
    """오프라인 음성 안내를 위한 백그라운드 스레드"""
    engine = pyttsx3.init()
    engine.setProperty("rate", 160)  # 읽기 속도 조절
    while True:
        text = tts_queue.get()
        if text is None:
            break
        engine.say(text)
        engine.runAndWait()
        tts_queue.task_done()


# TTS 백그라운드 스레드 시작
if "tts_thread_started" not in st.session_state:
    threading.Thread(target=tts_worker, daemon=True).start()
    st.session_state.tts_thread_started = True


def speak(text):
    """음성 출력 요청 함수"""
    tts_queue.put(text)


# 세션 상태 초기화
if "app_state" not in st.session_state:
    st.session_state.app_state = "RUNNING"  # RUNNING | EXIT_CONFIRM
    # 앱 시작 시 최초 음성 안내 실행
    speak("시각 보조 카메라 앱이 실행되었습니다. 화면 중앙의 음성 버튼을 눌러 명령하세요.")

# ==========================================
# 2. 로컬 AI 모델 로드 (오프라인 작동)
# ==========================================
@st.cache_resource
def load_yolo_model():
    # 인터넷 없이 동작하는 경량화 객체 탐지 모델 (yolov8n.pt 자동 로컬 저장)
    return YOLO("yolov8n.pt")


model = load_yolo_model()

# ==========================================
# 3. CSS 스타일링 (접근성 및 간결한 UI)
# ==========================================
st.markdown(
    """
    <style>
    /* 전체 배경을 어둡게 하여 대비 강조 */
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }
    /* 음성 셔터 버튼 대형화 및 원형 디자인 */
    div.stButton > button:first-child {
        background-color: #00E676;
        color: #000000;
        font-size: 28px !important;
        font-weight: bold;
        height: 120px;
        width: 100%;
        border-radius: 20px;
        border: 4px solid #FFFFFF;
        box-shadow: 0px 4px 15px rgba(0, 230, 118, 0.4);
    }
    /* 종료 처리 전용 버튼 스타일 */
    .exit-btn > button {
        background-color: #FF5252 !important;
        color: #FFFFFF !important;
        height: 80px !important;
        font-size: 22px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# ==========================================
# 4. 앱 화면 구성
# ==========================================

# A. 종료 확인 처리 화면 (실수 방지 안전장치)
if st.session_state.app_state == "EXIT_CONFIRM":
    st.warning("⚠️ 정말로 앱을 종료하시겠습니까?")
    st.write("실수로 누르셨다면 아래 '돌아가기' 버튼을 눌러주세요.")

    col_cancel, col_confirm = st.columns(2)

    with col_cancel:
        if st.button("🟢 계속 사용하기 (돌아가기)", use_container_width=True):
            st.session_state.app_state = "RUNNING"
            speak("앱을 계속 사용합니다.")
            st.rerun()

    with col_confirm:
        st.markdown('<div class="exit-btn">', unsafe_allow_html=True)
        if st.button("🔴 종료 확인", use_container_width=True):
            speak("앱을 종료합니다. 안녕히 가세요.")
            st.session_state.app_state = "TERMINATED"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.app_state == "TERMINATED":
    st.error("앱이 종료되었습니다. 브라우저 창을 닫아주세요.")

# B. 메인 카메라 및 조작 화면
else:
    st.title("👁️ AI 시각 보조 서비스")

    # 1. 카메라 프레임 영역 (카메라 뷰파인더)
    camera_image = st.camera_input(
        "카메라 화면", label_visibility="collapsed"
    )

    # 카메라 입력 시 AI 자동 분석 (장애물/객체 인지 및 음성 안내)
    if camera_image is not None:
        # 이미지를 OpenCV 포맷으로 변환
        bytes_data = camera_image.getvalue()
        cv_img = cv2.imdecode(
            np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR
        )

        # YOLO AI 객체 및 장애물 분석
        results = model(cv_img)
        detected_objects = []

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = model.names[cls_id]
                detected_objects.append(label)

        # 주요 인식 대상 한국어 번역 맵핑
        translation = {
            "person": "사람",
            "chair": "의자",
            "table": "탁자",
            "car": "자동차",
            "bottle": "병",
            "cup": "컵",
            "cell phone": "휴대폰",
            "door": "문",
        }

        if detected_objects:
            translated_items = [
                translation.get(item, item) for item in set(detected_objects)
            ]
            summary_text = f"전방에 {', '.join(translated_items)}가 있습니다. 주의하세요."
            st.info(f"🔊 {summary_text}")
            speak(summary_text)
        else:
            speak("특이 장애물이 감지되지 않았습니다.")

    st.divider()

    # 2. 메인 음성 소통 셔터 버튼
    if st.button("🎙️ 음성 안내 / 질문하기", use_container_width=True):
        speak("음성 명령을 듣고 있습니다. 필요하신 행동이나 질문을 말씀하세요.")
        st.toast("🎙️ 음성 명령 수신 중...")
        # 실제 환경에서는 local SpeechRecognition / Vosk 모듈을 연동하여 오프라인 음성 명령 수행

    # 3. 우발적 종료 방지 안전 바텀 영역
    st.divider()
    st.write("---")
    if st.button("🚪 앱 종료", key="request_exit"):
        st.session_state.app_state = "EXIT_CONFIRM"
        speak("종료 확인 화면입니다. 앱을 정말 종료하시겠습니까?")
        st.rerun()
