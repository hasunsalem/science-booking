import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. ตั้งค่าหน้าจอและดีไซน์ ---
st.set_page_config(page_title="Science Booking System", layout="wide")

# Custom CSS สำหรับความสวยงามและลายน้ำโมเลกุล
st.markdown("""
<style>
    .main { background-color: #f0f2f6; }
    
    /* ลายน้ำโมเลกุลลอยไปมา */
    .watermark-container {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        z-index: -1; pointer-events: none; overflow: hidden; opacity: 0.06;
    }
    .molecule {
        position: absolute; font-family: sans-serif; font-weight: bold;
        animation: float 25s infinite alternate ease-in-out;
    }
    @keyframes float {
        0% { transform: translate(0, 0) rotate(0deg); }
        100% { transform: translate(80px, 50px) rotate(360deg); }
    }
    
    /* ตกแต่ง Card ให้มีมิติ */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #ffffff; border-radius: 10px 10px 0 0;
        padding: 10px 20px; box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
    }
    .stForm {
        background: white; padding: 30px; border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    }
</style>

<div class="watermark-container">
    <div class="molecule" style="top:10%; left:5%; font-size:50px; animation-delay: 0s;">H₂O</div>
    <div class="molecule" style="top:30%; left:85%; font-size:70px; animation-delay: -5s;">C₆H₁₂O₆</div>
    <div class="molecule" style="top:60%; left:15%; font-size:40px; animation-delay: -10s;">NaCl</div>
    <div class="molecule" style="top:80%; left:70%; font-size:60px; animation-delay: -15s;">NH₃</div>
</div>
""", unsafe_allow_html=True)

# --- 2. ระบบฐานข้อมูล SQLite (จัดการในตัวแอป) ---
def init_db():
    conn = sqlite3.connect('local_booking.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, status TEXT, phone TEXT, faculty TEXT, 
        purpose TEXT, start_date DATE, end_date DATE, 
        tool_name TEXT, asset_id TEXT, state TEXT DEFAULT 'Active'
    )''')
    conn.commit()
    return conn

def check_overlap(asset_id, start, end):
    conn = sqlite3.connect('local_booking.db')
    query = """SELECT name FROM bookings 
               WHERE asset_id = ? AND state = 'Active' 
               AND (? <= end_date AND ? >= start_date)"""
    df = pd.read_sql_query(query, conn, params=(asset_id, str(end), str(start)))
    conn.close()
    return df

# --- 3. ส่วนประกอบหน้าเว็บ (UI) ---
tabs = st.tabs(["📝 แบบฟอร์มจองใหม่", "📊 ประวัติการจองทั้งหมด"])

with tabs[0]:
    st.title("🧪 ระบบจองเครื่องมือวิทยาศาสตร์")
    st.write("บันทึกข้อมูลการจองเครื่องมือในระบบฐานข้อมูลส่วนตัว")
    
    with st.form("booking_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("ชื่อ - นามสกุล", placeholder="สมชาย ใจดี")
            u_status = st.selectbox("สถานะ", ["อาจารย์", "เจ้าหน้าที่", "นักศึกษา"])
            phone = st.text_input("เบอร์โทรศัพท์")
        with col2:
            faculty = st.text_input("สังกัด / คณะ")
            purpose = st.selectbox("วัตถุประสงค์", ["งานวิจัย", "การเรียนการสอน", "อื่นๆ"])
        
        st.divider()
        col3, col4 = st.columns(2)
        with col3:
            tool_name = st.text_input("ชื่อเครื่องมือวิทยาศาสตร์")
            asset_id = st.text_input("รหัสครุภัณฑ์")
        with col4:
            start_date = st.date_input("เริ่มวันที่", min_value=datetime.today())
            end_date = st.date_input("ถึงวันที่", min_value=start_date)
            
        if st.form_submit_button("ยืนยันการจองเครื่องมือ", type="primary"):
            if not name or not asset_id:
                st.error("กรุณากรอกข้อมูลสำคัญให้ครบถ้วน")
            else:
                overlap_check = check_overlap(asset_id, start_date, end_date)
                if not overlap_check.empty:
                    st.error(f"❌ เครื่องมือนี้ถูกจองแล้วโดยคุณ {overlap_check.iloc[0]['name']}")
                else:
                    conn = sqlite3.connect('local_booking.db')
                    c = conn.cursor()
                    c.execute('''INSERT INTO bookings 
                        (name, status, phone, faculty, purpose, start_date, end_date, tool_name, asset_id)
                        VALUES (?,?,?,?,?,?,?,?,?)''', 
                        (name, u_status, phone, faculty, purpose, str(start_date), str(end_date), tool_name, asset_id))
                    conn.commit()
                    conn.close()
                    st.success("✅ บันทึกข้อมูลสำเร็จ!")
                    st.balloons()

with tabs[1]:
    st.title("📂 ตรวจสอบข้อมูลการจอง")
    conn = sqlite3.connect('local_booking.db')
    all_data = pd.read_sql_query("SELECT * FROM bookings ORDER BY id DESC", conn)
    conn.close()
    
    if not all_data.empty:
        # ระบบค้นหาแบบง่าย
        search = st.text_input("🔍 ค้นหาชื่อผู้จอง หรือ รหัสครุภัณฑ์")
        if search:
            all_data = all_data[all_data['name'].str.contains(search) | all_data['asset_id'].str.contains(search)]
        
        st.dataframe(all_data, use_container_width=True)
    else:
        st.info("ยังไม่มีข้อมูลการจองในฐานข้อมูล")

# เริ่มต้นสร้าง DB ถ้ายังไม่มี
