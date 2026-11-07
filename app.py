import random
import streamlit as st

# 페이지 설정
st.set_page_config(page_title="가위바위보 게임", page_icon="✊", layout="centered")

# 이모지 맵핑
CHOICES = {"가위": "✌️", "바위": "✊", "보": "✋"}

# 게임 진행 함수
def play(user_choice):
    computer_choice = random.choice(list(CHOICES.keys()))

    # 승패 판정 로직
    if user_choice == computer_choice:
        result = "무승부"
    elif (
        (user_choice == "가위" and computer_choice == "보")
        or (user_choice == "바위" and computer_choice == "가위")
        or (user_choice == "보" and computer_choice == "바위")
    ):
        result = "승리"
    else:
        result = "패배"

    # 이번 판 결과 저장
    st.session_state.last_game = {
        "user": user_choice,
        "computer": computer_choice,
        "result": result,
    }


# 메인 UI 구성
st.title("✊✌️✋ 가위바위보 게임")
st.write("아래 버튼 중 하나를 눌러 게임을 시작하세요!")

st.divider()

# 사용자 선택 버튼
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("✌️ 가위", use_container_width=True):
        play("가위")

with col2:
    if st.button("✊ 바위", use_container_width=True):
        play("바위")

with col3:
    if st.button("✋ 보", use_container_width=True):
        play("보")

st.divider()

# 게임 결과 출력
if "last_game" in st.session_state:
    last = st.session_state.last_game
    res_col1, res_col2 = st.columns(2)

    with res_col1:
        st.subheader("내 선택")
        st.write(f"# {CHOICES[last['user']]}")
        st.write(f"**{last['user']}**")

    with res_col2:
        st.subheader("컴퓨터 선택")
        st.write(f"# {CHOICES[last['computer']]}")
        st.write(f"**{last['computer']}**")

    # 승패 메시지
    if last["result"] == "승리":
        st.success("🎉 이겼습니다!")
    elif last["result"] == "패배":
        st.error("😭 졌습니다...")
    else:
        st.info("🤝 비겼습니다.")
