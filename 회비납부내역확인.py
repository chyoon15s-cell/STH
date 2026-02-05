if not match.empty:
            res = match.iloc[0]
            st.success(f"✅ {name_input} 회원님의 정보가 확인되었습니다.")
            
            # 1. 2026년 미납액 열 데이터 가져오기
            fee_col = "2026년 기준 미납"
            raw_val = str(res.get(fee_col, '0')).strip() # 원본 데이터
            lower_val = raw_val.lower() # 판정용 소문자 데이터
            
            # 🛑 [핵심] 해당 칸에 "원로"라는 단어가 포함되어 있는지 확인
            if "원로" in raw_val:
                st.markdown("---")
                st.markdown(f"""
                    <div style="text-align: center; padding: 30px; background-color: #fff5f5; border-radius: 20px; border: 2px solid #d32f2f;">
                        <h2 style="color: #d32f2f; margin-bottom: 15px;">🎭 {name_input} 선생님</h2>
                        <h3 style="color: #333; line-height: 1.6;">협회 원로 회원 분이십니다.<br>감사합니다.</h3>
                    </div>
                """, unsafe_allow_html=True)
            
            # 2. "원로"가 아닌 일반 회원 처리
            else:
                # 숫자만 남기기 (콤마, 원, .0 등 제거)
                clean_val = lower_val.replace(',', '').replace('원', '').replace('.0', '')
                
                # 완납 판정 (0이거나 '완납', '입금' 등의 단어가 있는 경우)
                is_paid = (
                    lower_val in ['', '-', 'nan', 'none', '0', '0.0'] or 
                    any(word in lower_val for word in ['완납', '완료', '입금']) or
                    (clean_val.isdigit() and int(clean_val) == 0)
                )

                c1, c2 = st.columns(2)
                if is_paid:
                    c1.metric("2026년 완납 여부", "🔵 완납")
                    c2.metric("납부 예정 금액", "0원")
                else:
                    if clean_val.isdigit() and int(clean_val) > 0:
                        c1.metric("2026년 완납 여부", "🔴 미납")
                        c2.metric("납부 예정 금액", f"{format(int(clean_val), ',')}원")
                    else:
                        c1.metric("2026년 완납 여부", "🔴 미납")
                        c2.metric("납부 예정 금액", "문의 필요")
