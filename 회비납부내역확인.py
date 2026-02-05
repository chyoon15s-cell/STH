import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정
st.set_page_config(page_title="서울연극협회 회비 조회", layout="centered")


# 2. 데이터 로드 (캐싱)
@st.cache_data
def load_data():
    file_name = "서협 회비납부현황 2026-02-05 14시 기준.xlsx"
    if not os.path.exists(file_name):
        return None
    # 엑셀의 모든 데이터를 문자열로 읽어오면 검색이 더 정확합니다.
    df = pd.read_excel(file_name, dtype=str)
    df.columns = df.columns.str.replace('\n', '').str.strip()
    return df


df = load_data()

if df is not None:
    st.title("🎭 회비 납부 현황 조회")
    st.markdown("---")

    # 3. 입력창 (성함 및 생년월일 6자리)
    with st.form("search_form", clear_on_submit=False):
        st.write("본인 확인을 위해 정보를 입력해 주세요.")
        name_input = st.text_input("성함", placeholder="예: 홍길동")
        birth_input = st.text_input("생년월일 6자리", placeholder="예: 900101", max_chars=6)
        submit = st.form_submit_button("조회하기")

    # 4. 조회 결과 로직
    if submit:
        if name_input and len(birth_input) == 6:
            # 엑셀의 '생년월일' 열에서 입력한 6자리가 포함되어 있는지 검색
            # (예: 19900101 데이터에서 900101 검색 가능하게 처리)
            match = df[
                (df['성명'].str.strip() == name_input.strip()) &
                (df['생년월일'].str.contains(birth_input.strip()))
                ]

            if not match.empty:
                res = match.iloc[0]

                # 회비2026년 데이터를 바탕으로 완납 여부와 금액 산출
                raw_fee = str(res['회비2026년']).strip()
                # 미납 조건: 값이 0, 0.0, 미납, 빈값인 경우
                is_unpaid = raw_fee in ['0', '0.0', '미납', 'nan', '', 'None']

                st.success(f"✅ {name_input} 회원님의 조회 결과입니다.")

                # 5. 결과 대시보드 (완납 여부 및 남은 금액)
                col1, col2 = st.columns(2)

                with col1:
                    status = "🔴 미납" if is_unpaid else "🔵 완납"
                    st.metric("2026년 완납 여부", status)

                with col2:
                    # 회비2026년 열에 적힌 값을 남은 금액으로 표시
                    # 완납인 경우 0원, 미납인 경우 해당 금액 표시
                    remained_amount = raw_fee if is_unpaid else "0"
                    st.metric("2026년 납부 예정 금액", f"{remained_amount}원")

                # 상세 정보 표시
                st.info(f"**소속:** {res['소속지부']} / {res['소속극단']} ({res['소속직위']})")

            else:
                st.error("일치하는 회원 정보가 없습니다. 성함과 생년월일을 다시 확인해 주세요.")
        else:
            st.warning("성함과 생년월일 6자리를 모두 올바르게 입력해 주세요.")

else:
    st.error("엑셀 파일을 찾을 수 없습니다. 파일명을 확인해 주세요.")