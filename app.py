import streamlit as st
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="WIA Global Tracker", page_icon="⚙️", layout="centered")

# --- [DESIGN: CSS 스타일 적용] ---
st.markdown("""
    <style>
    /* [요청하신 부분] 이미지 배경을 강제로 투명하게 설정 */
    img {
        background-color: transparent !important;
    }

    /* 메인 버튼 스타일 (네이비 블루) */
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
    
    /* 섹션 헤더 스타일 */
    .info-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #003366;
        margin-bottom: 10px;
        border-bottom: 2px solid #003366;
        padding-bottom: 5px;
        margin-top: 20px;
    }

    /* 상태 뱃지 스타일 */
    .status-badge {
        padding: 5px 10px;
        border-radius: 15px;
        color: white;
        font-weight: bold;
        text-align: center;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- [설정] 구글 시트 및 데이터 ---
# 구글 시트 링크
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQz_9hUxpSgy0qh_lOwBqB4H4uVubgMNh5qTnhrky4tHSWKkc7HydOCGDAox3K-yDTtRvI0I0Dmh4xs/pub?gid=0&single=true&output=csv"

# 진행 상태 순서 (6단계)
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
        if 'status' in data.columns:
            data['status'] = data['status'].astype(str).str.strip().str.lower()
        return data
    except Exception as e:
        return None

# --- 사이드바 (Sidebar) ---
with st.sidebar:
    # 1. Contact Us (회사 아이콘 🏢)
    st.header("🏢 Contact Us") 
    st.info("""
    **Sales Dept.**
            
    If you have any questions, 
    please contact us.            
    
    **Email:** sales@company.com
    """)
    
    st.write("") 
    st.divider()

    # 2. 로고 위치 (하단 배치)
    # logo.png 파일 사용
    try:
        st.image("logo.png", use_container_width=True) 
    except:
        st.header("WIA MACHINE TOOLS")

    st.caption("© 2025 WIA MACHINE TOOLS")

# --- 메인 화면 (Main Content) ---

# 1. 헤더 영역 (제목 + 기계 아이콘)
c_head_text, c_head_img = st.columns([3.5, 1])

with c_head_text:
    st.title("Order Status Tracker")
    st.markdown("Enter your **SO Number** to track the status.")

with c_head_img:
    # 기계 아이콘 (machine.png)
    try:
        st.image("machine.png", use_container_width=True)
    except:
        st.write("⚙️")

st.write("") # 간격 띄우기

df = load_data()

# 2. 검색창 영역
with st.container(border=True):
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        user_input = st.text_input("SO Number", placeholder="e.g. 40100", label_visibility="collapsed")
    with col_btn:
        search_btn = st.button("TRACK", use_container_width=True)

# 3. 결과 표시 영역
if search_btn or user_input:
    if not user_input:
        st.warning("Please enter a SO Number.")
    else:
        if df is not None:
            search_key = user_input.strip()
            result = df[df['so_number'] == search_key]
            
            if not result.empty:
                row = result.iloc[0]
                
                # 데이터 매핑
                p_name = row.get('product_name', '-')
                client = row.get('client_name', '-')
                status = row.get('status', 'unknown')
                prod_date = row.get('prod_date', '-')
                etd = row.get('ETD', '-')
                eta = row.get('ETA', '-')
                remarks = row.get('remarks', '-')

                # --- 결과 카드 디자인 ---
                st.markdown("#### 🔍 Tracking Result")
                
                with st.container(border=True):
                    # (1) 타이틀 & 뱃지
                    c_title, c_badge = st.columns([3, 1])
                    with c_title:
                        st.markdown(f"### {p_name}")
                        st.caption(f"Client: **{client}** | SO No: **{search_key}**")
                    
                    with c_badge:
                        # 상태별 뱃지 색상 지정
                        badge_color = "#6c757d" # 기본(회색)
                        if status == "sold": badge_color = "#28a745"       # 초록
                        elif status == "stock": badge_color = "#17a2b8"    # 청록
                        elif status == "arrived": badge_color = "#ffc107"  # 노랑
                        elif status == "shipping": badge_color = "#007bff" # 파랑
                        elif status == "in production": badge_color = "#003366" # 네이비
                        
                        st.markdown(f"""
                            <div style="background-color: {badge_color};" class="status-badge">
                                {status.upper()}
                            </div>
                        """, unsafe_allow_html=True)

                    st.divider()

                    # (2) 진행 단계 (6단계)
                    st.markdown("<div class='info-header'>Process Status</div>", unsafe_allow_html=True)
                    
                    progress_percent = 0
                    if status in STEP_ORDER:
                        current_idx = STEP_ORDER.index(status) + 1
                        progress_percent = int((current_idx / len(STEP_ORDER)) * 100)
                    
                    st.progress(progress_percent)
                    
                    # 텍스트 흐름 표시
                    step_labels = " > ".join([s.title() for s in STEP_ORDER])
                    st.caption(f"**Flow:** {step_labels}")
                    st.info(f"Current Phase: **{status.upper()}** ({progress_percent}%)")

                    st.write("") 

                    # (3) 일정 정보
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
                    
                    # (4) 비고 사항
                    if remarks and str(remarks).lower() not in ["nan", "none", "-"]:
                        st.divider()
                        st.markdown("**📝 Remarks**")
                        st.warning(remarks)

            else:
                st.error(f"❌ Order not found: **{search_key}**")
        else:
            st.error("System Error: Connection failed.")