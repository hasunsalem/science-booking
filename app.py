import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIG & UI DESIGN ---
st.set_page_config(page_title="Science Lab Booking", layout="wide")

# CSS สำหรับลายน้ำและดีไซน์กล่องสีแยกส่วน
st.markdown("""
<style>
    .stApp { background-color: #f8fafc !important; }
    
    /* ลายน้ำโมเลกุลลอยไปมา */
    .molecule-bg {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: 0; pointer-events: none; overflow: hidden; opacity: 0.1;
    }
    .molecule {
        position: absolute; font-family: 'Courier New', monospace; font-weight: 900;
        color: #1e293b; animation: floatAnim 20s infinite alternate ease-in-out;
    }
    @keyframes floatAnim {
        0% { transform: translate(0, 0) rotate(0deg); }
        100% { transform: translate(120px, 60px) rotate(360deg); }
    }

    /* กล่องส่วนที่ 1: โทนน้ำเงิน */
    .section-1-container {
        border-radius: 20px;
        overflow: hidden;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(30, 58, 138, 0.1);
    }
    .section-1-header {
        background: #1e3a8a;
        color: white;
        padding: 15px 25px;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .section-1-body {
        background: #eff6ff; /* น้ำเงินอ่อน */
        padding: 25px;
    }

    /* กล่องส่วนที่ 2: โทนม่วง */
    .section-2-container {
        border-radius: 20px;
        overflow: hidden;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(88, 28, 135, 0.1);
    }
    .section-2-header {
        background: #581c87;
        color: white;
        padding: 15px 25px;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .section-2-body {
        background: #f5f3ff; /* ม่วงอ่อน */
        padding: 25px;
    }

    /* ปรับแต่ง Input ให้เข้ากับโทนสี */
    .stTextInput > div > div > input, .stSelectbox > div > div > div, .stDateInput > div > div > input {
        border-radius: 10px !important;
        border: 1px solid rgba(0,0,0,0.1) !important;
    }
    
    .block-container { position: relative; z-index: 10; }
</style>

<div class="molecule-bg">
    <div class="molecule" style="top:10%; left:5%; font-size:55px;">H₂O</div>
    <div class="molecule" style="top:40%; left:85%; font-size:75px; animation-delay: -5s;">C₆H₁₂O₆</div>
    <div class="molecule" style="top:70%; left:20%; font-size:60px; animation-delay: -10s;">NaCl</div>
    <div class="molecule" style="top:25%; left:65%; font-size:50px; animation-delay: -15s;">NH₃</div>
</div>
""", unsafe_allow_html=True)

# --- 2. DATABASE SYSTEM ---
def init_db():
    conn = sqlite3.connect('lab_booking_v7.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, status TEXT, phone TEXT, faculty TEXT, supervisor TEXT,
        purpose TEXT, location TEXT, start_date DATE, end_date DATE, 
        tool_name TEXT, asset_id TEXT, state TEXT DEFAULT 'Active'
    )''')
    conn.commit()
    return conn
db_conn = init_db()

# --- 3. APP INTERFACE ---
st.markdown("<h1 style='text-align: center; color: #1e293b; margin-bottom: 30px;'>🧪 Science Booking Application</h1>", unsafe_allow_html=True)

tabs = st.tabs(["✍️ แบบฟอร์มการจอง", "📁 รายการประวัติ"])

with tabs[0]:
    if 'item_rows' not in st.session_state: st.session_state.item_rows = 1

    # --- ส่วนที่ 1: รายละเอียดผู้จอง ---
    st.markdown('<div class="section-1-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-1-header">👤 ส่วนที่ 1: รายละเอียดผู้ขอใช้บริการ และวัตถุประสงค์</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-1-body">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("ชื่อ - นามสกุล", placeholder="กรอกชื่อจริง")
        u_status = st.selectbox("สถานะ", ["อาจารย์", "เจ้าหน้าที่", "นักศึกษา"])
        phone = st.text_input("เบอร์โทรศัพท์")
    with col2:
        faculty = st.text_input("สังกัด / คณะ")
        supervisor = st.text_input("อาจารย์ผู้ควบคุม")
        location = st.text_input("สถานที่นำไปใช้")
    
    st.markdown("<br>", unsafe_allow_html=True)
    purpose = st.radio("วัตถุประสงค์การใช้งาน", ["งานวิจัย", "การเรียนการสอน", "อื่นๆ"], horizontal=True)
    
    date_col1, date_col2 = st.columns(2)
    with date_col1:
        start_date = st.date_input("ตั้งแต่วันที่", min_value=datetime.today())
    with date_col2:
        end_date = st.date_input("ถึงวันที่", min_value=start_date)
    
    st.markdown('</div></div>', unsafe_allow_html=True)

    # --- ส่วนที่ 2: รายละเอียดเครื่องมือ ---
    st.markdown('<div class="section-2-container">', unsafe_allow_html=True)
    st.markdown('<div class="section-2-header">🔬 ส่วนที่ 2: รายละเอียดเครื่องมือวิทยาศาสตร์</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-2-body">', unsafe_allow_html=True)
    
    booking_items = []
    for i in range(st.session_state.item_rows):
        st.markdown(f"**รายการที่ {i+1}**")
        it_col1, it_col2 = st.columns([2, 1])
        with it_col1:
            t_n = st.text_input(f"ชื่อเครื่องมือ", key=f"t_n_{i}")
        with it_col2:
            a_i = st.text_input(f"รหัสครุภัณฑ์", key=f"a_i_{i}")
        booking_items.append({"name": t_n, "id": a_i})
    
    if st.button("➕ เพิ่มรายการเครื่องมือ"):
        st.session_state.item_rows += 1
        st.rerun()
        
    st.markdown('</div></div>', unsafe_allow_html=True)

    # ปุ่มยืนยัน
    if st.button("🚀 ยืนยันข้อมูลการจองทั้งหมด", use_container_width=True, type="primary"):
        if not name or not booking_items[0]['id']:
            st.error("⚠️ ข้อมูลไม่ครบ: กรุณาระบุชื่อและรหัสครุภัณฑ์อย่างน้อย 1 รายการ")
        else:
            success_count = 0
            for item in booking_items:
                if item['id']:
                    # ตรวจสอบซ้ำ
                    q = "SELECT name FROM bookings WHERE asset_id = ? AND state = 'Active' AND (? <= end_date AND ? >= start_date)"
                    overlap = pd.read_sql_query(q, db_conn, params=(item['id'], str(end_date), str(start_date)))
                    
                    if not overlap.empty:
                        st.error(f"❌ รายการ {item['name']} ถูกจองแล้วโดยคุณ {overlap.iloc[0]['name']}")
                    else:
                        cursor = db_conn.cursor()
                        cursor.execute('''INSERT INTO bookings 
                            (name, status, phone, faculty, supervisor, purpose, location, start_date, end_date, tool_name, asset_id)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?)''', 
                            (name, u_status, phone, faculty, supervisor, purpose, location, str(start_date), str(end_date), item['name'], item['id']))
                        db_conn.commit()
                        success_count += 1
            if success_count > 0:
                st.success(f"🎊 บันทึกสำเร็จ {success_count} รายการ!")
                st.balloons()

with tabs[1]:
    st.markdown("### 📊 ประวัติการจอง")
    all_data = pd.read_sql_query("SELECT id, name, tool_name, asset_id, start_date, end_date FROM bookings ORDER BY id DESC", db_conn)
    if not all_data.empty:
        st.dataframe(all_data, use_container_width=True, hide_index=True)
    else:
        st.info("ไม่มีข้อมูลการจอง")
