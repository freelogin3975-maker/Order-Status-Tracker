import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="WIA Global Tracker", page_icon="⚙️", layout="centered")

# --- [DESIGN: Custom CSS] ---
st.markdown("""
    <style>
    /* 1. 메인 버튼 스타일 (네이비 블루 & 골드) */
    div.stButton > button:first-child {
        background-color: #003366;
        color: white;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: 0.3s;
    }
    div.stButton > button:first-child:hover {
        background-color: #002244;
        color: #FFD700;
        border: 1px solid #FFD700;
    }
    
    /* 2. 전체 레이아웃 패딩 조정 */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    
    /* 3. 섹션 헤더 스타일 */
    .info-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #003366;
        margin-bottom: 10px;
        border-bottom: 2px solid #003366;
        padding-bottom: 5px;
        margin-top: 20px;
    }

    /* 4. 상태 뱃지 스타일 */
    .status-badge {
        padding: 5px 10px;
        border-radius: 15px;
        color: white;
        font-weight: bold;
        text-align: center;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

# --- [CONFIGURATION] ---
# 구글 시트 링크 (기존 링크 유지)
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQz_9hUxpSgy0qh_lOwBqB4H4uVubgMNh5qTnhrky4tHSWKkc7HydOCGDAox3K-yDTtRvI0I0Dmh4xs/pub?gid=0&single=true&output=csv"

# [중요] 진행 상태 순서 정의 (6단계)
# 구글 시트의 'status' 컬럼에 적힐 영어 단어와 정확히 일치해야 합니다.
STEP_ORDER = [
    "in production",    # 1. 생산
    "ready to deliver", # 2. 배송준비
    "shipping",         # 3. 배송중
    "arrived",          # 4. 도착
    "stock",            # 5. 보관
    "sold"              # 6. 출고완료
]
# -----------------------

@st.cache_data
def load_data():
    try:
        data = pd.read_csv(sheet_url)
        if 'so_number' in data.columns:
            data['so_number'] = data['so_number'].astype(str).str.strip()
        # 공백 및 대소문자 처리를 위해 status 정리
        if 'status' in data.columns:
            data['status'] = data['status'].astype(str).str.strip().str.lower()
        return data
    except Exception as e:
        return None

# --- Sidebar ---
with st.sidebar:
    # 1. Contact Us (전화번호 삭제, 아이콘 변경)
    st.header("🏢 Contact Us") 
    st.info("""
    If you have any questions, 
    please contact us.
    
    **Email:** export@company.com  
    """)
    
    st.write("") # 여백 추가
    st.write("") 
    st.divider()

    # 2. Logo & Copyright (위치 변경: 하단 배치)
    # logo.png 파일이 폴더에 있어야 합니다.
    try:
        st.image("logo.png", use_container_width=True) 
    except:
        st.header("WIA MACHINE TOOLS") # 이미지가 없을 경우 텍스트 대체

    st.caption("© 2025 WIA MACHINE TOOLS")

# --- Main Content ---

# 1. Header Area (Icon moved to right)
c_head_text, c_head_img = st.columns([3.5, 1])

with c_head_text:
    st.title("Order Status Tracker")
    st.markdown("Enter your **SO Number** to track the status.")

with c_head_img:
    # machine.png 파일이 폴더에 있어야 합니다.
    try:
        st.image("machine.png", use_container_width=True)
    except:
        st.write("🚜") # 이미지가 없을 경우 이모지 대체

st.write("") # Spacer

df = load_data()

# 2. Search Area
with st.container(border=True):
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        user_input = st.text_input("SO Number", placeholder="e.g. 40100", label_visibility="collapsed")
    with col_btn:
        search_btn = st.button("TRACK", use_container_width=True)

# 3. Result Area
if search_btn or user_input:
    if not user_input:
        st.warning("Please enter a SO Number.")
    else:
        if df is not None:
            search_key = user_input.strip()
            result = df[df['so_number'] == search_key]
            
            if not result.empty:
                row = result.iloc[0]
                
                # Data Mapping
                p_name = row.get('product_name', '-')
                client = row.get('client_name', '-')
                status = row.get('status', 'unknown')
                prod_date = row.get('prod_date', '-')
                etd = row.get('ETD', '-')
                eta = row.get('ETA', '-')
                remarks = row.get('remarks', '-')

                # --- [DESIGN CORE] Result Card ---
                st.markdown("#### 🔍 Tracking Result")
                
                with st.container(border=True):
                    # (1) Title Section
                    c_title, c_badge = st.columns([3, 1])
                    with c_title:
                        st.markdown(f"### {p_name}")
                        st.caption(f"Client: **{client}** | SO No: **{search_key}**")
                    
                    with c_badge:
                        # 상태 뱃지 (색상 구분)
                        badge_color = "#6c757d" # 기본 회색
                        if status == "sold": badge_color = "#28a745" # 초록
                        elif status == "stock": badge_color = "#17a2b8" # 청록
                        elif status == "arrived": badge_color = "#ffc107" # 노랑
                        elif status == "shipping": badge_color = "#007bff" # 파랑
                        elif status == "in production": badge_color = "#003366" # 네이비
                        
                        st.markdown(f"""
                            <div style="background-color: {badge_color};" class="status-badge">
                                {status.upper()}
                            </div>
                        """, unsafe_allow_html=True)

                    st.divider()

                    # (2) Process Status (6단계)
                    st.markdown("<div class='info-header'>Process Status</div>", unsafe_allow_html=True)
                    
                    # 진행률 계산
                    progress_percent = 0
                    if status in STEP_ORDER:
                        # 리스트의 인덱스를 찾아 백분율로 환산 (1단계=16%, 6단계=100%)
                        current_idx = STEP_ORDER.index(status) + 1
                        progress_percent = int((current_idx / len(STEP_ORDER)) * 100)
                    
                    # 프로그레스 바 표시
                    st.progress(progress_percent)
                    
                    # 현재 단계 텍스트 표시
                    step_labels = " > ".join([s.title() for s in STEP_ORDER])
                    st.caption(f"**Flow:** {step_labels}")
                    st.info(f"Current Phase: **{status.upper()}** ({progress_percent}%)")

                    st.write("") 

                    # (3) Schedule Grid
                    st.markdown("<div class='info-header'>Schedule & Logistics</div>", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown("**🏭 Production**")
                        st.markdown(f"📅 `{prod_date}`")
                    with col2:
                        st.markdown("**🛫 ETD (Departure)**")
                        st.markdown(f"📅 `{etd}`")
                    with col3:
                        st.markdown("**🛬 ETA (Arrival)**")
                        st.markdown(f"📅 `{eta}`")
                    
                    # (4) Remarks
                    if remarks and str(remarks).lower() not in ["nan", "none", "-"]:
                        st.divider()
                        st.markdown("**📝 Remarks**")
                        st.warning(remarks)

            else:
                st.error(f"❌ Order not found: **{search_key}**")
        else:
            st.error("System Error: Connection failed.")