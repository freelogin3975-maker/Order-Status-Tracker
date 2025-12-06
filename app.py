import streamlit as st
import pandas as pd
import time

# 1. Page Configuration
st.set_page_config(page_title="Global Order Tracker", page_icon="✈️", layout="centered")

# --- [CONFIGURATION] ---
# [IMPORTANT] Paste your Google Sheet CSV Link here
sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQz_9hUxpSgy0qh_lOwBqB4H4uVubgMNh5qTnhrky4tHSWKkc7HydOCGDAox3K-yDTtRvI0I0Dmh4xs/pub?gid=0&single=true&output=csv"

# Define the logical order of your status for the Progress Bar
# Must match the exact spelling in your Google Sheet 'status' column
STEP_ORDER = ["in production", "ready to deliver", "shipping", "arrived"]
# -----------------------

@st.cache_data
def load_data():
    try:
        # 여기에 print를 넣어서 터미널에도 로그를 찍어봅니다.
        print(f"링크 연결 시도: {sheet_url}") 
        
        data = pd.read_csv(sheet_url)
        
        if 'so_number' in data.columns:
            data['so_number'] = data['so_number'].astype(str).str.strip()
        return data
    except Exception as e:
        # ▼▼▼ 에러가 나면 화면에 이유를 출력해주는 부분 ▼▼▼
        st.error(f"데이터 로드 실패! 에러 내용을 확인하세요: {e}")
        return None

# Sidebar (Contact Info)
with st.sidebar:
    st.header("📞 Contact Us")
    st.markdown("""
    If you have any questions, 
    please contact us directly.
    
    **Email:** export@company.com  
    **Phone:** +82-2-1234-5678
    """)
    st.divider()
    st.caption("© 2025 Company Name")

# Main Page UI
st.title("✈️ Order Status Tracker")
st.markdown("Please enter your **SO Number** to check the current status.")

# Load Data
df = load_data()

# Search Area
col_search, col_btn = st.columns([4, 1])
with col_search:
    user_input = st.text_input("SO Number", placeholder="e.g. 40100", label_visibility="collapsed")
with col_btn:
    search_btn = st.button("Search", use_container_width=True)

# Search Logic
if search_btn or user_input:
    if not user_input:
        st.warning("Please enter a SO Number.")
    else:
        if df is not None:
            # Remove spaces from input
            search_key = user_input.strip()
            
            # Find the row
            result = df[df['so_number'] == search_key]
            
            if not result.empty:
                row = result.iloc[0]
                
                # --- Get Values based on your Image Columns ---
                product_name = row.get('product_name', '-')
                client_name = row.get('client_name', '-')
                status = row.get('status', 'Unknown')
                prod_date = row.get('prod_date', '-')
                etd = row.get('ETD', '-') # Estimated Time of Departure
                eta = row.get('ETA', '-') # Estimated Time of Arrival
                remarks = row.get('remarks', '')

                # --- Display Result ---
                st.divider()
                st.subheader(f"📦 Order Details : {search_key}")
                
                # Client & Product Info
                c1, c2 = st.columns(2)
                c1.info(f"**Product Name**\n\n{product_name}")
                c2.info(f"**Client**\n\n{client_name}")

                # --- Progress Bar Logic ---
                st.markdown("### Current Status")
                
                # Calculate Progress
                progress_percent = 0
                if status in STEP_ORDER:
                    current_idx = STEP_ORDER.index(status) + 1
                    progress_percent = int((current_idx / len(STEP_ORDER)) * 100)
                elif status == "stock": 
                    # Special handling for 'stock' (Treat as fully ready 100% or separate?)
                    progress_percent = 50 
                
                # Draw Progress Bar
                st.progress(progress_percent)
                
                # Status Badge
                if status == "arrived":
                    st.success(f"📌 Status: **{status.upper()}**")
                elif status == "shipping":
                    st.info(f"🚢 Status: **{status.upper()}**")
                else:
                    st.warning(f"⚙️ Status: **{status.upper()}**")

                # --- Schedule Details (Dates) ---
                st.markdown("### 🗓️ Schedule")
                d1, d2, d3 = st.columns(3)
                with d1:
                    st.write("**Production Date**")
                    st.caption(prod_date)
                with d2:
                    st.write("**ETD (Departure)**")
                    st.caption(etd)
                with d3:
                    st.write("**ETA (Arrival)**")
                    st.caption(eta)
                
                # Remarks (if exists)
                if remarks and str(remarks) != "nan":
                    st.warning(f"**📝 Remarks:** {remarks}")

            else:
                st.error(f"❌ No order found for SO Number: **{search_key}**")
                st.markdown("Please check your number and try again.")
        else:
            st.error("Connection Error: Unable to load data.")