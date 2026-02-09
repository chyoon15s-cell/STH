import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. 페이지 설정 및 디자인
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
    .motto-main { font-size: 19px; font-weight: 700; color: #333; margin-bottom: 12px; }
    .motto-sub { color: #555; font-size: 15.5px; line-height: 1.7; margin: 0; word-break: keep-all; }
    .elder-box { text-align: center; padding: 30px; border-radius: 20px; margin-top: 20px; border: 2px solid; }
    .yellow-box { background-color: #fff9db; border-color: #fab005; }
    .red-box { background-color: #fff5f5; border-color: #d32f2f; }
    </style>
    """, unsafe_allow_html=True)

# 🎭 협회 안내 문구
st.markdown(f"""
    <div class="motto-box">
        <p style="color: #b71c1c; font-size: 15px; font-weight: bold; margin-bottom: 10px;">SEOUL THEATER ASSOCIATION</p>
        <p class="motto-main">“우리는 원합니다. 모두의 축제가 되는 연극을”</p>
        <p class="motto-sub">
            서울연극협회는 <b>매해</b> 회원님들께서 납부해 주시는 회비를 기반으로 운영되고 있습니다.<br>
            회원님의 소중한 참여와 성실한 회비 납부는 안정적인 협회 운영을 위한 <b>단단한 기초</b>가 됩니다.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">🎭 회비 납부 현황 조회</p>', unsafe_allow_html=True)

# 💡 공지사항 안내
st.info("💡 생년월일로 확인이 어려우신 분은 아래 홈페이지 공지의 첨부파일을 참고해 주시기 바랍니다.")
st.markdown('<a href="https://stheater.or.kr/community-notice/?bmode=view&idx=169671803&back_url=&t=board&page=1" target="_blank" style="font-size:14px; color:#0066cc; font-weight:bold;">👉 [공지사항] 2026년도 회비 납부 관련 2차 안내 확인하기</a>', unsafe_allow_html=True)
st.write("")

# 2. 구글 시트 데이터 연결
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # 알려주신 헤더 명칭: 등급, 성명, 본명, 소속지부, 지부직위, 소속극단, 소속직위, 분야, 성별, 생년월일, 납부현황, 회비2026년
    df = conn.read(ttl=0) 
    # 컬럼명 정리 (공백 및 줄바꿈 제거)
    df.columns = [str(c).replace('\n', '').strip() for c in df.columns]
except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다. 에러 내용: {e}")
    st.stop()

# 3. 조회 폼
with st.form("search_form", clear_on_submit=False): # 오타 수정을 위해 제출 후에도 입력값 유지
    col_in1, col_in2 = st.columns(2)
    with col_in1: name_input = st.text_input("성함", placeholder="예: 홍길동")
    with col_in2: birth_input = st.text_input("생년월일 6자리", placeholder="예: 900101", max_chars=6)
    submit = st.form_submit_button("현황 조회하기")

# 4. 결과 출력
if submit:
    if name_input and len(birth_input) == 6:
        # 검색용 임시 데이터프레임 복사
        search_df = df.copy()
        
        # 1) 성명 비교용 정리 (공백 제거)
        search_df['성명_match'] = search_df['성명'].astype(str).str.replace(r'\s+', '', regex=True)
        search_name = name_input.replace(' ', '')
        
        # 2) 생년월일 비교용 정리 (가장 중요한 부분!)
        # 날짜 형식이나 숫자 형식에 상관없이 숫자 6자리만 남기도록 처리
        search_df['생년월일_match'] = (
            search_df['생년월일'].astype(str)
            .str.replace(r'\.0$', '', regex=True) # 소수점 제거
            .str.replace(r'[^0-9]', '', regex=True) # 숫자 외 제거 (하이픈 등)
        )
        
        # 입력한 6자리가 포함되어 있는지 확인
        match = search_df[
            (search_df['성명_match'] == search_name) & 
            (search_df['생년월일_match'].str.contains(birth_input))
        ]
        
        if not match.empty:
            res = match.iloc[0]
            st.success(f"✅ {name_input} 회원님의 정보를 확인하였습니다.")
            
            # 값 가져오기
            grade_val = str(res.get('등급', '')).strip()
            fee_val = str(res.get('회비2026년', '0')).strip()
            
            # --- 하단 결과 출력 로직 (원로/정지/일반 판정)은 이전과 동일 ---
            if "정지" in grade_val and "원로" in fee_val:
                st.markdown("---")
                st.markdown(f'<div class="elder-box yellow-box"><h2 style="color: #fab005;">🎭 {name_input} 선생님</h2><h3>원로(전환대상) 문의 요망</h3><p>문의: 070-4820-2709</p></div>', unsafe_allow_html=True)
            elif "원로" in fee_val:
                st.markdown("---")
                st.markdown(f'<div class="elder-box red-box"><h2 style="color: #d32f2f;">🎭 {name_input} 선생님</h2><h3>협회 원로 회원 분이십니다.</h3></div>', unsafe_allow_html=True)
            else:
                clean_fee = "".join(filter(str.isdigit, fee_val))
                is_paid = clean_fee in ["", "0"] or any(w in fee_val for w in ['완납', '완료', '입금'])
                
                c1, c2 = st.columns(2)
                if is_paid:
                    c1.metric("납부 현황", "✅ 납부 완료")
                    c2.metric("잔여 회비", "0원")
                    st.balloons()
                else:
                    c1.metric("납부 현황", "✔ 납부 대상")
                    if clean_fee.isdigit():
                        c2.metric("납부 예정 금액", f"{int(clean_fee):,}원")
                        st.warning(f"ℹ️ {name_input} 회원님, 납부하실 내역이 확인됩니다.")
                    else:
                        c2.metric("납부 예정 금액", "확인 필요")
        else:
            st.warning("정보를 찾을 수 없습니다. 성함과 생년월일을 다시 확인해 주세요.")
            
            # [도와주세요!] 그래도 안 된다면 아래 주석(#)을 지워서 데이터가 어떻게 들어오는지 직접 확인해보세요.
            # st.write("데이터 샘플 (디버깅용):", search_df[['성명', '생년월일', '성명_match', '생년월일_match']].head(10))
