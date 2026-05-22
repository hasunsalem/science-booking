import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIG & MODERN UI ---
st.set_page_config(page_title="Science Lab Booking", layout="wide")

# CSS สำหรับลายน้ำโมเลกุลลอยสลับไปมา และการแยก Card ส่วนที่ 1 และ 2
st.markdown("""
<style>
    .stApp { background-color: #f0f4f8 !important; }
    
    /* เลเยอร์ลายน้ำโมเลกุล */
    .molecule-bg {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: 0; pointer-events: none; overflow: hidden; opacity: 0.1;
    }
    .molecule {
        position: absolute; font-family: 'Courier New', monospace; font-weight: 900;
        color: #2c3e50; animation: floatAnim 18s infinite alternate ease-in-out;
    }
    @keyframes floatAnim {
        0% { transform: translate(0, 0) rotate(0deg); }
        100% { transform: translate(100px, 50px) rotate(360deg); }
    }

    /* ตกแต่งส่วนเนื้อหาให้ลอยเหนือลายน้ำ */
    .block-container { position: relative; z-index: 10; }

    /* แยก Card ส่วนที่ 1 และ 2 ให้ชัดเจน */
    .section-card {
        background: rgba(255, 255, 255, 0.98);
        padding: 35px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        margin-bottom: 30px;
        border-left: 8px solid #3498db;
    }
    .section-card-2 {
        background: rgba(255, 255, 255, 0.98);
        padding: 35px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        margin-bottom: 30px;
        border-left: 8px solid #9b59b6;
    }
    h3 { color: #2c3e50; margin-bottom: 20px !important; }
</style>

<div class="molecule-bg">
    <div class="molecule" style="top:15%; left:10%; font-size:50px; animation-delay: 0s;">H₂O</div>
    <div class="molecule" style="top:40%; left:85%; font-size:70px; animation-delay: -4s;">C₆H₁₂O₆</div>
    <div class="molecule" style="top:70%; left:20%; font-size:55px; animation-delay: -8s;">NaCl</div>
    <div class="molecule" style="top:25%; left:65%; font-size:45px; animation-delay: -12s;">NH₃</div>
</div>
""", unsafe_allow_html=True)

# --- 2. DATABASE SYSTEM ---
def init_db():
    conn = sqlite3.connect('lab_booking_v4.db', check_same_thread=False)
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
tabs = st.tabs(["✨ แบบฟอร์มจอง", "📋 ประวัติการจอง"])

with tabs[0]:
    st.markdown("<h1 style='text-align: center; color: #1a3a5f;'>🧪 ระบบจองเครื่องมือวิทยาศาสตร์</h1>", unsafe_allow_html=True)
    
    # ใช้ Session State เพื่อเก็บจำนวนรายการเครื่องมือในส่วนที่ 2
    if 'rows' not in st.session_state:
        st.session_state.rows = 1

    # --- ส่วนที่ 1: ข้อมูลผู้จอง ---
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown("### 👤 ส่วนที่ 1: ข้อมูลผู้ขอใช้บริการ")
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("ชื่อ - นามสกุล", placeholder="กรุณาระบุชื่อจริง")
        u_status = st.selectbox("สถานะ", ["อาจารย์", "เจ้าหน้าที่", "นักศึกษา"])
        phone = st.text_input("เบอร์โทรศัพท์")
    with c2:
        faculty = st.text_input("สังกัด / คณะ")
        supervisor = st.text_input("อาจารย์ผู้ควบคุม")
        location = st.text_input("สถานที่นำไปใช้")
    
    purpose = st.radio("วัตถุประสงค์", ["งานวิจัย", "การเรียนการสอน", "อื่นๆ"], horizontal=True)
    
    d1, d2 = st.columns(2)
    with d1:
        start_date = st.date_input("ตั้งแต่วันที่", min_value=datetime.today())
    with d2:
        end_date = st.date_input("ถึงวันที่", min_value=start_date)
    st.markdown('</div>', unsafe_allow_html=True)

    # --- ส่วนที่ 2: ข้อมูลเครื่องมือ ---
    st.markdown('<div class="section-card-2">', unsafe_allow_html=True)
    st.markdown("### 🔬 ส่วนที่ 2: รายละเอียดเครื่องมือวิทยาศาสตร์")
    
    tools_to_save = []
    for i in range(st.session_state.rows):
        st.markdown(f"**รายการที่ {i+1}**")
        t1, t2 = st.columns([2, 1])
        with t1:
            t_name = st.text_input(f"ชื่อเครื่องมือ", key=f"t_name_{i}")
        with t2:
            a_id = st.text_input(f"รหัสครุภัณฑ์", key=f"a_id_{i}")
        tools_to_save.append({"name": t_name, "id": a_id})
    
    if st.button("➕ เพิ่มรายการเครื่องมือ"):
        st.session_state.rows += 1
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ปุ่มยืนยันการจองทั้งหมด
    if st.button("🚀 ยืนยันการจองเครื่องมือทั้งหมด", use_container_width=True, type="primary"):
        if not name or not tools_to_save[0]['id']:
            st.error("❌ กรุณากรอกข้อมูลผู้จองและรหัสครุภัณฑ์อย่างน้อย 1 รายการ")
        else:
            success = 0
            for item in tools_to_save:
                if item['id']:
                    # ตรวจสอบการจองซ้ำ
                    q = "SELECT name FROM bookings WHERE asset_id = ? AND state = 'Active' AND (? <= end_date AND ? >= start_date)"
                    overlap = pd.read_sql_query(q, db_conn, params=(item['id'], str(end_date), str(start_date)))
                    
                    if not overlap.empty:
                        st.error(f"⚠️ {item['name']} ({item['id']}) ถูกจองแล้วโดยคุณ {overlap.iloc[0]['name']}")
                    else:
                        c = db_conn.cursor()
                        c.execute('''INSERT INTO bookings 
                            (name, status, phone, faculty, supervisor, purpose, location, start_date, end_date, tool_name, asset_id)
                            VALUES (?,?,?,?,?,?,?,?,?,?,?)''', 
                            (name, u_status, phone, faculty, supervisor, purpose, location, str(start_date), str(end_date), item['name'], item['id']))
                        db_conn.commit()
                        success += 1
            if success > 0:
                st.success(f"✅ บันทึกการจองสำเร็จ {success} รายการ!")
                st.balloons()

with tabs[1]:
    st.markdown("### 📊 ประวัติการจองทั้งหมด")
    data = pd.read_sql_query("SELECT * FROM bookings ORDER BY id DESC", db_conn)
    if not data.empty:
        st.dataframe(data, use_container_width=True, hide_index=True)
    else:
        st.info("ยังไม่มีข้อมูลการจองในระบบ")
