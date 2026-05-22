import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. CONFIG & UI DESIGN ---
st.set_page_config(page_title="Chem Booking - วท.บ.เคมี", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #fcfdfe !important; }
    
    /* ลายน้ำโมเลกุล Dynamic */
    .molecule-bg {
        position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        z-index: 0; pointer-events: none; overflow: hidden; opacity: 0.12;
    }
    .molecule {
        position: absolute; font-family: 'Courier New', monospace; font-weight: 900;
        color: #1a365d; animation: floatWave 25s infinite alternate ease-in-out;
    }
    @keyframes floatWave {
        0% { transform: translate(0, 0) rotate(0deg); }
        100% { transform: translate(120px, 60px) rotate(360deg); }
    }

    /* กล่องส่วนที่ 1: น้ำเงิน */
    .section-1-container { border-radius: 20px; overflow: hidden; margin-bottom: 30px; box-shadow: 0 8px 25px rgba(30, 58, 138, 0.1); }
    .header-1 { background: #1e3a8a; color: white; padding: 18px 25px; font-weight: bold; font-size: 1.2rem; }
    .body-1 { background: #eff6ff; padding: 30px; }

    /* กล่องส่วนที่ 2: ม่วง */
    .section-2-container { border-radius: 20px; overflow: hidden; margin-bottom: 30px; box-shadow: 0 8px 25px rgba(88, 28, 135, 0.1); }
    .header-2 { background: #581c87; color: white; padding: 18px 25px; font-weight: bold; font-size: 1.2rem; }
    .body-2 { background: #f5f3ff; padding: 30px; }
    
    .block-container { position: relative; z-index: 10; }
    .busy-box { background: #fff3cd; color: #856404; padding: 15px; border-radius: 12px; margin-top: 10px; border-left: 6px solid #ffc107; font-size: 0.95rem; }
</style>

<div class="molecule-bg">
    <div class="molecule" style="top:10%; left:5%; font-size:55px;">H₂O</div>
    <div class="molecule" style="top:45%; left:85%; font-size:75px; animation-delay: -5s;">C₆H₁₂O₆</div>
    <div class="molecule" style="top:75%; left:15%; font-size:60px; animation-delay: -10s;">NaCl</div>
</div>
""", unsafe_allow_html=True)

# --- 2. DATABASE SYSTEM ---
def init_db():
    conn = sqlite3.connect('chem_lab_final_v1.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, status TEXT, phone TEXT, faculty TEXT, supervisor TEXT,
        start_date DATE, end_date DATE, tool_name TEXT, asset_id TEXT, 
        approval_status TEXT DEFAULT 'รออนุมัติ'
    )''')
    conn.commit()
    return conn
db_conn = init_db()

def get_busy_dates(asset_id):
    query = "SELECT start_date, end_date FROM bookings WHERE asset_id = ? AND approval_status != 'ไม่นุมัติ'"
    df = pd.read_sql_query(query, db_conn, params=(asset_id,))
    return [f"📅 {row['start_date']} ถึง {row['end_date']}" for _, row in df.iterrows()]

def is_conflict(asset_id, start, end):
    query = "SELECT id FROM bookings WHERE asset_id = ? AND approval_status != 'ไม่นุมัติ' AND (? <= end_date AND ? >= start_date)"
    res = pd.read_sql_query(query, db_conn, params=(asset_id, str(end), str(start)))
    return not res.empty

# --- 3. APP LAYOUT ---
st.markdown("<h1 style='text-align: center; color: #0f172a;'>ระบบขอใช้เครื่องมือวิทยาศาสตร์</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #475569; margin-bottom: 40px;'>หลักสูตร วท.บ. สาขาวิชาเคมี</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["✍️ ลงทะเบียนจอง", "🔍 ตรวจสอบสถานะ"])

with tab1:
    # --- ส่วนที่ 1: รายละเอียดผู้ขอใช้บริการ ---
    st.markdown('<div class="section-1-container"><div class="header-1">👤 ส่วนที่ 1: รายละเอียดผู้ขอใช้บริการ</div><div class="body-1">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("ชื่อ - นามสกุล", placeholder="กรอกชื่อจริง")
        u_status = st.selectbox("สถานะ", ["นักศึกษา", "อาจารย์", "เจ้าหน้าที่"])
        phone = st.text_input("เบอร์โทรศัพท์ติดต่อ")
    with c2:
        faculty = st.text_input("คณะ/สังกัด", value="วท.บ.เคมี")
        supervisor = st.text_input("อาจารย์ผู้ควบคุม")
        purpose = st.text_input("วัตถุประสงค์การใช้งาน")
    st.markdown('</div></div>', unsafe_allow_html=True)

    # --- ส่วนที่ 2: รายละเอียดเครื่องมือ ---
    st.markdown('<div class="section-2-container"><div class="header-2">🔬 ส่วนที่ 2: รายละเอียดเครื่องมือ และปฏิทินวันว่าง</div><div class="body-2">', unsafe_allow_html=True)
    col_tool, col_id = st.columns([2, 1])
    with col_tool:
        tool_name = st.text_input("ชื่อเครื่องมือวิทยาศาสตร์")
    with col_id:
        asset_id = st.text_input("รหัสครุภัณฑ์", placeholder="เช่น CHEM-001")
    
    if asset_id:
        busy_list = get_busy_dates(asset_id)
        if busy_list:
            st.markdown('<div class="busy-box"><b>⚠️ วันที่เครื่องมือนี้ไม่ว่าง:</b><br>' + '<br>'.join(busy_list) + '</div>', unsafe_allow_html=True)
        else:
            st.success("✅ เครื่องมือว่างทุกช่วงเวลา")

    st.divider()
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        start_date = st.date_input("วันที่เริ่มใช้งาน", min_value=datetime.today())
    with col_d2:
        end_date = st.date_input("วันที่ส่งคืน", min_value=start_date)
    st.markdown('</div></div>', unsafe_allow_html=True)

    if st.button("🚀 ยืนยันคำขอจอง", use_container_width=True, type="primary"):
        if not name or not asset_id:
            st.error("⚠️ กรุณากรอกข้อมูลให้ครบถ้วน")
        elif is_conflict(asset_id, start_date, end_date):
            st.error("❌ ช่วงวันที่เลือกมีการจองอยู่แล้ว โปรดเลือกช่วงเวลาอื่น")
        else:
            cur = db_conn.cursor()
            cur.execute("INSERT INTO bookings (name, status, phone, faculty, supervisor, start_date, end_date, tool_name, asset_id) VALUES (?,?,?,?,?,?,?,?,?)", 
                        (name, u_status, phone, faculty, supervisor, str(start_date), str(end_date), tool_name, asset_id))
            db_conn.commit()
            st.success("🎉 บันทึกคำขอสำเร็จ!")
            st.balloons()

with tab2:
    st.markdown("### 📊 รายการตรวจสอบสถานะการจอง")
    is_admin = st.sidebar.checkbox("โหมดเจ้าหน้าที่ (Admin)")
    df = pd.read_sql_query("SELECT * FROM bookings ORDER BY id DESC", db_conn)
    
    if not df.empty:
        # แก้ไข Error: เปลี่ยนจากการใช้ BadgeColumn เป็นตารางปกติที่รองรับทุกเวอร์ชัน
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        if is_admin:
            st.divider()
            st.subheader("🛠️ การจัดการสำหรับเจ้าหน้าที่")
            target_id = st.number_input("ใส่ ID ที่ต้องการจัดการ", min_value=1, step=1)
            b1, b2 = st.columns(2)
            if b1.button("✅ อนุมัติ"):
                db_conn.cursor().execute("UPDATE bookings SET approval_status = 'อนุมัติแล้ว' WHERE id = ?", (target_id,))
                db_conn.commit()
                st.rerun()
            if b2.button("❌ ไม่นุมัติ"):
                db_conn.cursor().execute("UPDATE bookings SET approval_status = 'ไม่นุมัติ' WHERE id = ?", (target_id,))
                db_conn.commit()
                st.rerun()
    else:
        st.info("ยังไม่มีข้อมูลการจอง")
