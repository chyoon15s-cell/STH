import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. 페이지 설정 및 세련된 디자인 적용
st.set_page_config(page_title="서울연극협회 회비 조회", layout="centered")

st.markdown("""
    <style>
    .main-title { font-size: 26px !important; font-weight: bold; color: #1a1a1a; margin-bottom: 10px; }
    .motto-box { 
        background-color: #fcfcfc; 
        padding: 25px; 
        border-radius: 15px; 
        border-left: 6px solid #b71c1c; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 30px;
    }
    .motto-header { color: #b71c1c; font-size: 15px; font-weight: bold; letter-spacing: 1px; margin-bottom: 10px; }
    .motto-main { font-size: 19px; font-weight: 700; color: #333; margin-bottom: 12px; }
    .motto-sub { color: #555; font-size: 15.5px; line-height: 1.7; margin: 0; word-break: keep-all; }
    </style>
    """, unsafe_allow_html=True)

# 🎭 협회 안내 문구 (채윤님 최종 확정본)
st.markdown(f"""
    <div class="motto-box">
        <p class="motto-header">SEOUL THEATER ASSOCIATION</p>
        <p class="motto-main">“우리는 원합니다. 모두의 축제가 되는 연극을”</p>
        <p class="motto-sub">
            서울연극협회는 <b>매해</b> 회원님들께서 납부해 주시는 회비를 기반으로 운영되고 있습니다.<br>
            회원님의 소중한 참여와 성실한 회비 납부는 안정적인 협회 운영을 위한 <b>단단한 기초</b>가 됩니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">🎭 회비 납부 현황 조회</p>', unsafe_allow_html=True)

# 2. 구글 시트 데이터 연결
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read()
    df.columns = [str(c).replace('\n', '').strip() for c in df.columns]
except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.")
    st.stop()

# 3. 조회 폼 (성함, 생년월일 입력)
with st.form("search_form", clear_on_submit=True):
    col_in1, col_in2 = st.columns(2)
    with col_in1:
        name_input = st.text_input("성함", placeholder="예: 홍길동")
    with col_in2:
        birth_input = st.text_input("생년월일 6자리", placeholder="예: 900101", max_chars=6)
    submit = st.form_submit_button("현황 조회하기")

# 4. 조회 결과 출력 로직
if submit:
    if name_input and len(birth_input) == 6:
        # 데이터 검색
        match = df[
            (df['성명'].str.replace(' ', '').str.strip() == name_input.replace(' ', '').strip()) & 
            (df['생년월일'].astype(str).str.contains(birth_input.strip()))
        ]
        
        if not match.empty:
            res = match.iloc[0]
            st.success(f"✅ {name_input} 회원님의 정보를 확인하였습니다.")
            
            # 회비 데이터 확인
            fee_col = "2026년 기준 미납"
            raw_val = str(res.get(fee_col, '0')).strip()
            lower_val = raw_val.lower()
            
            # 🛑 [경우 1] 원로 회원님 (선생님 예우)
            if "원로" in raw_val:
                st.markdown("---")
                st.markdown(f"""
                    <div style="text-align: center; padding: 30px; background-color: #fff5f5; border-radius: 20px; border: 2px solid #d32f2f;">
                        <h2 style="color: #d32f2f; margin-bottom: 15px;">🎭 {name_input} 선생님</h2>
                        <h3 style="color: #333; line-height: 1.6;">협회 원로 회원 분이십니다.<br>감사합니다.</h3>
                    </div>
                """, unsafe_allow_html=True)
            
            # 🟢 [경우 2] 일반 회원 판정
            else:
                clean_val = lower_val.replace(',', '').replace('원', '').replace('.0', '')
                is_paid = (
                    lower_val in ['', '-', 'nan', 'none', '0', '0.0'] or 
                    any(word in lower_val for word in ['완납', '완료', '입금']) or
                    (clean_val.isdigit() and int(clean_val) == 0)
                )

                c1, c2 = st.columns(2)
                if is_paid:
                    # 완납 시 파란색 체크 표시
                    c1.metric("납부 현황", "✅ 납부 완료")
                    c2.metric("잔여 회비", "0원")
                    st.balloons() # 축하 풍선 팡팡!
                else:
                    # 미납 시 요청하신 문구와 회색 체크 표시 적용
                    c1.metric("납부 현황", "✔ 납부 대상")
                    if clean_val.isdigit() and int(clean_val) > 0:
                        c2.metric("납부 예정 금액", f"{format(int(clean_val), ',')}원")
                        # 💡 부드러운 강조 문구
                        st.warning(f"ℹ️ {name_input} 회원님, 납부하실 내역이 확인됩니다.")
                    else:
                        c2.metric("납부 예정 금액", "확인 필요")
                        st.info("상세 내역 확인을 위해 협회 총무팀으로 문의 부탁드립니다.")
        else:
            st.warning("일치하는 회원 정보가 없습니다. 성함과 생년월일을 다시 확인해 주세요.")
    else:
        st.error("성함과 생년월일 6자리를 모두 입력해 주세요.")

st.markdown("---")
st.caption("문의: 서울연극협회 총무팀 (02-765-7500) | 본 정보는 1월 26일 입금분까지 반영되었습니다.")
