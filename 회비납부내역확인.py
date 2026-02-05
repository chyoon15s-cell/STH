import streamlit as st
import pandas as pd
import os

# 1. 안내 문구 설정 (공통 사용)
ERROR_MESSAGE = "오류입니다. 담당자에게 연락부탁드립니다. 070-4820-2709"

# 2. 페이지 설정
st.set_page_config(page_title="서울연극협회 회비 조회", layout="centered")


# 3. 데이터 로드 함수
@st.cache_data
def load_data():
    # 새 파일 이름 반영
    file_name = "26-02-05 회원명단_서울연극협회(읽기전용으로 읽어주세요) (자동 저장됨).xlsx"

    try:
        if not os.path.exists(file_name):
            return None

        # 엑셀 파일 읽기
        df = pd.read_excel(file_name, dtype=str)
        # 열 이름 정리 (공백/줄바꿈 제거)
        df.columns = [str(c).replace('\n', '').strip() for c in df.columns]
        return df
    except:
        return None


# 데이터 불러오기 실행
df = load_data()

# 4. 화면 구성
st.title("🎭 회비 납부 현황 조회")
st.write("성함과 생년월일 6자리를 입력해 주세요.")
st.markdown("---")

# 5. 입력 폼
if df is None:
    # 파일을 못 불러왔을 때 안내
    st.error(ERROR_MESSAGE)
else:
    with st.form("search_form"):
        name_input = st.text_input("성함", placeholder="예: 홍길동")
        birth_input = st.text_input("생년월일 6자리", placeholder="예: 900101", max_chars=6)
        submit = st.form_submit_button("조회하기")

    # 6. 조회 로직
    if submit:
        if name_input and len(birth_input) == 6:
            try:
                # 데이터 검색
                match = df[
                    (df['성명'].str.strip() == name_input.strip()) &
                    (df['생년월일'].str.contains(birth_input.strip()))
                    ]

                if not match.empty:
                    res = match.iloc[0]
                    st.success(f"✅ {name_input} 회원님의 정보가 확인되었습니다.")

                    # 2026년 회비 데이터 처리
                    fee_col = '회비2026년'
                    if fee_col in df.columns:
                        raw_fee = str(res[fee_col]).strip()
                        is_unpaid = raw_fee in ['0', '0.0', '미납', 'nan', '', 'None']

                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("2026년 완납 여부", "🔴 미납" if is_unpaid else "🔵 완납")
                        with col2:
                            amount = raw_fee if is_unpaid else "0"
                            st.metric("납부 예정 금액", f"{amount}원")

                    st.info(f"**소속:** {res['소속지부']} / {res['소속극단']}")
                else:
                    # 정보가 없는 경우 (입력 오류 등)
                    st.warning("일치하는 정보가 없습니다. 입력 정보를 다시 확인해 주세요.")
            except:
                # 코드 실행 중 알 수 없는 에러 발생 시
                st.error(ERROR_MESSAGE)
        else:
            st.warning("성함과 생년월일 6자리를 올바르게 입력해 주세요.")