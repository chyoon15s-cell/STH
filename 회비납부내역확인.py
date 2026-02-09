# ... (상단 디자인 및 안내 문구 부분은 동일)

# 2. 구글 시트 데이터 연결 (ttl=0으로 실시간 데이터 보장)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read(ttl=0)
    # 헤더의 줄바꿈과 공백 제거
    df.columns = [str(c).replace('\n', '').strip() for c in df.columns]
except:
    st.error("데이터를 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.")
    st.stop()

# 3. 조회 폼
with st.form("search_form", clear_on_submit=True):
    col_in1, col_in2 = st.columns(2)
    with col_in1: name_input = st.text_input("성함", placeholder="예: 홍길동")
    with col_in2: birth_input = st.text_input("생년월일 6자리", placeholder="예: 900101", max_chars=6)
    submit = st.form_submit_button("현황 조회하기")

# 4. 결과 출력
if submit:
    if name_input and len(birth_input) == 6:
        # 데이터 전처리: 비교를 위해 공백 제거 및 문자열 변환
        df['성명_clean'] = df['성명'].astype(str).str.replace(' ', '')
        df['생년월일_clean'] = df['생년월일'].astype(str).str.replace('.0', '', regex=False).str.strip()
        
        # 이름과 생년월일 매칭
        match = df[(df['성명_clean'] == name_input.replace(' ', '')) & 
                   (df['생년월일_clean'].str.contains(birth_input))]
        
        if not match.empty:
            res = match.iloc[0]
            st.success(f"✅ {name_input} 회원님의 정보를 확인하였습니다.")
            
            # --- 수정된 헤더 명칭 적용 ---
            grade_val = str(res.get('등급', '')).strip()
            # 열 이름 '회비2026년'으로 직접 가져오기 (가장 확실한 방법)
            fee_val = str(res.get('회비2026년', '0')).strip()
            # ---------------------------

            # 🛑 [핵심 조건] 등급에 "정지"가 있고 회비에 "원로"가 있는 경우
            if "정지" in grade_val and "원로" in fee_val:
                st.markdown("---")
                st.markdown(f"""
                    <div class="elder-box yellow-box">
                        <h2 style="color: #fab005; margin-bottom: 10px;">🎭 {name_input} 선생님</h2>
                        <h3 style="color: #333;">원로(전환대상) 문의 요망</h3>
                        <p style="font-size: 18px; color: #666; font-weight: bold;">문의: 070-4820-2709</p>
                    </div>
                """, unsafe_allow_html=True)
            
            # ⚪ 일반 원로 회원인 경우
            elif "원로" in fee_val:
                st.markdown("---")
                st.markdown(f"""
                    <div class="elder-box red-box">
                        <h2 style="color: #d32f2f; margin-bottom: 10px;">🎭 {name_input} 선생님</h2>
                        <h3 style="color: #333;">협회 원로 회원 분이십니다.<br>감사합니다.</h3>
                    </div>
                """, unsafe_allow_html=True)
            
            # 🟢 일반 회원 판정
            else:
                lower_val = fee_val.lower().replace(',', '').replace('원', '').replace('.0', '')
                is_paid = lower_val in ['', '-', 'nan', 'none', '0', '0.0'] or any(w in lower_val for w in ['완납', '완료', '입금'])
                
                c1, c2 = st.columns(2)
                if is_paid:
                    c1.metric("납부 현황", "✅ 납부 완료")
                    c2.metric("잔여 회비", "0원")
                    st.balloons()
                else:
                    c1.metric("납부 현황", "✔ 납부 대상")
                    if lower_val.isdigit() and int(lower_val) > 0:
                        c2.metric("납부 예정 금액", f"{format(int(lower_val), ',')}원")
                        st.warning(f"ℹ️ {name_input} 회원님, 납부하실 내역이 확인됩니다.")
                    else:
                        c2.metric("납부 예정 금액", "확인 필요")

        else: st.warning("정보를 찾을 수 없습니다. 성함과 생년월일을 다시 확인해 주세요.")
    else: st.error("성함과 생년월일 6자리를 모두 입력해 주세요.")

# ... (하단 동일)
