import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# --- 1. CONFIG & UI DESIGN ---
st.set_page_config(page_title="Chem Booking - ปฏิทินอัจฉริยะ", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #fcfdfe !important; }
    .molecule-bg { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 0; pointer-events: none; opacity: 0.1; overflow: hidden; }
    .molecule { position: absolute; font-family: 'Courier New', monospace; font-weight: 900; color: #1a365d; animation: floatWave 25s infinite alternate ease-in-out; }
    @keyframes floatWave { 0% { transform: translate(0, 0) rotate(0deg); } 100% { transform: translate(100px, 50px) rotate(360deg); } }
    
    /* สไตล์กล่อง Integrated Box แบบที่คุณชอบ */
    .section-container { border-radius: 20px; overflow: hidden; margin-bottom: 30px; box-shadow: 0 8px 25px rgba(0,0,0,0.08); }
    .header-blue { background: #1e3a8a; color: white; padding: 15px 25px; font-weight: bold; }
    .body-blue { background: #eff6ff; padding: 25px; }
    .header-purple { background: #581c87; color: white; padding: 15px 25px; font-weight: bold; }
    .body-purple { background: #f5f3ff; padding: 25px; }
    
    .block-container { position: relative; z-index: 10; }
    .avail-info { background: #fff3cd; color: #856404; padding: 10px; border-radius: 10px; margin-bottom: 15px; border-left: 5px solid #ffeeba; }
</style>

<div class="molecule-bg">
    <div class="molecule" style="top:10%; left:8%; font-size:55px;">H₂O</div>
    <div class="molecule" style="top:45%; left:82%; font-size:75px; animation-delay: -5s;">C₆H₁₂O₆</div>
    <div class="molecule" style="top:75%; left:18%; font-size:60px; animation-delay: -10s;">NaCl</div>
</div>
""", unsafe_allow_html=True)

# --- 2. DATABASE SYSTEM ---
def init_db():
    conn = sqlite3.connect('chem_lab_v9.db', check_same_thread=False)
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

# ฟังก์ชันดึงช่วงที่ไม่ว่างของเครื่องมือ
def get_unavailable_dates(asset_id):
    query = "SELECT start_date, end_date FROM bookings WHERE asset_id = ? AND approval_status != 'ไม่นุมัติ'"
    df_dates = pd.read_sql_query(query, db_conn, params=(asset_id,))
    unavailable_ranges = []
    for _, row in df_dates.iterrows():
        unavailable_ranges.append(f"📅 {row['start_date']} ถึง {row['end_date']}")
    return unavailable_ranges

# ฟังก์ชันเช็คการทับซ้อน (Logic เดิมแต่เข้มงวดขึ้น)
def is_date_conflict(asset_id, start, end):
    q = "SELECT id FROM bookings WHERE asset_id = ? AND approval_status != 'ไม่นุมัติ' AND (? <= end_date AND ? >= start_date)"
    res = pd.read_sql_query(q, db_conn, params=(asset_id, str(end), str(start)))
    return not res.empty

# --- 3. UI LAYOUT ---
st.markdown("<h1 style='text-align: center;'>ระบบขอใช้เครื่องมือวิทยาศาสตร์</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>หลักสูตร วท.บ. สาขาวิชาเคมี</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📝 แบบฟอร์มการจอง", "📋 ตรวจสอบสถานะ"])

with tab1:
    # --- ส่วนที่ 2: รายละเอียดเครื่องมือ (เอาขึ้นก่อนเพื่อให้เช็ควันได้เลย) ---
    st.markdown('<div class="section-container"><div class="header-purple">🔬 ส่วนที่ 2: รายละเอียดเครื่องมือ และ ตรวจสอบปฏิทินว่าง</div><div class="body-purple">', unsafe_allow_html=True)
    
    col_t1, col_t2 = st.columns([2, 1])
    with col_t2:
        asset_id_input = st.text_input("ระบุรหัสครุภัณฑ์เพื่อเช็ควันว่าง", placeholder="เช่น CHEM-001")
    with col_t1:
        tool_name_input = st.text_input("ชื่อเครื่องมือวิทยาศาสตร์")

    # บล็อกแสดงวันที่ไม่ว่าง
    if asset_id_input:
        busy_dates = get_unavailable_dates(asset_id_input)
        if busy_dates:
            st.markdown('<div class="avail-info"><b>⚠️ ช่วงเวลาที่ไม่สามารถเลือกได้:</b><br>' + '<br>'.join(busy_dates) + '</div>', unsafe_allow_html=True)
        else:
            st.success("✅ เครื่องมือนี้ว่างทุกช่วงเวลา สามารถเลือกวันได้ตามสะดวก")
    
    st.markdown('</div></div>', unsafe_allow_html=True)

    # --- ส่วนที่ 1: รายละเอียดผู้จอง และ วันที่ ---
    st.markdown('<div class="section-container"><div class="header-blue">👤 ส่วนที่ 1: รายละเอียดผู้ขอใช้ และ วันที่ต้องการจอง</div><div class="body-blue">', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("ชื่อ - นามสกุล")
        u_status = st.selectbox("สถานะ", ["นักศึกษา", "อาจารย์", "เจ้าหน้าที่"])
        phone = st.text_input("เบอร์โทรศัพท์")
    with c2:
        faculty = st.text_input("คณะ/สาขาวิชา", value="วท.บ.เคมี")
        supervisor = st.text_input("อาจารย์ผู้ควบคุม")
        
    st.divider()
    d1, d2 = st.columns(2)
    with d1:
        start_date = st.date_input("เลือกวันที่เริ่มใช้", min_value=datetime.today())
    with d2:
        end_date = st.date_input("เลือกวันที่คืน", min_value=start_date)
        
    st.markdown('</div></div>', unsafe_allow_html=True)

    # ปุ่มส่งข้อมูล
    if st.button("🚀 ตรวจสอบและยืนยันการจอง", use_container_width=True, type="primary"):
        if not name or not asset_id_input:
            st.error("⚠️ กรุณากรอกข้อมูลให้ครบถ้วน")
        elif is_date_conflict(asset_id_input, start_date, end_date):
            st.error(f"❌ ไม่สามารถจองได้: ช่วงวันที่คุณเลือกมีการจองอยู่แล้ว โปรดตรวจสอบปฏิทินอีกครั้ง")
        else:
            cur = db_conn.cursor()
            cur.execute("INSERT INTO bookings (name, status, phone, faculty, supervisor, start_date, end_date, tool_name, asset_id) VALUES (?,?,?,?,?,?,?,?,?)", 
                        (name, u_status, phone, faculty, supervisor, str(start_date), str(end_date), tool_name_input, asset_id_input))
            db_conn.commit()
            st.success("🎉 บันทึกคำขอจองเรียบร้อย! โปรดรอเจ้าหน้าที่พิจารณาอนุมัติ")
            st.balloons()

with tab2:
    # --- ส่วนจัดการสถานะ (เหมือนเดิมแต่เพิ่มการกรอง) ---
    st.markdown("### 📊 ตารางสถานะการจอง วท.บ.เคมี")
    
    is_admin = st.sidebar.checkbox("โหมดเจ้าหน้าที่")
    df = pd.read_sql_query("SELECT * FROM bookings ORDER BY id DESC", db_conn)
    
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True, column_config={
            "approval_status": st.column_config.BadgeColumn("สถานะ", 
                map={"รออนุมัติ": "🟡 รออนุมัติ", "อนุมัติแล้ว": "🟢 อนุมัติแล้ว", "ไม่นุมัติ": "🔴 ไม่นุมัติ"})
        })
        
        if is_admin:
            st.divider()
            target_id = st.number_input("จัดการ ID รายการ:", min_value=1, step=1)
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
