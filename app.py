import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIG & UI DESIGN ---
st.set_page_config(page_title="Science Lab Booking", layout="wide")

# CSS สำหรับลายน้ำและแถบสีที่บรรจุรายละเอียด
st.markdown("""
<style>
    .stApp { background-color: #f8fafc !important; }
    
    /* ลายน้ำโมเลกุล Dynamic */
    .molecule-bg {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: 0; pointer-events: none; overflow: hidden; opacity: 0.1;
    }
    .molecule {
        position: absolute; font-family: 'Courier New', monospace; font-weight: 900;
        color: #1e293b; animation: floatAnim 22s infinite alternate ease-in-out;
    }
    @keyframes floatAnim {
        0% { transform: translate(0, 0) rotate(0deg); }
        100% { transform: translate(150px, 80px) rotate(360deg); }
    }

    /* แถบสีส่วนที่ 1 (Blue) */
    .section-1 {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(59, 130, 246, 0.2);
    }
    
    /* แถบสีส่วนที่ 2 (Purple) */
    .section-2 {
        background: linear-gradient(135deg, #581c87 0%, #a855f7 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(168, 85, 247, 0.2);
    }

    /* ปรับแต่งช่องกรอกข้อมูลในแถบสีให้ดูเด่นขึ้น */
    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 10px !important;
        border: none !important;
    }
    
    label { color: white !important; font-weight: 600 !important; }
    .stRadio label { color: white !important; }
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
    conn = sqlite3.connect('lab_booking_v6.db', check_same_thread=False)
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
st.markdown("<h1 style='text-align: center; color: #1e293b; margin-top: -30px;'>🧪 Science Booking Application</h1>", unsafe_allow_html=True)
tabs = st.tabs(["✍️ แบบฟอร์มจอง", "📁 ประวัติข้อมูล"])

with tabs[0]:
    if 'items' not in st.session_state: st.session_state.items = 1

    # --- ส่วนที่ 1: รายละเอียดผู้จอง (บรรจุในแถบสีน้ำเงิน) ---
    st.markdown('<div class="section-1">', unsafe_allow_html=True)
    st.markdown("### 👤 ส่วนที่ 1: รายละเอียดผู้ขอใช้บริการ")
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("ชื่อ - นามสกุล", placeholder="ระบุชื่อจริง")
        u_status = st.selectbox("สถานะ", ["อาจารย์", "เจ้าหน้าที่", "นักศึกษา"])
        phone = st.text_input("เบอร์โทรศัพท์")
    with c2:
        faculty = st.text_input("สังกัด / คณะ")
        supervisor = st.text_input("อาจารย์ผู้ควบคุม")
        location = st.text_input("สถานที่นำไปใช้")
    
    st.markdown("<br>", unsafe_allow_html=True)
    purpose = st.radio("วัตถุประสงค์การใช้งาน", ["งานวิจัย", "การเรียนการสอน", "อื่นๆ"], horizontal=True)
    
    d1, d2 = st.columns(2)
    with d1:
        start_date = st.date_input("วันที่เริ่มใช้", min_value=datetime.today())
    with d2:
        end_date = st.date_input("วันที่สิ้นสุด", min_value=start_date)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- ส่วนที่ 2: รายละเอียดเครื่องมือ (บรรจุในแถบสีม่วง) ---
    st.markdown('<div class="section-2">', unsafe_allow_html=True)
    st.markdown("### 🔬 ส่วนที่ 2: รายละเอียดเครื่องมือวิทยาศาสตร์")
    
    tool_inputs = []
    for i in range(st.session_state.items):
        st.markdown(f"**เครื่องมือรายการที่ {i+1}**")
        t_col1, t_col2 = st.columns([2, 1])
        with t_col1:
            t_name = st.text_input(f"ชื่อเครื่องมือ", key=f"tool_name_{i}")
        with t_col2:
            a_id = st.text_input(f"รหัสครุภัณฑ์", key=f"asset_id_{i}")
        tool_inputs.append({"name": t_name, "id": a_id})
    
    if st.button("➕ เพิ่มรายการเครื่องมือ"):
        st.session_state.items += 1
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ปุ่ม Submit
    if st.button("🚀 ยืนยันการจองเครื่องมือทั้งหมด", use_container_width=True, type="primary"):
        if not name or not tool_inputs[0]['id']:
            st.error("⚠️ กรุณากรอกชื่อและรหัสครุภัณฑ์อย่างน้อย 1 รายการ")
        else:
            success = 0
            for tool in tool_inputs:
                if tool['id']:
                    # ตรวจสอบการจองซ้ำ
                    q = "SELECT name FROM bookings WHERE asset_id = ? AND state = 'Active' AND (? <= end_date AND ? >= start_date)"
                    overlap = pd.read_sql_query(q, db_conn, params=(tool['id'], str(end_date), str(start_date)))
                    
                    if not overlap.empty:
                        st.error(f"❌ รายการ {tool['name']} ถูกจองแล้วโดยคุณ {overlap.iloc[0]['name']}")
                    else:
                        cur = db_conn.cursor()
                        cur.execute('''INSERT INTO bookings 
                            (name, status, phone, faculty, supervisor, purpose, location, start_date, end_date, tool_name, asset_id)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?)''', 
                            (name, u_status, phone, faculty, supervisor, purpose, location, str(start_date), str(end_date), tool['name'], tool['id']))
                        db_conn.commit()
                        success += 1
            if success > 0:
                st.success(f"🎊 บันทึกการจองสำเร็จ {success} รายการ!")
                st.balloons()

with tabs[1]:
    st.markdown("### 📊 ประวัติการจอง")
    data = pd.read_sql_query("SELECT id, name, tool_name, asset_id, start_date, end_date FROM bookings ORDER BY id DESC", db_conn)
    if not data.empty:
        st.dataframe(data, use_container_width=True, hide_index=True)
    else:
        st.info("ไม่มีข้อมูล")
