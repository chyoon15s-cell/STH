import streamlit as st
import pandas as pd
import os
from openpyxl import load_workbook

# 1. 안내 문구 설정
ERROR_MESSAGE = "오류입니다. 담당자에게 연락부탁드립니다. 070-4820-2709"
ELDERLY_NOTICE = "⚠️ 원로회원 변경 요청 문의필요 070-765-6503"

# 2. 페이지 설정
st.set_page_config(page_title="서울연극협회 회비 조회", layout="centered")


# 3. 데이터 및 색상 로드 함수
@st.cache_data
def load_data_with_color():
    # 요청하신 파일명으로 변경
    file_name = "서협 회비납부현황 2026-02-05 14시 기준.xlsx"

    try:
        if not os.path.exists(file_name):
            return None

        # A. 데이터 읽기
        df = pd.read_excel(file_name, dtype=str)
        df.columns = [str(c).replace('\n', '').strip() for c in df.columns]

        # B. 배경색 읽기 (노란색 셀 감지)
        wb = load_workbook(file_name, data_only=True)
        ws = wb.active

        # '성명' 열 위치 확인
        name_col_idx = -1
        for i, cell in enumerate(ws[1]):
            if str(cell.value).replace('\n', '').strip() == "성명":
                name_col_idx = i + 1
                break

        yellow_rows = []
        if name_col_idx != -1:
            for row in range(2, ws.max_row + 1):
                color = ws.cell(row=row, column=name_col_idx).fill.start_color.index
                # 다양한 노란색 코드 대응 (표준 노랑: FFFF00)
                if color in ["FFFF0000", "FFFFFF00", "FFFF00", "00FFFF00"]:
                    yellow_rows.append(True)
                else:
                    yellow_rows.append(False)
        else:
            yellow_rows = [False] * len(df)

        df['is_yellow'] = yellow_rows[:len(df)]
        return df
    except:
        return None


df = load_data_with_color()

# 4. 화면 구성
st.title("🎭 회비 납부 현황 조회")
st.write("성함과 생년월일 6자리를 입력해 주세요.")
st.markdown("---")

if df is None:
    st.error(ERROR_MESSAGE)
else:
    with st.form("search_form"):
        name_input = st.text_input("성함", placeholder="예: 홍길동")
        birth_input = st.text_input("생년월일 6자리", placeholder="예: 900101", max_chars=6)
        submit = st.form_submit_button("조회하기")

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

                    # 💥 노란색 배경 회원 특별 안내 (원로회원 전용)
                    if res['is_yellow'] == True:
                        st.warning(ELDERLY_NOTICE)

                    # 회비 정보 출력
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
                    st.warning("일치하는 정보가 없습니다. 입력 정보를 다시 확인해 주세요.")
            except:
                st.error(ERROR_MESSAGE)
        else:
            st.warning("성함과 생년월일 6자리를 올바르게 입력해 주세요.")
