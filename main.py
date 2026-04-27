import streamlit as st
import os
import time

# [기본 설정]
MY_ST_ID = "2026404032"
MY_NAME = "이연우"

st.set_page_config(page_title="헤어스타일 추천 앱", layout="wide")

if 'registered_user' not in st.session_state:
    st.session_state['registered_user'] = None
if 'is_logged_in' not in st.session_state:
    st.session_state['is_logged_in'] = False

# ---------------------------------------------------------
# [캐싱 시연 강화] 로드 시간 측정 및 로그 추가
# ---------------------------------------------------------
@st.cache_data(show_spinner=False) # 기본 스피너는 끄고 커스텀 사용
def get_style_images(style_name):
    # 캐싱 효과를 보여주기 위한 의도적 지연 (최초 로드 시에만 발생)
    time.sleep(1.5) 
    
    image_dir = "images"
    if not os.path.exists(image_dir):
        return []
    
    # 키워드 매칭: '단발, 미디움' -> ['단발', '미디움'] 
    keywords = [k.strip() for k in style_name.replace(',', '~').split('~') if k.strip()]
    
    all_files = os.listdir(image_dir)
    matched_files = []
    for f in all_files:
        if any(kw in f for kw in keywords) and f.lower().endswith(('.png', '.jpg', '.jpeg')):
            matched_files.append(os.path.join(image_dir, f))
            
    # 매칭된 파일 리스트와 현재 시간을 함께 반환 (캐시 시점 확인용)
    return sorted(list(set(matched_files))), time.time()

# 화면 구현
if st.session_state['is_logged_in']:
    st.markdown(f"**제출자:** {MY_NAME} ({MY_ST_ID}) | **계정:** {st.session_state['registered_user']['id']}")
    
    h_col, l_col = st.columns([5, 1])
    with h_col: st.title("💇 헤어스타일 추천")
    with l_col:
        if st.button("로그아웃"):
            st.session_state['is_logged_in'] = False
            st.rerun()

    st.write("---")
    gender = st.radio("성별", ["남자", "여자"], horizontal=True)
    
    c1, c2 = st.columns(2)
    with c1:
        q1 = st.radio("1. 얼굴 길이", ["A. 가로로 길다", "B. 세로로 길다"])
        q2 = st.radio("2. 이마 모양", ["A. 둥글고 높다", "B. 각지고 좁다"])
    with c2:
        if gender == "여자":
            q3 = st.radio("3. 목 길이", ["A. 짧음", "B. 길음"])
            q4 = st.radio("4. 머리카락", ["A. 얇음", "B. 굵음"])
        else:
            q3 = st.radio("3. 광대 부각", ["A. 부각됨", "B. 부각안됨"])
            q4 = st.radio("4. 얼굴형", ["A. 둥근형", "B. 각진형"])

    if st.button("분석 결과 보기"):
        res_key = f"{q1[0]}{q2[0]}{q3[0]}{q4[0]}"
        results = {
            "여자": {
                "AAAA": "단발, 미디움", "AAAB": "미디움, 롱", "AABA": "단발, 중단발", "AABB": "중단발, 미디움",
                "ABAA": "미디움", "ABAB": "미디움, 롱", "ABBA": "중단발, 미디움", "ABBB": "미디움, 롱",
                "BAAA": "숏, 단발", "BAAB": "단발, 중단발", "BABA": "단발", "BABB": "단발, 중단발",
                "BBAA": "숏, 중단발", "BBAB": "중단발, 미디움", "BBBA": "단발", "BBBB": "단발, 중단발"
            },
            "남자": {
                "AAAA": "베이비펌", "AAAB": "가르마펌", "AABA": "댄디컷", "AABB": "가르마펌",
                "ABAA": "크롭컷", "ABAB": "쉐도우펌", "ABBA": "내출럴펌", "ABBB": "가르마펌",
                "BAAA": "댄디컷", "BAAB": "가르마펌", "BABA": "내출럴펌", "BABB": "쉐도우펌",
                "BBAA": "베이비펌", "BBAB": "가르마펌", "BBBA": "크롭컷", "BBBB": "베이비펌"
            }
        }
        
        style = results[gender].get(res_key, "추천 스타일")
        st.success(f"추천 스타일: **{style}**")
        
        # --- 캐싱 시연 로그 ---
        start_time = time.time()
        with st.spinner("이미지 데이터를 확인 중입니다..."):
            imgs, load_id = get_style_images(style)
        end_time = time.time()
        
        duration = end_time - start_time
        if duration < 0.2: # 0.2초 미만으로 걸렸다면 캐시에서 불러온 것
            st.toast(f"⚡ 캐시 데이터를 사용하여 0.01초 만에 로드했습니다!", icon="🚀")
        else:
            st.toast(f"🐢 폴더에서 새 데이터를 읽어왔습니다. (소요시간: {duration:.2f}초)", icon="📂")
        # ---------------------

        if imgs:
            cols = st.columns(len(imgs))
            for i, p in enumerate(imgs):
                with cols[i]:
                    st.image(p, width=300, caption=os.path.basename(p)) 
        else:
            st.warning("매칭되는 이미지가 없습니다.")

else:
    # 로그인 화면 (기존 로직 유지)
    st.title("✂️ 헤어스타일 추천 서비스")
    st.info(f"제출자: {MY_NAME} ({MY_ST_ID})")
    if st.session_state['registered_user'] is None:
        st.subheader("STEP 1: 정보 등록")
        rid = st.text_input("아이디", key="rid")
        rpw = st.text_input("비밀번호", type="password", key="rpw")
        if st.button("등록"):
            if rid and rpw:
                st.session_state['registered_user'] = {"id": rid, "pw": rpw}
                st.rerun()
    else:
        st.subheader("STEP 2: 로그인")
        lid = st.text_input("ID", key="lid")
        lpw = st.text_input("PW", type="password", key="lpw")
        if st.button("로그인"):
            reg = st.session_state['registered_user']
            if lid == reg['id'] and lpw == reg['pw']:
                st.session_state['is_logged_in'] = True
                st.rerun()
            else: st.error("정보 불일치")