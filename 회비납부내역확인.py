import streamlit as st
import pandas as pd
import os
import glob
from openpyxl import load_workbook

# 1. 안내 문구 설정
ERROR_MESSAGE = "오류입니다. 담당자에게 연락부탁드립니다. 070-4820-2709"
ELDERLY_NOTICE = "⚠️ 원로회원 변경 요청 문의필요 070-765-6503"

# 2. 페이지 설정
st.set_page_config(page_title="서울연극협회 회비 조회", layout="centered")

# 3. 데이터 로드 함수
@st.cache_data
def load_data_with_logic():
    try:
        excel_files = glob.glob("*.xlsx")
        if not excel_files: return None
        file_name = excel_files[0] 
        
        df = pd.read_excel(file_name, dtype=str)
        df.columns = [str(c).replace('\n', '').strip() for c in df.columns]

        wb = load_workbook(file_name, data_only=True)
        ws = wb.active
        
        name_idx = -1
        elderly_col_idx = -1
        
        for i, cell in enumerate(ws[1]):
            header = str(cell.value).replace('\n', '').replace(' ', '').strip()
            if "성명" in header: name_idx = i + 1
            if "원로" in header: elderly_col_idx = i + 1

        elderly_target_rows = []
        for row in range(2, ws.max_row + 1):
            is_yellow = False
            if name_idx != -1:
                color = ws.cell(row=row, column=name_idx).fill.start_color.index
                if color in ["FFFF0000", "FFFFFF00", "FFFF00", "00FFFF00"]:
                    is_yellow = True
            
            has_elderly_text = False
            if elderly_col_idx != -1:
                val = str(ws.cell(row=row, column=elderly_col_idx).value).strip()
                if val and val != "None" and val != "0" and val != "nan":
                    has_elderly_text = True
            
            elderly_target_rows.append(is_yellow and has_elderly_text)
            
        df['is_elderly_target'] = elderly_target_rows[:len(df)]
        return df
    except:
        return None

df = load_data_with_logic()

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
                match = df[
                    (df['성명'].str.replace(' ', '').str.strip() == name_input.replace(' ', '').strip()) & 
                    (df['생년월일'].str.contains(birth_input.strip()))
                ]
                
                if not match.empty:
                    res = match.iloc[0]
                    st.success(f"✅ {name_input} 회원님의 정보가 확인되었습니다.")
                    
                    if res['is_elderly_target'] == True:
                        st.warning(ELDERLY_NOTICE)

                    # 회비 정보 출력 및 'nan' 처리
                    target_col = [c for c in df.columns if '2026' in c and '회비' in c]
                    if target_col:
                        fee_col = target_col[0]
                        raw_fee = str(res[fee_col]).strip().lower()
                        
                        # 미납 여부 판단
                        is_unpaid = raw_fee in ['0', '0.0', '미납', 'nan', '', 'none']
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("2026년 완납 여부", "🔴 미납" if is_unpaid else "🔵 완납")
                        with col2:
                            # 💥 금액 표시 로직: nan이거나 비어있으면 '문의필요', 아니면 금액 표시
                            if is_unpaid:
                                if raw_fee in ['nan', '', 'none']:
                                    display_amount = "문의필요"
                                else:
                                    # 0원도 문의필요로 띄우고 싶다면 이 부분을 조정하세요. 
                                    # 지금은 0원일 경우 0원, 데이터가 아예 없으면 문의필요입니다.
                                    display_amount = f"{raw_fee}원" if raw_fee != '0' else "문의필요"
                            else:
                                display_amount = "0원"
                            
                            st.metric("납부 예정 금액", display_amount)
                    
                    st.info(f"**소속:** {res.get('소속지부', '정보없음')} / {res.get('소속극단', '정보없음')}")
                else:
                    st.warning("일치하는 정보가 없습니다. 입력 정보를 다시 확인해 주세요.")
            except:
                st.error(ERROR_MESSAGE)
        else:
            st.warning("성함과 생년월일 6자리를 올바르게 입력해 주세요.")
