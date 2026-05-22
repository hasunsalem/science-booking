import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIG & UI DESIGN ---
st.set_page_config(page_title="Science Lab Booking", layout="wide")

# ปรับปรุง CSS ใหม่เพื่อให้ลายน้ำแสดงผลแน่นอน
st.markdown("""
<style>
    /* ตั้งค่าพื้นหลังแอป */
    .stApp {
        background-color: #f4f7f6 !important;
    }

    /* สร้างเลเยอร์ลายน้ำโมเลกุล */
    .watermark-wrapper {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: 0; /* อยู่หลังเนื้อหาแต่หน้าพื้นหลัง */
        pointer-events: none;
        overflow: hidden;
    }

    .molecule {
        position: absolute;
        font-family: 'monospace';
        font-weight: 900;
        color: #2c3e50;
        opacity: 0.12; /* เพิ่มความเข้มเล็กน้อยเพื่อให้เห็นชัดขึ้น */
        animation: floatAnim 12s infinite alternate ease-in-out;
    }

    @keyframes floatAnim {
        0% { transform: translate(0, 0) rotate(0deg); opacity: 0.08; }
        50% { opacity: 0.15; }
        100% { transform: translate(60px, 40px) rotate(20deg); opacity: 0.08; }
    }

    /* ตกแต่งเนื้อหาให้อยู่บนเลเยอร์ลายน้ำ */
    .block-container {
        position: relative;
        z-index: 10;
    }

    /* ดีไซน์ Card */
    div[data-testid="stForm"] {
        background: rgba(255, 255, 255, 0.95);
        padding: 40px;
        border-radius: 24px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.07);
        border: 1px solid rgba(255,255,255,0.3);
    }
</style>

<div class="watermark-wrapper">
    <div class="molecule" style="top:10%; left:5%; font-size:60px; animation-delay: 0s;">H₂O</div>
    <div class="molecule" style="top:35%; left:80%; font-size:80px; animation-delay: -3s;">C₆H₁₂O₆</div>
    <div class="molecule" style="top:65%; left:15%; font-size:55px; animation-delay: -6s;">NaCl</div>
    <div class="molecule" style="top:80%; left:65%; font-size:70px; animation-delay: -9s;">CO₂</div>
    <div class="molecule" style="top:20%; left:55%; font-size:45px; animation-delay: -12s;">NH₃</div>
    <div class="molecule" style="top:50%; left:40%; font-size:35px; animation-delay: -4s;">CH₄</div>
</div>
""", unsafe_allow_html=True)

# --- 2. DATABASE SYSTEM ---
def init_db():
    conn = sqlite3.connect('science_lab_v3.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, status TEXT, phone TEXT, faculty TEXT, 
        purpose TEXT, start_date DATE, end_date DATE, 
        tool_name TEXT, asset_id TEXT, state TEXT DEFAULT 'Active'
    )''')
    conn.commit()
    return conn

db_conn = init_db()

# --- 3. MAIN APP INTERFACE ---
tabs = st.tabs(["✨ จองเครื่องมือใหม่", "📋 ตารางการใช้งาน"])

with tabs[0]:
    st.markdown("<h1 style='color: #1a3a5f;'>🧪 จองเครื่องมือวิทยาศาสตร์</h1>", unsafe_allow_html=True)
    
    with st.form("booking_form", clear_on_submit=True):
        st.subheader("👤 ส่วนที่ 1: รายละเอียดผู้จอง")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("ชื่อ - นามสกุล")
            u_status = st.selectbox("สถานะ", ["อาจารย์", "เจ้าหน้าที่", "นักศึกษา"])
        with col2:
            phone = st.text_input("เบอร์โทรศัพท์")
            faculty = st.text_input("คณะ/สังกัด")

        purpose = st.radio("วัตถุประสงค์", ["งานวิจัย", "การเรียนการสอน", "อื่นๆ"], horizontal=True)
        
        c3, c4 = st.columns(2)
        with c3:
            start_date = st.date_input("เริ่มวันที่", min_value=datetime.today())
        with c4:
            end_date = st.date_input("ถึงวันที่", min_value=start_date)

        st.divider()
        
        # ส่วนที่ 2: เพิ่มรายการ (แบบ UI ทันสมัย)
        st.subheader("🔬 ส่วนที่ 2: ข้อมูลเครื่องมือ")
        
        # สร้างช่องกรอกข้อมูล 3 แถวเผื่อไว้เลย (ตามที่คุณต้องการเพิ่มรายการ)
        tool_list = []
        for i in range(3):
            t_col1, t_col2 = st.columns([2, 1])
            with t_col1:
                t_n = st.text_input(f"ชื่อเครื่องมือ {i+1}", key=f"tn_{i}")
            with t_col2:
                a_i = st.text_input(f"รหัสครุภัณฑ์ {i+1}", key=f"ai_{i}")
            if t_n and a_i:
                tool_list.append((t_n, a_i))

        if st.form_submit_button("🚀 ยืนยันการจองทั้งหมด", use_container_width=True):
            if not name or not tool_list:
                st.error("กรุณากรอกชื่อผู้จองและรายละเอียดเครื่องมืออย่างน้อย 1 รายการ")
            else:
                for t_name, asset_id in tool_list:
                    # เช็คซ้ำ
                    q = "SELECT name FROM bookings WHERE asset_id = ? AND state = 'Active' AND (? <= end_date AND ? >= start_date)"
                    overlap = pd.read_sql_query(q, db_conn, params=(asset_id, str(end_date), str(start_date)))
                    
                    if not overlap.empty:
                        st.error(f"❌ {t_name} ({asset_id}) ถูกจองแล้วโดยคุณ {overlap.iloc[0]['name']}")
                    else:
                        c = db_conn.cursor()
                        c.execute('''INSERT INTO bookings 
                            (name, status, phone, faculty, purpose, start_date, end_date, tool_name, asset_id)
                            VALUES (?,?,?,?,?,?,?,?,?)''', 
                            (name, u_status, phone, faculty, purpose, str(start_date), str(end_date), t_name, asset_id))
                        db_conn.commit()
                st.success("✅ บันทึกการจองสำเร็จ!")
                st.balloons()

with tabs[1]:
    st.title("📋 รายการประวัติการจอง")
    data = pd.read_sql_query("SELECT * FROM bookings ORDER BY id DESC", db_conn)
    if not data.empty:
        st.dataframe(data, use_container_width=True, hide_index=True)
    else:
        st.info("ยังไม่มีข้อมูลในระบบ")
