import streamlit as st
import pandas as pd
import base64

# 1. 페이지 설정
st.set_page_config(page_title="WIA Global Tracker", page_icon="📦", layout="centered")

# --- [함수] 이미지를 Base64 코드로 변환 (HTML 삽입용) ---
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- [DESIGN: CSS 스타일 적용] ---
st.markdown("""
    <style>
    /* 이미지 선택/드래그/우클릭 방지 (전역 설정) */
    img {
        pointer-events: none;
        user-select: none;
        -webkit-user-drag: none;
        -webkit-touch-callout: none;
    }

    /* 메인 버튼 스타일 */
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
        color: #30a5f3; 
        margin-bottom: 10px;
        border-bottom: 2px solid #003366;
        padding-bottom: 5px;
        margin-top: 20px;
    }

    /* 상태 뱃지 기본 스타일 */
    .status-badge {
        padding: 8px 16px;
        border-radius: 20px;
        color: white;
        font-weight: bold;
        text-align: center;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        font-size: 0.9rem;
        white-space: nowrap; /* 텍스트 줄바꿈 방지 */
    }

    /* [중요] 뱃지 컨테이너 반응형 설정 */
    .badge-container {
        display: flex;
        align-items: center;
        height: 100%;
        justify-content: center; /* PC: 중앙/우측 정렬 */
    }

    /* 모바일 화면(폭 600px 이하)일 때 뱃지 위치 변경 */
    @media only screen and (max-width: 600px) {
        .badge-container {
            justify-content: flex-start !important; /* 모바일: 왼쪽 정렬 */
            margin-top: 15px;      /* 위쪽 여백 추가 */
            margin-left: 5px;      /* 왼쪽 살짝 여백 */
            width: 100%;           /* 전체 너비 사용 */
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- [설정] 구글 시트 및 데이터 ---
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQz_9hUxpSgy0qh_lOwBqB4H4uVubgMNh5qTnhrky4tHSWKkc7HydOCGDAox3K-yDTtRvI0I0Dmh4xs/pub?gid=0&single=true&output=csv"

STEP_ORDER = [
    "in production", "ready to deliver", "shipping", 
    "arrived", "stock", "sold"
]
# -----------------------

@st.cache_data(ttl=60)
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
    # 1. 로고 (상단 배치 & 선택 방지)
    try:
        logo_b64 = get_img_as_base64("logo.png")
        st.markdown(
            f'<img src="data:image/png;base64,{logo_b64}" style="width: 100%; max-width: 200px; pointer-events: none;">', 
            unsafe_allow_html=True
        )
    except:
        st.header("WIA MACHINE TOOLS")
    
    st.write("") 
    st.divider()

    # 2. Contact Us
    st.header("🏢 Contact Us") 
    st.info("""
    **Sales Dept.**
    
    If you have any questions, 
    please contact us.
    
    **📌Email:** sales@company.com
    """)
    
    st.caption("© 2025 WIA MACHINE TOOLS")

# --- 메인 화면 (Main Content) ---

# 1. 헤더 영역
st.title("Order Status Tracker")
st.markdown("Enter your **SO Number** to track the status.")

st.write("") 

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
                    # c_main(정보 영역) : c_badge(뱃지 영역)
                    # 모바일에서는 c_badge가 c_main 아래로 자연스럽게 내려감
                    c_main, c_badge = st.columns([3, 1])
                    
                    with c_main:
                        try:
                            img_b64 = get_img_as_base64("machine.png")
                        except:
                            img_b64 = ""

                        # HTML Flexbox: 아이콘과 텍스트를 가로로 배치 (모바일에서도 유지)
                        st.markdown(f"""
                        <div style="display: flex; align-items: flex-start; gap: 15px;">
                            <div style="flex-shrink: 0; width: 80px;">
                                <img src="data:image/png;base64,{img_b64}" style="width: 100%; height: auto; pointer-events: none;">
                            </div>
                            <div style="flex-grow: 1;">
                                <h3 style="margin: 0; padding: 0; font-size: 1.5rem; line-height: 1.2;">{p_name}</h3>
                                <div style="color: #c79f00; font-weight: 500; font-size: 0.95rem; margin-top: 8px; line-height: 1.5;">
                                    Client: <b>{client}</b><br>
                                    Serial No: <b>{search_key}</b>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with c_badge:
                        badge_color = "#6c757d"
                        if status == "sold": badge_color = "#28a745"
                        elif status == "stock": badge_color = "#17a2b8"
                        elif status == "arrived": badge_color = "#ffc107"
                        elif status == "shipping": badge_color = "#007bff"
                        elif status == "in production": badge_color = "#003366"
                        
                        # 반응형 클래스 'badge-container' 적용
                        st.markdown(f"""
                            <div class="badge-container">
                                <div style="background-color: {badge_color};" class="status-badge">
                                    {status.upper()}
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                    st.divider()

                    # (2) 진행 단계
                    st.markdown("<div class='info-header'>Process Status</div>", unsafe_allow_html=True)
                    
                    progress_percent = 0
                    if status in STEP_ORDER:
                        current_idx = STEP_ORDER.index(status) + 1
                        progress_percent = int((current_idx / len(STEP_ORDER)) * 100)
                    
                    st.progress(progress_percent)
                    
                    step_labels = " > ".join([s.title() for s in STEP_ORDER])
                    st.caption(f"**Flow:** {step_labels}")
                    # (% 숫자 삭제됨)
                    st.info(f"Current Phase: **{status.upper()}**")

                    st.write("") 

                    # (3) 일정 정보
                    st.markdown("<div class='info-header'>Schedule & Logistics</div>", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown("**⚙️ Production**")
                        st.markdown(f"📅 `{prod_date}`")
                    with col2:
                        st.markdown("**🚢 ETD (Departure)**")
                        st.markdown(f"📅 `{etd}`")
                    with col3:
                        st.markdown("**🚢 ETA (Arrival)**")
                        st.markdown(f"📅 `{eta}`")
                    
                    # (4) 비고 사항
                    if remarks and str(remarks).lower() not in ["nan", "none", "-"]:
                        st.divider()
                        st.markdown("**✅ Remarks**")
                        st.warning(remarks)

            else:
                st.error(f"❌ Order not found: **{search_key}**")
        else:
            st.error("System Error: Connection failed.")