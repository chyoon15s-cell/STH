import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. 디자인 설정
st.set_page_config(page_title="서울연극협회 회비 조회", layout="centered")

st.markdown("""
    <style>
    .main-title { font-size: 30px !important; font-weight: bold; margin-bottom: 5px !important; }
    .sub-title { font-size: 16px; margin-bottom: -10px !important; }
    hr { margin-top: 10px !important; margin-bottom: 15px !important; }
    [data-testid="stMetricLabel"] { font-size: 14px !important; }
    [data-testid="stMetricValue"] { font-size: 20px !important; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">🎭 회비 납부 현황 조회</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">성함과 생년월일 6자리를 입력해 주세요.</p>', unsafe_allow_html=True)
st.markdown("---")

# 2. 구글 시트 연결 (Secrets에 주소 넣으셨죠?)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read()
    # 모든 열 이름의 공백 및 줄바꿈 정리
    df.columns = [str(c).replace('\n', '').strip() for c in df.columns]
except Exception as e:
    st.error("데이터 연결 오류입니다. 담당자에게 연락부탁드립니다. 070-4820-2709")
    st.stop()

# 3. 조회 폼
with st.form("search_form", clear_on_submit=True):
    name_input = st.text_input("성함", placeholder="예: 홍길동")
    birth_input = st.text_input("생년월일 6자리", placeholder="예: 900101", max_chars=6)
    submit = st.form_submit_button("조회하기")

if submit:
    if name_input and len(birth_input) == 6:
        # 검색 로직 (공백 무시)
        match = df[
            (df['성명'].str.replace(' ', '').str.strip() == name_input.replace(' ', '').strip()) & 
            (df['생년월일'].str.contains(birth_input.strip()))
        ]
        
        if not match.empty:
            res = match.iloc[0]
            st.success(f"✅ {name_input} 회원님의 정보가 확인되었습니다.")
            
            # 원로회원 안내 (원로 칸에 데이터가 있는 경우)
            elder_col = next((c for c in df.columns if '원로' in c), None)
            if elder_col and str(res[elder_col]).strip().lower() not in ['nan', '', '0', 'none']:
                st.warning("⚠️ 원로회원 변경 요청 문의필요 070-765-6503")

           # 미납 금액 로직 (0, -, 빈칸 모두 완납으로 처리!)
            fee_col = "2026년 기준 미납"
            if fee_col in df.columns:
                # 데이터 정리: 소문자로 바꾸고 앞뒤 공백 제거
                raw_val = str(res[fee_col]).strip().lower()
                
                # 숫자만 남기기 (콤마, 원, .0 등 제거)
                clean_val = raw_val.replace(',', '').replace('원', '').replace('.0', '')
                
                col1, col2 = st.columns(2)
                
                # 🔵 완납으로 판단하는 기준 (여기에 해당하면 모두 완납!)
                # 1. 값이 없거나(nan, none, 빈칸)
                # 2. 하이픈(-)이거나
                # 3. 숫자가 0이거나
                # 4. '완납', '입금' 등의 단어가 포함된 경우
                is_paid = (
                    raw_val in ['', '-', 'nan', 'none', '0', '0.0'] or 
                    any(word in raw_val for word in ['완납', '완료', '입금', 'paid']) or
                    (clean_val.isdigit() and int(clean_val) == 0)
                )

                if is_paid:
                    with col1: st.metric("2026년 완납 여부", "🔵 완납")
                    with col2: st.metric("납부 예정 금액", "0원")
                
                # 🔴 미납으로 판단 (숫자가 0보다 큰 경우)
                elif clean_val.isdigit() and int(clean_val) > 0:
                    with col1: st.metric("2026년 완납 여부", "🔴 미납")
                    with col2: st.metric("납부 예정 금액", f"{format(int(clean_val), ',')}원")
                
                # 그 외 (정말 알 수 없는 데이터가 들어있는 경우)
                else:
                    with col1: st.metric("2026년 완납 여부", "🔴 미납")
                    with col2: st.metric("납부 예정 금액", "문의필요")
            
            # 소속 정보 (비어있으면 출력 안 함)
            def clean(val):
                v = str(val).strip()
                return "" if v.lower() in ['nan', 'none', ''] else v
            
            branch = clean(res.get('소속지부', ''))
            troupe = clean(res.get('소속극단', ''))
            if branch or troupe:
                st.info(f"**소속:** {branch} {'/' if branch and troupe else ''} {troupe}")
        else:
            st.warning("일치하는 정보가 없습니다. 다시 확인해 주세요.")
    else:
        st.warning("성함과 생년월일 6자리를 올바르게 입력해 주세요.")


