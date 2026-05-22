import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- การตั้งค่าหน้าจอและธีม ---
st.set_page_config(page_title="Science Booking System", layout="wide")

# --- CUSTOM CSS (สำหรับดีไซน์และลายน้ำโมเลกุล) ---
st.markdown("""
<style>
    /* พื้นหลังและลายน้ำโมเลกุล */
    .main {
        background-color: #f8f9fa;
        background-image: 
            url('https://www.transparenttextures.com/patterns/carbon-fibre.png');
    }
    
    /* สร้างลายน้ำโมเลกุลลอยไปมา */
    .watermark {
        position: fixed;
        top: 0; left: 0; width: 100%; height: 100%;
        z-index: -1;
        opacity: 0.05;
        pointer-events: none;
        overflow: hidden;
    }
    
    .molecule {
        position: absolute;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
        color: #2c3e50;
        animation: float 20s infinite linear;
    }

    @keyframes float {
        0% { transform: translate(0, 0) rotate(0deg); opacity: 0.2; }
        50% { transform: translate(100px, 100px) rotate(180deg); opacity: 0.5; }
        100% { transform: translate(0, 0) rotate(360deg); opacity: 0.2; }
    }

    /* ตกแต่ง Card */
    .stForm {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
</style>

<div class="watermark">
    <div class="molecule" style="top:10%; left:10%; font-size:40px;">H₂O</div>
    <div class="molecule" style="top:40%; left:80%; font-size:60px;">C₆H₁₂O₆</div>
    <div class="molecule" style="top:70%; left:20%; font-size:50px;">NaCl</div>
    <div class="molecule" style="top:20%; left:60%; font-size:30px;">CH₄</div>
    <div class="molecule" style="top:85%; left:75%; font-size:45px;">CO₂</div>
</div>
""", unsafe_allow_html=True)

# --- ส่วนฐานข้อมูล (Google Sheets) ---
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(worksheet="Sheet1", ttl=0)

# --- ฟังก์ชันเช็คการจอง ---
def check_overlap(df, asset_id, start_date, end_date):
    if df.empty: return None
    df['start_date'] = pd.to_datetime(df['start_date']).dt.date
    df['end_date'] = pd.to_datetime(df['end_date']).dt.date
    mask = (df['asset_id'] == asset_id) & (df['status'] != 'Cancelled') & \
           (pd.to_datetime(start_date).date() <= df['end_date']) & \
           (pd.to_datetime(end_date).date() >= df['start_date'])
    overlap = df[mask]
    return overlap.iloc[0] if not overlap.empty else None

# --- การแบ่งหน้า (Navigation) ---
tabs = st.tabs(["📝 แบบฟอร์มจองเครื่องมือ", "🔍 ตรวจสอบและประวัติการจอง"])

# --- หน้าที่ 1: แบบฟอร์มจอง ---
with tabs[0]:
    st.title("🧪 จองเครื่องมือวิทยาศาสตร์")
    st.caption("กรุณากรอกข้อมูลให้ครบถ้วนเพื่อทำการจองในระบบ")
    
    with st.form("modern_booking_form"):
        st.subheader("👤 ข้อมูลผู้จอง")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("ชื่อ - นามสกุล", placeholder="ระบุชื่อจริง-นามสกุล")
            u_status = st.selectbox("สถานะผู้ใช้งาน", ["อาจารย์", "เจ้าหน้าที่", "นักศึกษา"])
        with col2:
            phone = st.text_input("เบอร์โทรศัพท์ที่ติดต่อได้")
            faculty = st.text_input("สังกัด / คณะ")
            
        st.subheader("⚙️ รายละเอียดการใช้งาน")
        purpose = st.radio("วัตถุประสงค์", ["งานวิจัย", "การเรียนการสอน", "อื่นๆ"], horizontal=True)
        
        col3, col4 = st.columns(2)
        with col3:
            start_date = st.date_input("วันที่เริ่มใช้", min_value=datetime.today())
        with col4:
            end_date = st.date_input("วันที่ส่งคืน", min_value=start_date)

        st.subheader("🔬 รายละเอียดเครื่องมือ")
        tool_name = st.text_input("ชื่อเครื่องมือวิทยาศาสตร์")
        asset_id = st.text_input("รหัสครุภัณฑ์ (Asset ID)")

        if st.form_submit_button("ส่งข้อมูลการจอง"):
            if not name or not asset_id:
                st.warning("⚠️ กรุณากรอกข้อมูลที่จำเป็นให้ครบถ้วน")
            else:
                overlap = check_overlap(df, asset_id, start_date, end_date)
                if overlap is not None:
                    st.error(f"🚫 เครื่องมือรหัส {asset_id} ถูกจองแล้วในช่วงเวลานี้")
                else:
                    new_entry = pd.DataFrame([{
                        "name": name, "user_status": u_status, "phone": phone, 
                        "faculty": faculty, "purpose": purpose, 
                        "start_date": str(start_date), "end_date": str(end_date),
                        "tool_name": tool_name, "asset_id": asset_id, "status": "Active"
                    }])
                    updated_df = pd.concat([df, new_entry], ignore_index=True)
                    conn.update(worksheet="Sheet1", data=updated_df)
                    st.success("🎉 บันทึกการจองสำเร็จ! คุณสามารถตรวจสอบสถานะได้ในหน้าถัดไป")
                    st.balloons()

# --- หน้าที่ 2: ประวัติการจอง ---
with tabs[1]:
    st.title("📊 ประวัติและสถานะการจอง")
    st.write("รายการจองทั้งหมดที่บันทึกอยู่ในระบบปัจจุบัน")
    
    # ช่องค้นหา (Search)
    search_query = st.text_input("🔍 ค้นหาด้วยชื่อผู้จอง หรือ รหัสครุภัณฑ์")
    
    display_df = df.copy()
    if search_query:
        display_df = display_df[display_df['name'].str.contains(search_query) | 
                                display_df['asset_id'].str.contains(search_query)]
    
    # จัดการการแสดงผลตารางให้สวยงาม
    if not display_df.empty:
        st.dataframe(display_df, use_container_width=True)
    else:
        st.info("ยังไม่มีข้อมูลการจองในขณะนี้")
