import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. ตั้งค่าหน้าจอและดีไซน์ ---
st.set_page_config(page_title="Science Booking System", layout="wide")

# --- 2. ระบบฐานข้อมูล SQLite (ต้องทำก่อนเริ่มวาดหน้าเว็บ) ---
def init_db():
    conn = sqlite3.connect('local_booking.db', check_same_thread=False)
    c = conn.cursor()
    # สร้างตารางเตรียมไว้ก่อนเสมอ
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, status TEXT, phone TEXT, faculty TEXT, 
        purpose TEXT, start_date DATE, end_date DATE, 
        tool_name TEXT, asset_id TEXT, state TEXT DEFAULT 'Active'
    )''')
    conn.commit()
    return conn

# เรียกใช้งานฐานข้อมูลทันทีที่เปิดแอป
db_conn = init_db()

# ฟังก์ชันตรวจสอบการจองซ้ำ
def check_overlap(asset_id, start, end):
    query = """SELECT name FROM bookings 
               WHERE asset_id = ? AND state = 'Active' 
               AND (? <= end_date AND ? >= start_date)"""
    # ใช้คอนเนคชั่นที่สร้างไว้ตอนต้น
    df = pd.read_sql_query(query, db_conn, params=(asset_id, str(end), str(start)))
    return df

# --- 3. CSS สำหรับลายน้ำโมเลกุลและดีไซน์ ---
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .watermark-container {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        z-index: -1; pointer-events: none; overflow: hidden; opacity: 0.08;
    }
    .molecule {
        position: absolute; font-family: 'Courier New', monospace; font-weight: bold;
        color: #34495e; animation: float 20s infinite alternate ease-in-out;
    }
    @keyframes float {
        0% { transform: translate(0, 0) rotate(0deg); }
        100% { transform: translate(60px, 40px) rotate(360deg); }
    }
    .stForm {
        background: white; padding: 2.5rem; border-radius: 20px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.08);
    }
</style>
<div class="watermark-container">
    <div class="molecule" style="top:15%; left:10%; font-size:45px;">H₂O</div>
    <div class="molecule" style="top:45%; left:75%; font-size:65px;">C₆H₁₂O₆</div>
    <div class="molecule" style="top:75%; left:25%; font-size:55px;">NaCl</div>
    <div class="molecule" style="top:25%; left:60%; font-size:40px;">NH₃</div>
</div>
""", unsafe_allow_html=True)

# --- 4. ส่วนประกอบหน้าเว็บ (UI) ---
tabs = st.tabs(["📝 แบบฟอร์มจองใหม่", "📊 ประวัติการจองทั้งหมด"])

with tabs[0]:
    st.title("🧪 ระบบจองเครื่องมือวิทยาศาสตร์")
    st.write("กรอกรายละเอียดเพื่อจองเครื่องมือในระบบฐานข้อมูลส่วนตัว")
    
    with st.form("booking_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("ชื่อ - นามสกุล")
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
                st.error("กรุณากรอกข้อมูลสำคัญให้ครบถ้วน (ชื่อ และ รหัสครุภัณฑ์)")
            else:
                overlap_check = check_overlap(asset_id, start_date, end_date)
                if not overlap_check.empty:
                    st.error(f"❌ เครื่องมือนี้ถูกจองแล้วโดยคุณ {overlap_check.iloc[0]['name']}")
                else:
                    c = db_conn.cursor()
                    c.execute('''INSERT INTO bookings 
                        (name, status, phone, faculty, purpose, start_date, end_date, tool_name, asset_id)
                        VALUES (?,?,?,?,?,?,?,?,?)''', 
                        (name, u_status, phone, faculty, purpose, str(start_date), str(end_date), tool_name, asset_id))
                    db_conn.commit()
                    st.success("✅ บันทึกข้อมูลสำเร็จ!")
                    st.balloons()
                    st.rerun()

with tabs[1]:
    st.title("📂 ตรวจสอบข้อมูลการจอง")
    # อ่านข้อมูลล่าสุดจาก DB
    try:
        all_data = pd.read_sql_query("SELECT * FROM bookings ORDER BY id DESC", db_conn)
        
        if not all_data.empty:
            search = st.text_input("🔍 ค้นหาด้วยชื่อ หรือ รหัสครุภัณฑ์")
            if search:
                all_data = all_data[all_data['name'].str.contains(search, na=False) | 
                                    all_data['asset_id'].str.contains(search, na=False)]
            
            # ปรับแต่งการแสดงผลตาราง
            st.dataframe(all_data, use_container_width=True, hide_index=True)
        else:
            st.info("ยังไม่มีข้อมูลการจองในฐานข้อมูล")
    except Exception as e:
        st.error(f"เกิดข้อผิดพลาดในการโหลดข้อมูล: {e}")
