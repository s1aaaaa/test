import streamlit as st

st.title("📝 간편 메모장")

# 메모를 저장할 리스트 초기화
if "notes" not in st.session_state:
    st.session_state.notes = []

# 입력 폼
new_note = st.text_input("메모를 입력하세요:")
if st.button("추가하기"):
    if new_note:
        st.session_state.notes.append(new_note)
        st.rerun()

st.divider()

# 메모 목록 출력
st.subheader("저장된 메모 목록")
if not st.session_state.notes:
    st.info("작성된 메모가 없습니다.")
else:
    for i, note in enumerate(st.session_state.notes):
        st.write(f"{i+1}. {note}")
        
    if st.button("모두 삭제"):
        st.session_state.notes = []
        st.rerun()
