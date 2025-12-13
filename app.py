import streamlit as st
import pandas as pd
import base64

# 1. 페이지 설정
st.set_page_config(page_title="WIA Global Tracker", page_icon="📦", layout="centered")

# --- [함수] 이미지를 Base64 코드로 변환 ---
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- [DESIGN: CSS 스타일 적용] ---
st.markdown("""
    <style>
    /* [폰트] Google Fonts에서 Source Code Pro 폰트 불러오기 */
    @import url('https://fonts.googleapis.com/css2?family=Source+Code+Pro:wght@400;600;700&display=swap');

    /* 이미지 선택/드래그/우클릭 방지 */
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
        white-space: nowrap;
    }

    /* 뱃지 컨테이너 반응형 설정 */
    .badge-container {
        display: flex;
        align-items: center;
        height: 100%;
        justify-content: center; /* PC: 중앙 정렬 */
    }

    /* 모바일 화면(폭 600px 이하) 설정 */
    @media only screen and (max-width: 600px) {
        .badge-container {
            justify-content: flex-start !important; /* 모바일: 왼쪽 정렬 */
            margin-top: 15px;
            margin-left: 5px;
            width: 100%;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- [설정] 구글 시트 링크 ---
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQz_9hUxpSgy0qh_lOwBqB4H4uVubgMNh5qTnhrky4tHSWKkc7HydOCGDAox3K-yDTtRvI0I0Dmh4xs/pub?gid=0&single=true&output=csv"

# 진행 단계 설정 (5단계)
STEP_ORDER = [
    "in production", 
    "ready to deliver", 
    "shipping", 
    "arrived", 
    "stock"
]
# -----------------------

@st.cache_data(ttl=60)
def load_data():
    try:
        data = pd.read_csv(sheet_url)
        
        if 'PO_number' in data.columns:
            data['PO_number'] = data['PO_number'].astype(str).str.strip()
            
        if 'serial_number' in data.columns:
            data['serial_number'] = data['serial_number'].astype(str).str.strip()
            
        if 'status' in data.columns:
            data['status'] = data['status'].astype(str).str.strip().str.lower()
        return data
    except Exception as e:
        return None

# --- 사이드바 ---
with st.sidebar:
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

    st.header("🏢 Contact Us") 
    st.info("""
    **Sales Dept.**
    
    If you have any questions, 
    please contact us.
    
    **📫Email:** sales@company.com
    """)
    
    st.caption("© 2025 WIA MACHINE TOOLS")

# --- 메인 화면 ---

# 헤더 간격 줄이기
st.markdown("""
    <div style="margin-bottom: 5px;">
        <h3 style='color: #003366; margin-bottom: 0; padding-bottom: 0;'>WIA MACHINE TOOLS</h3>
        <h1 style='margin-top: 1px; padding-top: 0;'>Order Status Tracker</h1>
    </div>
    """, unsafe_allow_html=True)

st.markdown("Enter your **PO Number** (e.g. A25..., F25...) to track the status.")

st.write("") 

df = load_data()

# 검색창 영역
with st.container(border=True):
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        user_input = st.text_input("PO Number", placeholder="e.g. A25-08-01", label_visibility="collapsed")
    with col_btn:
        search_btn = st.button("TRACK", use_container_width=True)

# 결과 표시 영역
if search_btn or user_input:
    if not user_input:
        st.warning("Please enter a PO Number.")
    else:
        if df is not None:
            search_key = user_input.strip()
            
            if 'PO_number' in df.columns:
                result = df[df['PO_number'] == search_key]
            else:
                st.error("Error: 'PO_number' column not found in Google Sheet.")
                result = pd.DataFrame()

            if not result.empty:
                row = result.iloc[0]
                
                # 데이터 매핑
                p_name = row.get('product_name', '-')
                client = row.get('client_name', '-')
                serial_val = row.get('serial_number', '-') 
                status = row.get('status', 'unknown')
                prod_date = row.get('prod_date', '-')
                etd = row.get('ETD', '-')
                eta = row.get('ETA', '-')
                remarks = row.get('remarks', '-')

                # --- 결과 카드 ---
                st.markdown("#### 💡 Tracking Result")
                
                with st.container(border=True):
                    c_main, c_badge = st.columns([3, 1])
                    
                    with c_main:
                        try:
                            img_b64 = get_img_as_base64("machine.png")
                        except:
                            img_b64 = ""
                        
                        # [수정됨] HTML 코드 앞의 공백을 완전히 제거하여 마크다운이 코드로 인식하지 않도록 수정함
                        # f-string 안의 내용을 왼쪽 벽에 딱 붙였습니다.
                        st.markdown(f"""<div style="display: flex; align-items: flex-start; gap: 15px;">
<div style="flex-shrink: 0; width: 80px;">
<img src="data:image/png;base64,{img_b64}" style="width: 100%; height: auto; pointer-events: none;">
</div>
<div style="flex-grow: 1;">
<h3 style="margin: 0; padding: 0; font-size: 1.8rem; line-height: 1.2;">{p_name}</h3>
<div style="margin-top: 8px; line-height: 1.2; font-size: 1.2rem;">
<span style="color: #ffffff; font-weight: 500;">Client:</span>
<span style="color: #e0b000; font-weight: bold;">{client}</span>
<br>
<span style="color: #ffffff; font-weight: 500;">Serial No:</span>
<span style="color: #e0b000; font-weight: bold;">{serial_val}</span>
<br>
<span style="color: #ffffff; font-weight: 500;">PO No:</span>
<span style="color: #e0b000; font-weight: bold;">{search_key}</span>
</div>
</div>
</div>""", unsafe_allow_html=True)
                    
                    with c_badge:
                        badge_color = "#6c757d"
                        if status == "sold": badge_color = "#28a745"
                        elif status == "stock": badge_color = "#17a2b8"
                        elif status == "arrived": badge_color = "#ffc107"
                        elif status == "shipping": badge_color = "#007bff"
                        elif status == "in production": badge_color = "#003366"
                        
                        # 여기도 공백 제거
                        st.markdown(f"""<div class="badge-container">
<div style="background-color: {badge_color};" class="status-badge">
{status.upper()}
</div>
</div>""", unsafe_allow_html=True)

                    st.divider()

                    # 진행 단계
                    st.markdown("<div class='info-header'>▣ Process Status</div>", unsafe_allow_html=True)
                    
                    progress_percent = 0
                    if status in STEP_ORDER:
                        current_idx = STEP_ORDER.index(status) + 1
                        progress_percent = int((current_idx / len(STEP_ORDER)) * 100)
                    
                    st.progress(progress_percent)
                    
                    step_labels = " > ".join([s.title() for s in STEP_ORDER])
                    
                    # Flow 텍스트
                    st.markdown(f"""
                        <div style="margin-top: 5px; font-size: 0.9rem; color: #ababab;">
                            <strong style="margin-right: 10px; color: #7d7d7d;">Flow:</strong>
                            {step_labels}
                        </div>
                    """, unsafe_allow_html=True)

                    # Current Phase 박스
                    st.markdown(f"""
                        <div style="
                            background-color: #112e41; 
                            padding: 15px; 
                            border-radius: 5px; 
                            margin-top: 10px; 
                            border: 1px solid #020f17;
                            color: #30a5f3;">
                            <span style="font-weight: bold; font-size: 1.0rem; margin-right: 10px;">Current Phase:</span>
                            <span style="font-weight: 800; font-size: 1.2rem;">{status.upper()}</span>
                        </div>
                    """, unsafe_allow_html=True)

                    st.write("") 

                    # 일정 정보
                    st.markdown("<div class='info-header'>▣ Schedule & Logistics</div>", unsafe_allow_html=True)
                    
                    date_style = "font-size: 1.1rem; font-weight: 600; color: #5ce488; font-family: 'Source Code Pro', monospace;"
                    label_style = "font-weight: bold; margin-bottom: 5px; color: #ecf0f1; display: block;"

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"""
                            <div style="{label_style}">⚙️ Production</div>
                            <div style="{date_style}">📅 {prod_date}</div>
                        """, unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"""
                            <div style="{label_style}">🚢 ETD (Departure)</div>
                            <div style="{date_style}">📅 {etd}</div>
                        """, unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"""
                            <div style="{label_style}">🚢 ETA (Arrival)</div>
                            <div style="{date_style}">📅 {eta}</div>
                        """, unsafe_allow_html=True)
                    
                    # 비고 사항
                    if remarks and str(remarks).lower() not in ["nan", "none", "-"]:
                        st.divider()
                        st.markdown("**🏷️  Remarks**")
                        st.warning(remarks)

            else:
                st.error(f"❌ Order not found: **{search_key}**")
        else:
            st.error("System Error: Connection failed.")