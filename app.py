import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIG & MODERN UI ---
st.set_page_config(page_title="Science Lab Booking", layout="wide")

# CSS สำหรับลายน้ำและแถบหัวข้อส่วนที่ 1 & 2
st.markdown("""
<style>
    .stApp { background-color: #f4f7f9 !important; }
    
    /* เลเยอร์ลายน้ำโมเลกุลลอย */
    .molecule-bg {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: 0; pointer-events: none; overflow: hidden; opacity: 0.12;
    }
    .molecule {
        position: absolute; font-family: 'Courier New', monospace; font-weight: 900;
        color: #1a3a5f; animation: floatAnim 20s infinite alternate ease-in-out;
    }
    @keyframes floatAnim {
        0% { transform: translate(0, 0) rotate(0deg); }
        100% { transform: translate(120px, 60px) rotate(360deg); }
    }

    /* ตกแต่งเนื้อหาให้ลอยเหนือลายน้ำ */
    .block-container { position: relative; z-index: 10; }

    /* แถบหัวข้อส่วนที่ 1 (Blue Gradient) */
    .header-bar-1 {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 15px 25px;
        border-radius: 15px 15px 0 0;
        font-size: 1.2rem;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }

    /* แถบหัวข้อส่วนที่ 2 (Purple Gradient) */
    .header-bar-2 {
        background: linear-gradient(90deg, #6b21a8 0%, #a855f7 100%);
        color: white;
        padding: 15px 25px;
        border-radius: 15px 15px 0 0;
        font-size: 1.2rem;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-top: 20px;
    }

    /* คอนเทนเนอร์เนื้อหาใต้แถบ */
    .content-box {
        background: rgba(255, 255, 255, 0.95);
        padding: 30px;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        margin-bottom: 30px;
        border: 1px solid #e5e7eb;
        border-top: none;
    }
</style>

<div class="molecule-bg">
    <div class="molecule" style="top:10%; left:5%; font-size:50px;">H₂O</div>
    <div class="molecule" style="top:40%; left:80%; font-size:70px; animation-delay: -5s;">C₆H₁₂O₆</div>
    <div class="molecule" style="top:70%; left:15%; font-size:55px; animation-delay: -10s;">NaCl</div>
    <div class="molecule" style="top:20%; left:60%; font-size:45px; animation-delay: -15s;">NH₃</div>
</div>
""", unsafe_allow_html=True)

# --- 2. DATABASE SYSTEM ---
def init_db():
    conn = sqlite3.connect('lab_booking_v5.db', check_same_thread=False)
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

# --- 3. UI LAYOUT ---
tabs = st.tabs(["✨ แบบฟอร์มการจอง", "📋 ตรวจสอบข้อมูล"])

with tabs[0]:
    st.markdown("<h1 style='text-align: center; color: #1e3a8a; margin-bottom: 30px;'>🧪 ระบบจองเครื่องมือออนไลน์</h1>", unsafe_allow_html=True)

    if 'rows' not in st.session_state: st.session_state.rows = 1

    # --- ส่วนที่ 1: รายละเอียดผู้ขอใช้บริการ ---
    st.markdown('<div class="header-bar-1">👤 ส่วนที่ 1: รายละเอียดผู้ขอใช้บริการ และวัตถุประสงค์</div>', unsafe_allow_html=True)
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("ชื่อ - นามสกุล", placeholder="กรอกชื่อ-สกุล")
        u_status = st.selectbox("สถานะ", ["อาจารย์", "เจ้าหน้าที่", "นักศึกษา"])
        phone = st.text_input("เบอร์โทรศัพท์")
    with c2:
        faculty = st.text_input("สังกัด / คณะ")
        supervisor = st.text_input("อาจารย์ผู้ควบคุม")
        location = st.text_input("สถานที่นำไปใช้")
    
    purpose = st.radio("วัตถุประสงค์การใช้", ["งานวิจัย", "การเรียนการสอน", "อื่นๆ"], horizontal=True)
    
    d1, d2 = st.columns(2)
    with d1:
        start_date = st.date_input("ตั้งแต่วันที่", min_value=datetime.today())
    with d2:
        end_date = st.date_input("ถึงวันที่", min_value=start_date)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- ส่วนที่ 2: รายละเอียดเครื่องมือวิทยาศาสตร์ ---
    st.markdown('<div class="header-bar-2">🔬 ส่วนที่ 2: รายละเอียดเครื่องมือวิทยาศาสตร์ และรหัสครุภัณฑ์</div>', unsafe_allow_html=True)
    st.markdown('<div class="content-box">', unsafe_allow_html=True)
    
    tools_list = []
    for i in range(st.session_state.rows):
        st.markdown(f"**รายการจองที่ {i+1}**")
        t1, t2 = st.columns([2, 1])
        with t1:
            t_name = st.text_input(f"ชื่อเครื่องมือ", key=f"t_name_{i}")
        with t2:
            a_id = st.text_input(f"รหัสครุภัณฑ์", key=f"a_id_{i}")
        tools_list.append({"name": t_name, "id": a_id})
    
    if st.button("➕ เพิ่มรายการเครื่องมือใหม่"):
        st.session_state.rows += 1
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ปุ่มส่งข้อมูล
    if st.button("🚀 ยืนยันการส่งข้อมูลจองทั้งหมด", use_container_width=True, type="primary"):
        if not name or not tools_list[0]['id']:
            st.error("❌ ข้อมูลไม่ครบ: กรุณาระบุชื่อผู้จองและรหัสครุภัณฑ์อย่างน้อย 1 รายการ")
        else:
            success_count = 0
            for item in tools_list:
                if item['id']:
                    # ตรวจสอบทับซ้อน
                    q = "SELECT name FROM bookings WHERE asset_id = ? AND state = 'Active' AND (? <= end_date AND ? >= start_date)"
                    overlap = pd.read_sql_query(q, db_conn, params=(item['id'], str(end_date), str(start_date)))
                    
                    if not overlap.empty:
                        st.error(f"⚠️ รายการ {item['name']} ({item['id']}) มีผู้จองแล้วโดยคุณ {overlap.iloc[0]['name']}")
                    else:
                        cursor = db_conn.cursor()
                        cursor.execute('''INSERT INTO bookings 
                            (name, status, phone, faculty, supervisor, purpose, location, start_date, end_date, tool_name, asset_id)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?)''', 
                            (name, u_status, phone, faculty, supervisor, purpose, location, str(start_date), str(end_date), item['name'], item['id']))
                        db_conn.commit()
                        success_count += 1
            if success_count > 0:
                st.success(f"🎉 บันทึกการจองสำเร็จ {success_count} รายการ!")
                st.balloons()

with tabs[1]:
    st.markdown("### 📊 ตารางประวัติการจอง")
    data = pd.read_sql_query("SELECT id, name, tool_name, asset_id, start_date, end_date FROM bookings ORDER BY id DESC", db_conn)
    if not data.empty:
        st.dataframe(data, use_container_width=True, hide_index=True)
    else:
        st.info("ไม่มีข้อมูลการจอง")
