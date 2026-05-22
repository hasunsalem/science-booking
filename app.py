import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIG & ADVANCED UI DESIGN ---
st.set_page_config(page_title="Chem Booking - วท.บ.เคมี", layout="wide")

st.markdown("""
<style>
    /* พื้นหลังหลัก */
    .stApp { background-color: #fcfdfe !important; }
    
    /* ลายน้ำโมเลกุล Dynamic Watermark */
    .molecule-bg {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: 0; pointer-events: none; overflow: hidden; opacity: 0.12;
    }
    .molecule {
        position: absolute; font-family: 'Courier New', monospace; font-weight: 900;
        color: #1a365d; animation: floatWave 25s infinite alternate ease-in-out;
    }
    @keyframes floatWave {
        0% { transform: translate(0, 0) rotate(0deg) scale(1); }
        50% { transform: translate(100px, 50px) rotate(180deg) scale(1.1); }
        100% { transform: translate(-50px, 100px) rotate(360deg) scale(1); }
    }

    /* สไตล์กล่องส่วนที่ 1 (น้ำเงิน) */
    .box-1-container { border-radius: 20px; overflow: hidden; margin-bottom: 35px; box-shadow: 0 10px 30px rgba(30,58,138,0.15); border: 1px solid #e2e8f0; }
    .box-1-header { background: linear-gradient(90deg, #1e3a8a, #3b82f6); color: white; padding: 18px 25px; font-size: 1.25rem; font-weight: bold; }
    .box-1-body { background: #f0f7ff; padding: 30px; border-top: 2px solid rgba(255,255,255,0.3); }

    /* สไตล์กล่องส่วนที่ 2 (ม่วง) */
    .box-2-container { border-radius: 20px; overflow: hidden; margin-bottom: 35px; box-shadow: 0 10px 30px rgba(88,28,135,0.15); border: 1px solid #e2e8f0; }
    .box-2-header { background: linear-gradient(90deg, #581c87, #a855f7); color: white; padding: 18px 25px; font-size: 1.25rem; font-weight: bold; }
    .box-2-body { background: #faf5ff; padding: 30px; border-top: 2px solid rgba(255,255,255,0.3); }

    /* ปรับแต่งช่อง Input */
    .stTextInput > div > div > input, .stSelectbox > div > div > div {
        border-radius: 12px !important; border: 1px solid #cbd5e1 !important; background: white !important;
    }
    
    .block-container { position: relative; z-index: 10; padding-top: 2rem; }
    .main-title { font-weight: 800; color: #0f172a; text-align: center; margin-bottom: 5px; }
    .sub-title { text-align: center; color: #475569; font-size: 1.1rem; margin-bottom: 40px; }
</style>

<div class="molecule-bg">
    <div class="molecule" style="top:10%; left:8%; font-size:55px;">H₂O</div>
    <div class="molecule" style="top:45%; left:82%; font-size:75px; animation-delay: -5s;">C₆H₁₂O₆</div>
    <div class="molecule" style="top:75%; left:18%; font-size:60px; animation-delay: -10s;">NaCl</div>
    <div class="molecule" style="top:25%; left:65%; font-size:50px; animation-delay: -15s;">NH₃</div>
    <div class="molecule" style="top:85%; left:70%; font-size:45px; animation-delay: -2s;">CO₂</div>
</div>
""", unsafe_allow_html=True)

# --- 2. DATABASE INITIALIZATION ---
def init_db():
    conn = sqlite3.connect('chem_lab_booking.db', check_same_thread=False)
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

# --- 3. APP MAIN INTERFACE ---
st.markdown("<h1 class='main-title'>ระบบขอใช้เครื่องมือวิทยาศาสตร์</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>หลักสูตร วท.บ. สาขาวิชาเคมี</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 แบบฟอร์มลงทะเบียนจอง", "📋 ตรวจสอบสถานะการจอง"])

with tab1:
    if 'rows_count' not in st.session_state: st.session_state.rows_count = 1

    # --- ส่วนที่ 1: รายละเอียดผู้จอง ---
    st.markdown('<div class="box-1-container">', unsafe_allow_html=True)
    st.markdown('<div class="box-1-header">👤 ส่วนที่ 1: รายละเอียดผู้ขอใช้บริการ และ วัตถุประสงค์</div>', unsafe_allow_html=True)
    st.markdown('<div class="box-1-body">', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("ชื่อ - นามสกุล", placeholder="ตัวอย่าง: นายสมชาย เคมีไทย")
        u_status = st.selectbox("สถานะผู้ขอใช้", ["อาจารย์", "เจ้าหน้าที่", "นักศึกษา"])
        phone = st.text_input("เบอร์โทรศัพท์ติดต่อ")
    with c2:
        faculty = st.text_input("สังกัด / คณะ / สาขาวิชา")
        supervisor = st.text_input("อาจารย์ผู้ควบคุม (Advisor)")
        location = st.text_input("สถานที่นำเครื่องมือไปใช้")
    
    st.markdown("<br>", unsafe_allow_html=True)
    purpose = st.radio("วัตถุประสงค์การใช้งาน", ["งานวิจัย", "การเรียนการสอน (Lab)", "อื่นๆ"], horizontal=True)
    
    d1, d2 = st.columns(2)
    with d1:
        start_date = st.date_input("วันที่เริ่มต้นการใช้", min_value=datetime.today())
    with d2:
        end_date = st.date_input("วันที่ส่งคืน/สิ้นสุด", min_value=start_date)
    st.markdown('</div></div>', unsafe_allow_html=True)

    # --- ส่วนที่ 2: รายละเอียดเครื่องมือ ---
    st.markdown('<div class="box-2-container">', unsafe_allow_html=True)
    st.markdown('<div class="box-2-header">🔬 ส่วนที่ 2: รายละเอียดเครื่องมือวิทยาศาสตร์ และ รหัสครุภัณฑ์</div>', unsafe_allow_html=True)
    st.markdown('<div class="box-2-body">', unsafe_allow_html=True)
    
    items_to_book = []
    for i in range(st.session_state.rows_count):
        st.markdown(f"**🔹 รายการเครื่องมือที่ {i+1}**")
        it1, it2 = st.columns([3, 1])
        with it1:
            t_n = st.text_input(f"ชื่อเครื่องมือ (Chemical Tool Name)", key=f"t_n_{i}")
        with it2:
            a_i = st.text_input(f"รหัสครุภัณฑ์", key=f"a_i_{i}")
        items_to_book.append({"name": t_n, "id": a_i})
    
    if st.button("➕ เพิ่มรายการเครื่องมืออื่น ๆ"):
        st.session_state.rows_count += 1
        st.rerun()
        
    st.markdown('</div></div>', unsafe_allow_html=True)

    if st.button("🚀 ยืนยันข้อมูลการจอง", use_container_width=True, type="primary"):
        if not name or not items_to_book[0]['id']:
            st.error("⚠️ กรุณากรอกข้อมูลผู้จองและรหัสครุภัณฑ์อย่างน้อย 1 รายการ")
        else:
            success = 0
            for item in items_to_book:
                if item['id']:
                    q = "SELECT name FROM bookings WHERE asset_id = ? AND state = 'Active' AND (? <= end_date AND ? >= start_date)"
                    overlap = pd.read_sql_query(q, db_conn, params=(item['id'], str(end_date), str(start_date)))
                    
                    if not overlap.empty:
                        st.error(f"❌ รายการ '{item['name']}' ถูกจองแล้วโดยคุณ {overlap.iloc[0]['name']}")
                    else:
                        cursor = db_conn.cursor()
                        cursor.execute('''INSERT INTO bookings 
                            (name, status, phone, faculty, supervisor, purpose, location, start_date, end_date, tool_name, asset_id)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?)''', 
                            (name, u_status, phone, faculty, supervisor, purpose, location, str(start_date), str(end_date), item['name'], item['id']))
                        db_conn.commit()
                        success += 1
            if success > 0:
                st.success(f"🎉 บันทึกสำเร็จ! ข้อมูลถูกส่งเข้าระบบ วท.บ.เคมี เรียบร้อยแล้ว")
                st.balloons()

with tab2:
    st.markdown("### 📊 ตารางแสดงประวัติการใช้งาน (วท.บ.เคมี)")
    all_data = pd.read_sql_query("SELECT id, name, tool_name, asset_id, start_date, end_date, state FROM bookings ORDER BY id DESC", db_conn)
    if not all_data.empty:
        st.dataframe(all_data, use_container_width=True, hide_index=True)
    else:
        st.info("ยังไม่มีข้อมูลการจองในฐานข้อมูลของสาขา")
